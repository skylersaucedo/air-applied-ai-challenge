# Testing Documentation

## Overview

This document outlines the testing strategy and procedures for the Air Applied AI Challenge project. Our testing approach covers unit tests, integration tests, end-to-end tests, and performance testing.

## Test Structure

```
tests/
├── unit/
│   ├── test_ocr.py
│   ├── test_transcription.py
│   ├── test_facial_recognition.py
│   └── test_semantic_search.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_qdrant_handler.py
│   └── test_aws_services.py
├── e2e/
│   └── test_full_workflow.py
└── performance/
    └── test_load.py
```

## Running Tests

### Prerequisites
- Python 3.8 or higher
- All dependencies installed from `requirements.txt`
- Environment variables configured in `.env`
- Test data generated using `scripts/generate_test_data.py`

### Commands

1. Run all tests:
```bash
pytest
```

2. Run specific test category:
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
pytest tests/performance/
```

3. Run with coverage:
```bash
pytest --cov=app tests/
```

## Test Data

### Sample Data Generation
```bash
python scripts/generate_test_data.py
```

Generated test data includes:
- Text files (including Shakespeare samples)
- Image files
- Audio files
- Video files

### Vector Search Testing
The `test_semantic_search.py` includes specific tests for:
- Shakespeare text search with famous quotes
- Vector similarity scoring
- Context retrieval

## Unit Tests

### OCR Service Tests
- Image preprocessing
- Text extraction
- Table detection
- Language detection

### Transcription Service Tests
- Audio preprocessing
- Speech-to-text conversion
- Speaker diarization
- Timestamp accuracy

### Facial Recognition Tests
- Face detection
- Feature extraction
- Emotion analysis
- Face matching

### Semantic Search Tests
- Text vectorization
- Query processing
- Relevance scoring
- Result ranking

## Integration Tests

### API Endpoint Tests
- Request validation
- Response formatting
- Error handling
- Rate limiting

### Qdrant Integration Tests
- Collection management
- Vector storage
- Search functionality
- Batch operations

### AWS Service Tests
- S3 operations
- SQS message handling
- CloudWatch logging
- ECS deployment

## End-to-End Tests

### Full Workflow Tests
- Complete request processing
- Multi-service interaction
- Data persistence
- Error recovery

## Performance Testing

### Load Tests
- Concurrent request handling
- Response time monitoring
- Resource utilization
- Scaling behavior

### Benchmarks
```bash
pytest tests/performance/test_load.py --benchmark-only
```

Target metrics:
- API Response Time: < 200ms
- Batch Processing: < 2s per item
- Search Latency: < 100ms
- Maximum Concurrent Requests: 1000

## CI/CD Integration

### GitHub Actions
Tests are automatically run on:
- Pull requests
- Merge to main
- Release tags

### Test Reports
- Coverage reports in HTML and XML
- JUnit XML test results
- Performance benchmark history

## Troubleshooting

Common issues and solutions:
1. Test data not found
   - Run `generate_test_data.py`
   - Check file permissions
2. Environment variables missing
   - Copy `.env.example` to `.env`
   - Fill in required values
3. Qdrant connection issues
   - Verify Qdrant is running
   - Check connection string

## Adding New Tests

Guidelines for adding new tests:
1. Follow existing test structure
2. Include docstrings and comments
3. Add appropriate fixtures
4. Update documentation

## Test Coverage Goals

Minimum coverage requirements:
- Unit Tests: 90%
- Integration Tests: 80%
- End-to-End Tests: 70%
- Overall Coverage: 85% 