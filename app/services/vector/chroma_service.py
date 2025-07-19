from typing import Dict, List, Optional, Any

import chromadb
from chromadb.config import Settings
# These imports may show as unresolved in the IDE but they do exist at runtime
from langchain_huggingface.embeddings import HuggingFaceEmbeddings  # type: ignore
from langchain_chroma import Chroma  # type: ignore

from app.core.config import settings
from app.utils.audit_logger import audit_logger


class ChromaService:
    """
    Service for interacting with ChromaDB vector database.
    """

    def __init__(self):
        """Initialize the ChromaDB service"""
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.langchain_chroma = None
        
    async def initialize(self, persist_directory=None, collection_name=None):
        """Initialize the ChromaDB service"""
        # Use provided values or defaults from settings
        persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Initialize the embedding model using HuggingFaceEmbeddings
        self.embedding_model = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
        
        # Initialize LangChain's Chroma wrapper
        self.langchain_chroma = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=persist_directory
        )
        
        audit_logger.log(
            action="chroma_service_initialized",
            resource_type="chroma",
            status="success"
        )
    
    async def upsert_document(self, 
                           document_id: str, 
                           content: str, 
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Upsert a document into the vector store.
        
        Args:
            document_id: Unique ID for the document
            content: Text content to be embedded
            metadata: Optional metadata to store alongside the embedding
            
        Returns:
            The document ID
        """
        if metadata is None:
            metadata = {}
            
        try:
            # Generate embedding
            embedding = self.embedding_model.embed_documents([content])[0]
            
            # Prepare metadata with content
            document_metadata = {
                "content": content,
                **metadata
            }
            
            # Upsert to ChromaDB
            self.collection.upsert(
                ids=[document_id],
                embeddings=[embedding],
                metadatas=[document_metadata],
                documents=[content]
            )
            
            audit_logger.log(
                action="document_upserted",
                resource_type="chroma_document",
                resource_id=document_id,
                status="success",
                details={"metadata_keys": list(metadata.keys())}
            )
            
            return document_id
            
        except Exception as e:
            audit_logger.log(
                action="document_upserted",
                resource_type="chroma_document",
                resource_id=document_id,
                status="failure",
                details={"error": str(e)}
            )
            raise
    
    async def upsert_documents(self, 
                            documents: List[Dict[str, Any]]) -> List[str]:
        """
        Upsert multiple documents into the vector store.
        
        Args:
            documents: List of documents, each with id, content, and optional metadata
            
        Returns:
            List of document IDs
        """
        try:
            ids = []
            contents = []
            metadatas = []
            
            # Process each document
            for doc in documents:
                document_id = doc.get("id")
                content = doc.get("content")
                metadata = doc.get("metadata", {})
                
                ids.append(document_id)
                contents.append(content)
                metadatas.append({
                    "content": content,
                    **metadata
                })
            
            # Generate embeddings
            embeddings = self.embedding_model.embed_documents(contents)
            
            # Batch upsert to ChromaDB
            if ids:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=contents
                )
            
            document_ids = [doc.get("id") for doc in documents]
            
            audit_logger.log(
                action="documents_batch_upserted",
                resource_type="chroma_documents",
                status="success",
                details={"document_count": len(documents)}
            )
            
            return document_ids
            
        except Exception as e:
            audit_logger.log(
                action="documents_batch_upserted",
                resource_type="chroma_documents",
                status="failure",
                details={"error": str(e), "document_count": len(documents)}
            )
            raise
    
    async def query_similar(self, 
                         query_text: str, 
                         top_k: int = 5, 
                         filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query for documents similar to the query text.
        
        Args:
            query_text: Query text to find similar documents for
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of similar documents with their similarity scores and metadata
        """
        try:
            # Generate query embedding
            embedding = self.embedding_model.embed_documents([query_text])[0]
            
            # Prepare filter for ChromaDB (format is different from Pinecone)
            where_filter = None
            if filter_dict:
                where_filter = filter_dict  # ChromaDB has its own filtering format
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else 0
                
                # Convert distance to score (ChromaDB returns distance, so 1-distance for similarity score)
                score = 1.0 - distance if distance <= 1.0 else 0.0
                
                formatted_results.append({
                    "id": doc_id,
                    "score": score,
                    "content": metadata.get("content", ""),
                    "metadata": {k: v for k, v in metadata.items() if k != "content"}
                })
            
            audit_logger.log(
                action="chroma_query",
                resource_type="chroma",
                status="success",
                details={"query": query_text[:100] + "..." if len(query_text) > 100 else query_text,
                        "results_count": len(formatted_results)}
            )
            
            return formatted_results
            
        except Exception as e:
            audit_logger.log(
                action="chroma_query",
                resource_type="chroma",
                status="failure",
                details={"error": str(e), "query": query_text[:100] + "..." if len(query_text) > 100 else query_text}
            )
            raise
    
    async def query_by_embedding(self, 
                             embedding: List[float], 
                             top_k: int = 5, 
                             filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query for documents similar to the provided embedding.
        
        Args:
            embedding: Vector embedding to query with
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of similar documents with their similarity scores and metadata
        """
        try:
            # Prepare filter for ChromaDB
            where_filter = None
            if filter_dict:
                where_filter = filter_dict
            
            # Query ChromaDB with provided embedding
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else 0
                
                # Convert distance to score
                score = 1.0 - distance if distance <= 1.0 else 0.0
                
                formatted_results.append({
                    "id": doc_id,
                    "score": score,
                    "content": metadata.get("content", ""),
                    "metadata": {k: v for k, v in metadata.items() if k != "content"}
                })
            
            audit_logger.log(
                action="chroma_query_by_embedding",
                resource_type="chroma",
                status="success",
                details={"results_count": len(formatted_results)}
            )
            
            return formatted_results
            
        except Exception as e:
            audit_logger.log(
                action="chroma_query_by_embedding",
                resource_type="chroma",
                status="failure",
                details={"error": str(e)}
            )
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[document_id])
            
            audit_logger.log(
                action="document_deleted",
                resource_type="chroma_document",
                resource_id=document_id,
                status="success"
            )
            
            return True
            
        except Exception as e:
            audit_logger.log(
                action="document_deleted",
                resource_type="chroma_document",
                resource_id=document_id,
                status="failure",
                details={"error": str(e)}
            )
            raise


# Create singleton instance
chroma_service = ChromaService()
