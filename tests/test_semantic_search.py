import asyncio
from pathlib import Path

import pytest

from app.services.qdrant_handler import QdrantHandler


@pytest.fixture
async def qdrant_handler():
    handler = QdrantHandler()
    # Create a test collection for Shakespeare texts
    await handler._create_collections()
    return handler


@pytest.fixture
def shakespeare_text():
    text_path = Path("test_data/text/shakespeare_sample.txt")
    with open(text_path, "r", encoding="utf-8") as f:
        return f.read()


async def test_shakespeare_semantic_search(qdrant_handler, shakespeare_text):
    # First, vectorize and store the Shakespeare text
    text_vector = await qdrant_handler.vectorize_text(shakespeare_text)

    # Store in Qdrant with metadata
    await qdrant_handler.upsert_data(
        collection_name="text",
        data={"content": shakespeare_text},
        vector=text_vector,
        metadata={
            "source": "shakespeare",
            "title": "Famous Monologues",
            "author": "William Shakespeare",
        },
    )

    # Test cases with famous Shakespeare phrases
    test_queries = [
        "To be or not to be",
        "All the world's a stage",
        "Tomorrow and tomorrow and tomorrow",
    ]

    print("\nSemantic Search Results:")
    print("-" * 50)

    for query in test_queries:
        # Vectorize the search query
        query_vector = await qdrant_handler.vectorize_text(query)

        # Search in Qdrant
        results = await qdrant_handler.search(
            collection_name="text",
            query_vector=query_vector,
            limit=1,
            score_threshold=0.0,  # Set to 0 to see all results
        )

        print(f"\nQuery: '{query}'")
        if results:
            result = results[0]
            print(f"Similarity Score: {result.score:.4f}")
            # Print a snippet of the matched text
            content = result.payload.get("content", "")
            start_idx = max(0, content.lower().find(query.lower()) - 50)
            end_idx = min(
                len(content), content.lower().find(query.lower()) + len(query) + 50
            )
            snippet = content[start_idx:end_idx]
            print(f"Context: '...{snippet}...'")
        else:
            print("No results found")


if __name__ == "__main__":
    asyncio.run(test_shakespeare_semantic_search(qdrant_handler(), shakespeare_text()))
