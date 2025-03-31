import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest

from app.services.qdrant_handler import QdrantHandler
from tests.test_config import MockQdrantClient


@pytest.fixture
def mock_qdrant_handler(monkeypatch):
    """Mock QdrantHandler for testing"""
    def mock_init(self, qdrant_url="http://localhost:6333"):
        self.client = MockQdrantClient()
        self._initialize_models()
        self._create_collections()
    
    monkeypatch.setattr(QdrantHandler, "__init__", mock_init)
    return QdrantHandler()


@pytest.mark.asyncio
async def test_semantic_search_basic(mock_qdrant_handler):
    """Test basic semantic search functionality"""
    # Test document
    test_doc = {
        "id": "test1",
        "content": "This is a test document",
        "metadata": {"type": "text"}
    }
    
    # Get vector for test document
    vector = await mock_qdrant_handler.vectorize_text(test_doc["content"])
    
    # Upsert test document
    await mock_qdrant_handler.upsert_data(
        collection_name="text",
        data=test_doc,
        vector=vector,
        metadata=test_doc["metadata"]
    )
    
    # Search for similar documents
    results = await mock_qdrant_handler.search(
        collection_name="text",
        query_vector=vector,
        limit=1
    )
    
    assert len(results) == 1
    assert results[0]["data"]["content"] == test_doc["content"]
    assert results[0]["metadata"] == test_doc["metadata"]


@pytest.mark.asyncio
async def test_semantic_search_empty_collection(mock_qdrant_handler):
    """Test search on empty collection"""
    # Create a test vector
    vector = [0.1] * 384
    
    # Search empty collection
    results = await mock_qdrant_handler.search(
        collection_name="text",
        query_vector=vector,
        limit=10
    )
    
    assert len(results) == 0


@pytest.mark.asyncio
async def test_semantic_search_with_filter(mock_qdrant_handler):
    """Test search with metadata filter"""
    # Test documents
    docs = [
        {
            "id": "test1",
            "content": "Document about technology",
            "metadata": {"category": "tech"}
        },
        {
            "id": "test2",
            "content": "Document about nature",
            "metadata": {"category": "nature"}
        }
    ]
    
    # Upsert test documents
    for doc in docs:
        vector = await mock_qdrant_handler.vectorize_text(doc["content"])
        await mock_qdrant_handler.upsert_data(
            collection_name="text",
            data=doc,
            vector=vector,
            metadata=doc["metadata"]
        )
    
    # Search with filter
    vector = await mock_qdrant_handler.vectorize_text("tech article")
    results = await mock_qdrant_handler.search(
        collection_name="text",
        query_vector=vector,
        limit=10,
        filter={"must": [{"key": "metadata.category", "match": {"value": "tech"}}]}
    )
    
    assert len(results) == 1
    assert results[0]["data"]["id"] == "test1"
    assert results[0]["metadata"]["category"] == "tech"
