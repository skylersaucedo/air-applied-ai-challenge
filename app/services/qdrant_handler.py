import base64
import io
import logging
from typing import Any, Dict, List, Optional, Union

import openai
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams
from transformers import (
    CLAPModel,
    CLAPProcessor,
    CLIPModel,
    CLIPProcessor,
    VideoMAEFeatureExtractor,
    VideoMAEForVideoClassification,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantHandler:
    """Handler for multimodal data vectorization and storage in Qdrant"""

    def __init__(self, qdrant_url: str = settings.QDRANT_URL):
        self.client = QdrantClient(url=qdrant_url)
        self._initialize_models()
        self._create_collections()

    def _initialize_models(self):
        """Initialize all required models"""
        # Text embedding model (OpenAI)
        self.text_model = "text-embedding-3-large"

        # Image embedding model (CLIP)
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32"
        )

        # Audio embedding model (CLAP)
        self.clap_model = CLAPModel.from_pretrained("laion/clap-htsat-unfied")
        self.clap_processor = CLAPProcessor.from_pretrained("laion/clap-htsat-unfied")

        # Video embedding model (VideoMAE)
        self.video_model = VideoMAEForVideoClassification.from_pretrained(
            "MCG-NJU/videomae-base"
        )
        self.video_processor = VideoMAEFeatureExtractor.from_pretrained(
            "MCG-NJU/videomae-base"
        )

    def _create_collections(self):
        """Create collections for each data type if they don't exist"""
        collections = {
            "text": VectorParams(size=3072, distance=Distance.COSINE),
            "image": VectorParams(size=512, distance=Distance.COSINE),
            "audio": VectorParams(size=512, distance=Distance.COSINE),
            "video": VectorParams(size=768, distance=Distance.COSINE),
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
        """Vectorize text using OpenAI's embedding model"""
        try:
            response = await openai.Embedding.acreate(model=self.text_model, input=text)
            return response["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Error vectorizing text: {str(e)}")
            raise

    async def vectorize_image(
        self, image_data: Union[str, bytes], description: Optional[str] = None
    ) -> List[float]:
        """Vectorize image using CLIP and optionally include text description"""
        try:
            # Convert base64 to PIL Image if needed
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_data))

            # Process image with CLIP
            inputs = self.clip_processor(images=image, return_tensors="pt")
            image_features = self.clip_model.get_image_features(**inputs)

            # If description provided, process text and combine embeddings
            if description:
                text_inputs = self.clip_processor(text=description, return_tensors="pt")
                text_features = self.clip_model.get_text_features(**text_inputs)

                # Combine embeddings (simple average)
                combined_features = (image_features + text_features) / 2
                return combined_features.detach().numpy().tolist()[0]

            return image_features.detach().numpy().tolist()[0]
        except Exception as e:
            logger.error(f"Error vectorizing image: {str(e)}")
            raise

    async def vectorize_audio(self, audio_data: Union[str, bytes]) -> List[float]:
        """Vectorize audio using CLAP"""
        try:
            # Convert base64 to bytes if needed
            if isinstance(audio_data, str):
                audio_data = base64.b64decode(audio_data)

            # Process audio with CLAP
            inputs = self.clap_processor(audio=audio_data, return_tensors="pt")
            audio_features = self.clap_model.get_audio_features(**inputs)

            return audio_features.detach().numpy().tolist()[0]
        except Exception as e:
            logger.error(f"Error vectorizing audio: {str(e)}")
            raise

    async def vectorize_video(self, video_data: Union[str, bytes]) -> List[float]:
        """Vectorize video using VideoMAE"""
        try:
            # Convert base64 to bytes if needed
            if isinstance(video_data, str):
                video_data = base64.b64decode(video_data)

            # Process video with VideoMAE
            inputs = self.video_processor(video=video_data, return_tensors="pt")
            video_features = self.video_model(**inputs).last_hidden_state.mean(dim=1)

            return video_features.detach().numpy().tolist()[0]
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
