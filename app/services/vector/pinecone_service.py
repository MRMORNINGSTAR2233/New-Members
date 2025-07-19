from typing import Dict, List, Optional, Any, Union, Tuple

import pinecone
from langchain.embeddings import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone

from app.core.config import settings
from app.utils.audit_logger import audit_logger


class PineconeService:
    """
    Service for interacting with Pinecone vector database.
    """

    def __init__(self):
        """Initialize the Pinecone service with API credentials"""
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        # Create the index if it doesn't exist
        if settings.PINECONE_INDEX_NAME not in pinecone.list_indexes():
            pinecone.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=768,  # Default dimension for Gemini embeddings
                metric="cosine"
            )
        
        # Connect to the index
        self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
        
        # Initialize the embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            task_type="RETRIEVAL_DOCUMENT"  # Optimized for document retrieval
        )
        
        # Initialize LangChain's Pinecone wrapper
        self.langchain_pinecone = LangchainPinecone(
            index=self.index,
            embedding=self.embeddings,
            text_key="content"
        )
        
        audit_logger.log(
            action="pinecone_service_initialized",
            resource_type="pinecone",
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
            embedding = self.embeddings.embed_query(content)
            
            # Prepare record
            record = {
                "id": document_id,
                "values": embedding,
                "metadata": {
                    "content": content,
                    **metadata
                }
            }
            
            # Upsert to Pinecone
            self.index.upsert(vectors=[record])
            
            audit_logger.log(
                action="document_upserted",
                resource_type="pinecone_document",
                resource_id=document_id,
                status="success",
                details={"metadata_keys": list(metadata.keys())}
            )
            
            return document_id
            
        except Exception as e:
            audit_logger.log(
                action="document_upserted",
                resource_type="pinecone_document",
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
            records = []
            
            # Process each document
            for doc in documents:
                document_id = doc.get("id")
                content = doc.get("content")
                metadata = doc.get("metadata", {})
                
                # Generate embedding
                embedding = self.embeddings.embed_query(content)
                
                # Prepare record
                record = {
                    "id": document_id,
                    "values": embedding,
                    "metadata": {
                        "content": content,
                        **metadata
                    }
                }
                
                records.append(record)
            
            # Batch upsert to Pinecone
            if records:
                self.index.upsert(vectors=records)
            
            document_ids = [doc.get("id") for doc in documents]
            
            audit_logger.log(
                action="documents_batch_upserted",
                resource_type="pinecone_documents",
                status="success",
                details={"document_count": len(documents)}
            )
            
            return document_ids
            
        except Exception as e:
            audit_logger.log(
                action="documents_batch_upserted",
                resource_type="pinecone_documents",
                status="failure",
                details={"error": str(e), "document_count": len(documents)}
            )
            raise
    
    async def query_similar(self, 
                         query_text: str, 
                         top_k: int = 5, 
                         filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query for documents similar to the query text.
        
        Args:
            query_text: Query text to find similar documents for
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar documents with their similarity scores and metadata
        """
        try:
            # Generate query embedding
            embedding = self.embeddings.embed_query(query_text)
            
            # Query Pinecone
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "content": match.metadata.get("content", ""),
                    "metadata": {k: v for k, v in match.metadata.items() if k != "content"}
                })
            
            audit_logger.log(
                action="pinecone_query",
                resource_type="pinecone",
                status="success",
                details={"query": query_text[:100] + "..." if len(query_text) > 100 else query_text,
                        "results_count": len(formatted_results)}
            )
            
            return formatted_results
            
        except Exception as e:
            audit_logger.log(
                action="pinecone_query",
                resource_type="pinecone",
                status="failure",
                details={"error": str(e), "query": query_text[:100] + "..." if len(query_text) > 100 else query_text}
            )
            raise
    
    async def query_by_embedding(self, 
                             embedding: List[float], 
                             top_k: int = 5, 
                             filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query for documents similar to the provided embedding.
        
        Args:
            embedding: Vector embedding to query with
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar documents with their similarity scores and metadata
        """
        try:
            # Query Pinecone with provided embedding
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "content": match.metadata.get("content", ""),
                    "metadata": {k: v for k, v in match.metadata.items() if k != "content"}
                })
            
            audit_logger.log(
                action="pinecone_query_by_embedding",
                resource_type="pinecone",
                status="success",
                details={"results_count": len(formatted_results)}
            )
            
            return formatted_results
            
        except Exception as e:
            audit_logger.log(
                action="pinecone_query_by_embedding",
                resource_type="pinecone",
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
            self.index.delete(ids=[document_id])
            
            audit_logger.log(
                action="document_deleted",
                resource_type="pinecone_document",
                resource_id=document_id,
                status="success"
            )
            
            return True
            
        except Exception as e:
            audit_logger.log(
                action="document_deleted",
                resource_type="pinecone_document",
                resource_id=document_id,
                status="failure",
                details={"error": str(e)}
            )
            raise


# Create singleton instance
pinecone_service = PineconeService()
