from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import numpy as np
from app.core.config import settings
import structlog

logger = structlog.get_logger()

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_CLUSTER,
            port=settings.QDRANT_PORT
        )
        self.collection_name = "air_assets"
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't"""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # OpenAI embedding size
                    distance=Distance.COSINE
                )
            )
            logger.info("Created new Qdrant collection", collection=self.collection_name)
    
    async def upsert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Upsert vectors with their payloads into the collection
        
        Args:
            vectors: List of vector embeddings
            payloads: List of metadata payloads
            ids: Optional list of IDs for the vectors
        """
        try:
            points = []
            for i, (vector, payload) in enumerate(zip(vectors, payloads)):
                point_id = ids[i] if ids else i
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(
                "Successfully upserted vectors",
                count=len(vectors),
                collection=self.collection_name
            )
        except Exception as e:
            logger.error(
                "Failed to upsert vectors",
                error=str(e),
                collection=self.collection_name
            )
            raise
    
    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        offset: int = 0,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection
        
        Args:
            query_vector: The query vector to search with
            limit: Maximum number of results to return
            offset: Number of results to skip
            filter: Optional filter conditions for the search
            
        Returns:
            List of search results with scores and payloads
        """
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                offset=offset,
                query_filter=models.Filter(**filter) if filter else None
            )
            
            results = [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in search_result
            ]
            
            logger.info(
                "Successfully performed vector search",
                query_size=len(query_vector),
                results_count=len(results)
            )
            return results
        except Exception as e:
            logger.error(
                "Failed to perform vector search",
                error=str(e),
                collection=self.collection_name
            )
            raise
    
    async def delete_vectors(self, ids: List[str]) -> None:
        """
        Delete vectors by their IDs
        
        Args:
            ids: List of vector IDs to delete
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=ids
                )
            )
            logger.info(
                "Successfully deleted vectors",
                count=len(ids),
                collection=self.collection_name
            )
        except Exception as e:
            logger.error(
                "Failed to delete vectors",
                error=str(e),
                collection=self.collection_name
            )
            raise
    
    async def batch_operations(
        self,
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform batch operations on vectors
        
        Args:
            operations: List of operations to perform
                Each operation should be a dict with:
                - type: "upsert" or "delete"
                - vectors: List of vectors (for upsert)
                - payloads: List of payloads (for upsert)
                - ids: List of IDs (for delete)
                
        Returns:
            Dict containing operation results
        """
        results = []
        for operation in operations:
            try:
                if operation["type"] == "upsert":
                    await self.upsert_vectors(
                        vectors=operation["vectors"],
                        payloads=operation["payloads"]
                    )
                    results.append({"type": "upsert", "status": "success"})
                elif operation["type"] == "delete":
                    await self.delete_vectors(ids=operation["ids"])
                    results.append({"type": "delete", "status": "success"})
                else:
                    results.append({
                        "type": operation["type"],
                        "status": "error",
                        "message": "Invalid operation type"
                    })
            except Exception as e:
                results.append({
                    "type": operation["type"],
                    "status": "error",
                    "message": str(e)
                })
        
        return {"results": results} 