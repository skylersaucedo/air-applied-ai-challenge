from typing import Dict

import pytest
from fakeredis import FakeRedis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Mock Redis
@pytest.fixture
def mock_redis():
    return FakeRedis()

# Mock Database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def test_db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture
def test_db_session(test_db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mock Qdrant Client
class MockQdrantClient:
    """Mock Qdrant client for testing."""

    def __init__(self):
        self.collections = {}
        self.points = {}

    def create_collection(self, collection_name: str, vectors_config=None):
        """Create a collection."""
        if collection_name not in self.collections:
            self.collections[collection_name] = vectors_config or VectorParams(size=384, distance=Distance.COSINE)
            self.points[collection_name] = {}

    def upsert(self, collection_name: str, points: list):
        """Upsert points into a collection."""
        if collection_name not in self.points:
            self.points[collection_name] = {}
        
        for point in points:
            self.points[collection_name][point.id] = {
                "vector": point.vector,
                "payload": point.payload
            }

    def search(self, collection_name: str, query_vector: list, limit: int = 10, score_threshold: float = 0.7, query_filter=None):
        """Search for similar vectors."""
        if collection_name not in self.points:
            return []

        # For testing, just return all points with a mock score
        results = []
        for point_id, point_data in self.points[collection_name].items():
            if query_filter:
                # Simple filter implementation
                metadata = point_data["payload"]["metadata"]
                if not self._check_filter(metadata, query_filter):
                    continue
            
            results.append(
                ScoredPoint(
                    id=point_id,
                    version=1,
                    score=0.9,  # Mock score
                    payload=point_data["payload"],
                    vector=point_data["vector"]
                )
            )
            if len(results) >= limit:
                break
        
        return results

    def _check_filter(self, metadata: dict, query_filter: dict) -> bool:
        """Check if metadata matches the filter."""
        if not query_filter:
            return True

        if isinstance(query_filter, Filter):
            query_filter = query_filter.dict()

        if "must" in query_filter:
            for condition in query_filter["must"]:
                key_parts = condition["key"].split(".")
                value = metadata
                for part in key_parts:
                    if part not in value:
                        return False
                    value = value[part]
                if "match" in condition:
                    if value != condition["match"]["value"]:
                        return False
        
        return True

@pytest.fixture
def mock_qdrant():
    return MockQdrantClient()

# Test environment variables
@pytest.fixture(autouse=True)
def test_env(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("POSTGRES_SERVER", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "test")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test")
    monkeypatch.setenv("POSTGRES_DB", "test")
    monkeypatch.setenv("QDRANT_CLUSTER", "localhost")
    monkeypatch.setenv("QDRANT_PORT", "6333")

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from qdrant_client.http.models import Filter, PointStruct, ScoredPoint
from qdrant_client.models import Distance, VectorParams

from app.main import app

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client fixture."""
    return MockQdrantClient() 