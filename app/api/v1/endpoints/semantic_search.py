from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog
from app.services.semantic_search_service import SemanticSearchService
from app.core.exceptions import APIException

router = APIRouter()
logger = structlog.get_logger()
semantic_search_service = SemanticSearchService()

class SearchQuery(BaseModel):
    """Semantic search query model"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 10
    score_threshold: Optional[float] = 0.7

class SearchResult(BaseModel):
    """Search result model"""
    id: str
    score: float
    content: Dict[str, Any]
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    """Search response model"""
    results: List[SearchResult]
    total_results: int
    processing_time: float

class BatchSearchRequest(BaseModel):
    """Batch search request model"""
    queries: List[SearchQuery]
    batch_size: Optional[int] = 10

class BatchSearchResponse(BaseModel):
    """Batch search response model"""
    results: List[SearchResponse]
    total_queries: int
    total_processing_time: float

@router.post("/search", response_model=SearchResponse)
async def semantic_search(
    query: SearchQuery,
    collection: Optional[str] = Query(None, description="Collection to search in")
):
    """
    Perform semantic search across documents
    """
    try:
        # Process the search query
        result = await semantic_search_service.search(
            query=query.query,
            filters=query.filters,
            top_k=query.top_k,
            score_threshold=query.score_threshold,
            collection=collection
        )
        
        return SearchResponse(
            results=result["results"],
            total_results=result["total_results"],
            processing_time=result["processing_time"]
        )
        
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Semantic search failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch", response_model=BatchSearchResponse)
async def batch_semantic_search(
    request: BatchSearchRequest,
    collection: Optional[str] = Query(None, description="Collection to search in")
):
    """
    Perform semantic search across multiple queries in batch
    """
    try:
        results = []
        total_time = 0
        
        for query in request.queries:
            result = await semantic_search_service.search(
                query=query.query,
                filters=query.filters,
                top_k=query.top_k,
                score_threshold=query.score_threshold,
                collection=collection
            )
            results.append(SearchResponse(**result))
            total_time += result["processing_time"]
            
        return BatchSearchResponse(
            results=results,
            total_queries=len(request.queries),
            total_processing_time=total_time
        )
        
    except Exception as e:
        logger.error("Batch semantic search failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/index", response_model=Dict[str, Any])
async def index_document(
    document: Dict[str, Any],
    collection: Optional[str] = Query(None, description="Collection to index in")
):
    """
    Index a document for semantic search
    """
    try:
        result = await semantic_search_service.index_document(
            document=document,
            collection=collection
        )
        return result
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Document indexing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch-index", response_model=List[Dict[str, Any]])
async def batch_index_documents(
    documents: List[Dict[str, Any]],
    collection: Optional[str] = Query(None, description="Collection to index in")
):
    """
    Index multiple documents in batch
    """
    try:
        results = []
        for document in documents:
            result = await semantic_search_service.index_document(
                document=document,
                collection=collection
            )
            results.append(result)
        return results
    except Exception as e:
        logger.error("Batch document indexing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") 