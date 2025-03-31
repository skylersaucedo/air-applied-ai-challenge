from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import Settings

settings = Settings()


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_CLUSTER, port=settings.QDRANT_PORT
        )

    async def create_collection(self, collection_name: str, vector_size: int) -> None:
        """Create a new collection in Qdrant."""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        except Exception as e:
            raise QdrantException(f"Failed to create collection: {str(e)}")

    async def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from Qdrant."""
        try:
            self.client.delete_collection(collection_name=collection_name)
        except Exception as e:
            raise QdrantException(f"Failed to delete collection: {str(e)}")

    async def upsert_points(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payload: Optional[List[dict]] = None,
    ) -> None:
        """Insert or update points in a collection."""
        try:
            self.client.upsert(
                collection_name=collection_name, points=vectors, payload=payload
            )
        except Exception as e:
            raise QdrantException(f"Failed to upsert points: {str(e)}")

    async def search_points(
        self, collection_name: str, query_vector: List[float], limit: int = 10
    ) -> List[dict]:
        """Search for similar vectors in a collection."""
        try:
            results = self.client.search(
                collection_name=collection_name, query_vector=query_vector, limit=limit
            )
            return [
                {"id": hit.id, "score": hit.score, "payload": hit.payload}
                for hit in results
            ]
        except Exception as e:
            raise QdrantException(f"Failed to search points: {str(e)}")

    async def delete_points(self, collection_name: str, points_selector: dict) -> None:
        """Delete points from a collection based on a selector."""
        try:
            self.client.delete(
                collection_name=collection_name, points_selector=points_selector
            )
        except Exception as e:
            raise QdrantException(f"Failed to delete points: {str(e)}")

    async def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a collection."""
        try:
            return self.client.get_collection(collection_name=collection_name)
        except Exception as e:
            raise QdrantException(f"Failed to get collection info: {str(e)}")


class QdrantException(Exception):
    """Custom exception for Qdrant-related errors."""

    pass
