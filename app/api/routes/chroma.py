# Test ChromaDB with a simple document
import json
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from app.services.vector.chroma_service import chroma_service
from app.utils.audit_logger import audit_logger

router = APIRouter()

class ChromaTestDocument(BaseModel):
    """Test document for ChromaDB"""
    document_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    
class ChromaSearchQuery(BaseModel):
    """Search query for ChromaDB"""
    query_text: str
    limit: int = 5

@router.post("/test/add-document", status_code=status.HTTP_201_CREATED)
async def add_test_document(document: ChromaTestDocument):
    """Add a test document to ChromaDB"""
    try:
        document_id = await chroma_service.upsert_document(
            document_id=document.document_id,
            content=document.content,
            metadata=document.metadata
        )
        
        return {
            "status": "success",
            "document_id": document_id,
            "message": "Document added to ChromaDB"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add document: {str(e)}"
        )

@router.post("/test/search", status_code=status.HTTP_200_OK)
async def search_documents(query: ChromaSearchQuery):
    """Search for documents in ChromaDB"""
    try:
        results = await chroma_service.query_similar(
            query_text=query.query_text,
            top_k=query.limit
        )
        
        return {
            "status": "success",
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search documents: {str(e)}"
        )
