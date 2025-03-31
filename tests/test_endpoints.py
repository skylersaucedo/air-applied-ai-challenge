import base64

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Sample test data
SAMPLE_IMAGE_PATH = "tests/data/sample.jpg"
SAMPLE_AUDIO_PATH = "tests/data/sample.mp3"
SAMPLE_VIDEO_PATH = "tests/data/sample.mp4"


def encode_file(file_path: str) -> str:
    """Helper function to encode file to base64"""
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode()


@pytest.mark.asyncio
async def test_ocr_endpoint():
    """Test OCR endpoint with sample image"""
    # Read and encode sample image
    image_data = encode_file(SAMPLE_IMAGE_PATH)

    request_data = {
        "image": {"content": image_data, "format": "jpg"},
        "features": {
            "detectText": True,
            "languageHints": ["en"],
            "extractTables": True,
            "textDensity": "dense",
        },
        "options": {"scale": 1.0, "enhanceContrast": False, "deskew": True},
    }

    response = client.post("/api/v1/ocr/process", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "requestId" in data
    assert "textAnnotations" in data


@pytest.mark.asyncio
async def test_transcription_endpoint():
    """Test transcription endpoint with sample audio"""
    # Read and encode sample audio
    audio_data = encode_file(SAMPLE_AUDIO_PATH)

    request_data = {
        "audio": {"content": audio_data, "format": "mp3"},
        "config": {
            "language": "en-US",
            "enableWordTimestamps": True,
            "enableSpeakerDiarization": True,
            "maxSpeakers": 2,
            "filterProfanity": False,
            "model": "standard",
            "audioChannels": 1,
            "sampleRateHertz": 44100,
        },
    }

    response = client.post("/api/v1/transcription/process", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "requestId" in data
    assert "transcript" in data


@pytest.mark.asyncio
async def test_facial_recognition_endpoint():
    """Test facial recognition endpoint with sample image"""
    # Read and encode sample image
    image_data = encode_file(SAMPLE_IMAGE_PATH)

    request_data = {
        "image": {"content": image_data, "format": "png"},
        "features": {
            "detectFaces": True,
            "landmarks": True,
            "attributes": True,
            "matching": {"enabled": True, "threshold": 0.8, "databaseId": "test-db"},
        },
        "maxResults": 5,
    }

    response = client.post("/api/v1/facial-recognition/detect", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "faces" in data
    assert "summary" in data


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
    data = response.json()
    assert data["status"] == "success"
    assert "results" in data
    assert "relatedQueries" in data


@pytest.mark.asyncio
async def test_qdrant_vectorization():
    """Test Qdrant vectorization with different data types"""
    from app.services.qdrant_handler import QdrantHandler

    qdrant = QdrantHandler()

    # Test text vectorization
    text_vector = await qdrant.vectorize_text("Sample text for testing")
    assert len(text_vector) == 3072

    # Test image vectorization
    image_data = encode_file(SAMPLE_IMAGE_PATH)
    image_vector = await qdrant.vectorize_image(image_data)
    assert len(image_vector) == 512

    # Test audio vectorization
    audio_data = encode_file(SAMPLE_AUDIO_PATH)
    audio_vector = await qdrant.vectorize_audio(audio_data)
    assert len(audio_vector) == 512

    # Test video vectorization
    video_data = encode_file(SAMPLE_VIDEO_PATH)
    video_vector = await qdrant.vectorize_video(video_data)
    assert len(video_vector) == 768


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
