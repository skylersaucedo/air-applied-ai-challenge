import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    os.environ["AWS_ACCESS_KEY_ID"] = "test_key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test_secret"
    os.environ["AWS_REGION"] = "us-east-2"
    os.environ["QDRANT_CLUSTER"] = "localhost"
    os.environ["QDRANT_PORT"] = "6333"
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"


@pytest.fixture
def test_data_dir():
    """Create and return test data directory"""
    base_dir = Path("tests/data")
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


@pytest.fixture
def sample_image(test_data_dir):
    """Create a sample test image"""
    from PIL import Image, ImageDraw, ImageFont
    
    image_path = test_data_dir / "sample.jpg"
    if not image_path.exists():
        # Create a sample image with text
        img = Image.new('RGB', (400, 100), color='white')
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Sample Test Image", fill='black')
        img.save(image_path)
    
    return str(image_path)


@pytest.fixture
def sample_audio(test_data_dir):
    """Create a sample test audio file"""
    import numpy as np
    from scipy.io import wavfile
    
    audio_path = test_data_dir / "sample.wav"
    if not audio_path.exists():
        # Create a simple sine wave
        sample_rate = 44100
        duration = 1  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        data = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        wavfile.write(audio_path, sample_rate, data.astype(np.float32))
    
    return str(audio_path)


@pytest.fixture
def sample_video(test_data_dir):
    """Create a sample test video file"""
    video_path = test_data_dir / "sample.mp4"
    if not video_path.exists():
        # Create an empty file for now - we'll implement actual video creation if needed
        video_path.touch()
    
    return str(video_path) 