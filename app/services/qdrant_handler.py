import base64
import io
import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams
from transformers import AutoModel, AutoTokenizer

logger = logging.getLogger(__name__)


class QdrantHandler:
    """Handler for multimodal data vectorization and storage in Qdrant"""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=qdrant_url)
        self._initialize_models()
        self._create_collections()

    def _initialize_models(self):
        """Initialize all required models"""
        # Text embedding model
        self.text_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.text_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    def _create_collections(self):
        """Create collections for each data type if they don't exist"""
        collections = {
            "text": VectorParams(size=384, distance=Distance.COSINE),
            "image": VectorParams(size=384, distance=Distance.COSINE),
            "audio": VectorParams(size=384, distance=Distance.COSINE),
            "video": VectorParams(size=384, distance=Distance.COSINE),
        }

        for collection_name, params in collections.items():
            try:
                self.client.create_collection(
                    collection_name=collection_name, vectors_config=params
                )
                logger.info(f"Created collection: {collection_name}")
            except Exception as e:
                logger.warning(
                    f"Collection {collection_name} may already exist: {str(e)}"
                )

    async def vectorize_text(self, text: str) -> List[float]:
        """Vectorize text using the model"""
        try:
            inputs = self.text_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            outputs = self.text_model(**inputs)
            return outputs.last_hidden_state.mean(dim=1).detach().numpy().tolist()[0]
        except Exception as e:
            logger.error(f"Error vectorizing text: {str(e)}")
            raise

    async def vectorize_image(
        self, image_data: Union[str, bytes], description: Optional[str] = None
    ) -> List[float]:
        """Vectorize image"""
        try:
            # For testing, return a simple vector
            return [0.1] * 384
        except Exception as e:
            logger.error(f"Error vectorizing image: {str(e)}")
            raise

    async def vectorize_audio(self, audio_data: Union[str, bytes]) -> List[float]:
        """Vectorize audio"""
        try:
            # For testing, return a simple vector
            return [0.1] * 384
        except Exception as e:
            logger.error(f"Error vectorizing audio: {str(e)}")
            raise

    async def vectorize_video(self, video_data: Union[str, bytes]) -> List[float]:
        """Vectorize video"""
        try:
            # For testing, return a simple vector
            return [0.1] * 384
        except Exception as e:
            logger.error(f"Error vectorizing video: {str(e)}")
            raise

    async def upsert_data(
        self,
        collection_name: str,
        data: Dict[str, Any],
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Upsert data into Qdrant collection"""
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=data.get("id", str(hash(str(data)))),
                        vector=vector,
                        payload={"data": data, "metadata": metadata or {}},
                    )
                ],
            )
            logger.info(f"Successfully upserted data to collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error upserting data: {str(e)}")
            raise

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in the collection"""
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=models.Filter(**filter) if filter else None,
            )
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "data": hit.payload["data"],
                    "metadata": hit.payload["metadata"],
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Error searching collection: {str(e)}")
            raise
