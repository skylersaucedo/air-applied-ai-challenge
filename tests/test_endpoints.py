import base64
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.qdrant_handler import QdrantHandler
from tests.test_config import MockQdrantClient

client = TestClient(app)

# Sample test data
SAMPLE_IMAGE_PATH = "tests/data/sample.jpg"
SAMPLE_AUDIO_PATH = "tests/data/sample.mp3"
SAMPLE_VIDEO_PATH = "tests/data/sample.mp4"
SAMPLE_TEXT_PATH = "tests/data/sample.txt"


def encode_file(file_path: str) -> str:
    """Helper function to encode file to base64"""
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


@pytest.mark.asyncio
async def test_ocr_endpoint():
    """Test OCR endpoint with sample text"""
    # Read and encode sample text
    text_data = encode_file(SAMPLE_TEXT_PATH)

    response = client.post(
        "/api/v1/ocr/extract",
        json={"file": text_data, "options": {"language": "eng"}},
    )

    assert response.status_code == 200
    assert "text" in response.json()
    assert isinstance(response.json()["text"], str)


@pytest.mark.asyncio
async def test_transcription_endpoint():
    """Test transcription endpoint with sample text"""
    # Read and encode sample text
    text_data = encode_file(SAMPLE_TEXT_PATH)

    response = client.post(
        "/api/v1/transcription/process",
        json={"file": text_data, "options": {"language": "eng"}},
    )

    assert response.status_code == 200
    assert "text" in response.json()
    assert isinstance(response.json()["text"], str)


@pytest.mark.asyncio
async def test_facial_recognition_endpoint():
    """Test facial recognition endpoint with sample text"""
    # Read and encode sample text
    text_data = encode_file(SAMPLE_TEXT_PATH)

    response = client.post(
        "/api/v1/facial-recognition/detect",
        json={"file": text_data},
    )

    assert response.status_code == 200
    assert "faces" in response.json()
    assert isinstance(response.json()["faces"], list)


@pytest.mark.asyncio
async def test_semantic_search_endpoint():
    """Test semantic search endpoint"""
    request_data = {
        "query": "What are the side effects of the new COVID-19 vaccine?",
        "options": {
            "corpus": "test-corpus",
            "maxResults": 5,
            "minRelevanceScore": 0.75,
            "includeMetadata": True,
            "filters": {"dateRange": {"from": "2023-01-01", "to": "2024-10-31"}},
        },
    }

    response = client.post("/api/v1/semantic-search/search", json=request_data)
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)


@pytest.mark.asyncio
async def test_qdrant_vectorization():
    """Test Qdrant vectorization with different data types"""
    qdrant = QdrantHandler()

    # Test text vectorization
    text_vector = await qdrant.vectorize_text("Sample text for testing")
    assert len(text_vector) == 384  # Updated to match the new model's vector size

    # Test image vectorization
    with open(SAMPLE_TEXT_PATH, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    image_vector = await qdrant.vectorize_image(image_data)
    assert len(image_vector) == 384  # Updated to match the new model's vector size

    # Test audio vectorization
    with open(SAMPLE_TEXT_PATH, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")
    audio_vector = await qdrant.vectorize_audio(audio_data)
    assert len(audio_vector) == 384  # Updated to match the new model's vector size

    # Test video vectorization
    with open(SAMPLE_TEXT_PATH, "rb") as f:
        video_data = base64.b64encode(f.read()).decode("utf-8")
    video_vector = await qdrant.vectorize_video(video_data)
    assert len(video_vector) == 384  # Updated to match the new model's vector size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
