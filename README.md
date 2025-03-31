# Air AI Integration Platform

A comprehensive AI integration platform built with FastAPI, AWS, and modern AI services.

## Project Structure

```
air-applied-ai-challenge/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── ocr.py
│   │           ├── transcription.py
│   │           ├── facial_recognition.py
│   │           └── semantic_search.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── middleware.py
│   ├── services/
│   │   ├── ocr_service.py
│   │   ├── transcription_service.py
│   │   ├── facial_recognition_service.py
│   │   └── semantic_search_service.py
│   └── main.py
├── tests/
│   ├── api/
│   ├── services/
│   └── conftest.py
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── requirements.txt
├── .env.example
└── README.md
```

## API Documentation

### OCR Endpoints

#### Process Image
```http
POST /api/v1/ocr/process
```

Request:
```json
{
  "image": {
    "content": "base64_encoded_image_data_here",
    "format": "jpg"
  },
  "features": {
    "detectText": true,
    "languageHints": ["en", "fr", "es"],
    "extractTables": true,
    "textDensity": "dense"
  },
  "options": {
    "scale": 1.0,
    "enhanceContrast": false,
    "deskew": true
  }
}
```

Response:
```json
{
  "status": "success",
  "requestId": "ocr-req-12345",
  "processedTime": "2025-03-31T10:15:30Z",
  "textAnnotations": [
    {
      "locale": "en",
      "description": "The complete extracted text from the image",
      "boundingPoly": {
        "vertices": [
          {"x": 0, "y": 0},
          {"x": 1000, "y": 0},
          {"x": 1000, "y": 800},
          {"x": 0, "y": 800}
        ]
      }
    }
  ],
  "tables": [
    {
      "rows": 5,
      "columns": 3,
      "cells": [
        {
          "text": "Item",
          "rowIndex": 0,
          "columnIndex": 0,
          "confidence": 0.95
        }
      ]
    }
  ],
  "confidence": 0.92
}
```

### Transcription Endpoints

#### Process Audio
```http
POST /api/v1/transcription/process
```

Request:
```json
{
  "audio": {
    "content": "base64_encoded_audio_data_here",
    "format": "mp3"
  },
  "config": {
    "language": "en-US",
    "alternativeLanguages": ["en-GB", "en-AU"],
    "enableWordTimestamps": true,
    "enableSpeakerDiarization": true,
    "maxSpeakers": 2,
    "filterProfanity": false,
    "model": "standard",
    "audioChannels": 1,
    "sampleRateHertz": 44100
  }
}
```

Response:
```json
{
  "status": "completed",
  "requestId": "transcript-req-67890",
  "duration": "00:05:32",
  "transcript": "This is the full transcript of the audio file with all spoken content.",
  "confidence": 0.87,
  "segments": [
    {
      "speakerId": 1,
      "text": "Hello, how are you doing today?",
      "startTime": "00:00:02.500",
      "endTime": "00:00:05.100",
      "confidence": 0.92
    }
  ],
  "words": [
    {
      "word": "Hello",
      "startTime": "00:00:02.500",
      "endTime": "00:00:02.900",
      "confidence": 0.95,
      "speakerId": 1
    }
  ],
  "metadata": {
    "processingTime": "15.2",
    "audioQuality": "good",
    "backgroundNoise": "low"
  }
}
```

### Facial Recognition Endpoints

#### Detect Faces
```http
POST /api/v1/facial-recognition/detect
```

Request:
```json
{
  "image": {
    "content": "base64_encoded_image_data_here",
    "format": "png"
  },
  "features": {
    "detectFaces": true,
    "landmarks": true,
    "attributes": true,
    "matching": {
      "enabled": true,
      "threshold": 0.8,
      "databaseId": "employees-db-2025"
    }
  },
  "maxResults": 5
}
```

Response:
```json
{
  "status": "success",
  "requestId": "face-req-24680",
  "processedTime": "2025-03-31T14:22:15Z",
  "faces": [
    {
      "boundingBox": {
        "topLeft": {"x": 125, "y": 75},
        "bottomRight": {"x": 225, "y": 175}
      },
      "confidence": 0.96,
      "landmarks": {
        "leftEye": {"x": 152, "y": 107},
        "rightEye": {"x": 198, "y": 107},
        "nose": {"x": 175, "y": 135},
        "leftMouth": {"x": 155, "y": 155},
        "rightMouth": {"x": 195, "y": 155}
      },
      "attributes": {
        "age": {
          "value": 34,
          "confidence": 0.85
        },
        "gender": {
          "value": "female",
          "confidence": 0.92
        },
        "emotion": {
          "primary": "happy",
          "confidence": 0.88,
          "all": {
            "happy": 0.88,
            "neutral": 0.08,
            "surprised": 0.04
          }
        },
        "glasses": {
          "value": false,
          "confidence": 0.97
        }
      },
      "matching": {
        "matched": true,
        "personId": "emp-1234",
        "score": 0.92,
        "name": "Jane Doe"
      }
    }
  ],
  "summary": {
    "faceCount": 1,
    "matchedCount": 1
  }
}
```

### Semantic Search Endpoints

#### Search Documents
```http
POST /api/v1/semantic-search/search
```

Request:
```json
{
  "query": "What are the side effects of the new COVID-19 vaccine?",
  "options": {
    "corpus": "medical-publications-2024",
    "maxResults": 10,
    "minRelevanceScore": 0.75,
    "includeMetadata": true,
    "filters": {
      "dateRange": {
        "from": "2023-01-01",
        "to": "2024-10-31"
      },
      "sources": ["peer-reviewed", "clinical-trials"],
      "authors": ["who", "cdc", "nih"]
    },
    "embedModel": "semantic-v3",
    "queryExpansion": true,
    "retrievalMethod": "hybrid"
  }
}
```

Response:
```json
{
  "status": "success",
  "requestId": "search-req-13579",
  "queryTime": "0.246",
  "results": [
    {
      "documentId": "med-doc-45678",
      "title": "Clinical Trial Results: Safety Profile of mRNA-based COVID-19 Vaccine XYZ",
      "snippet": "The most common side effects reported in trial participants included mild to moderate pain at the injection site (68%), fatigue (43%), headache (39%), and muscle pain (38%). Serious adverse events were rare, occurring in less than 0.5% of participants...",
      "relevanceScore": 0.94,
      "source": "Journal of Immunology",
      "authors": ["Smith, J.", "Johnson, A.", "Williams, R."],
      "publicationDate": "2024-05-12",
      "url": "https://example.com/journal/45678",
      "citations": 127,
      "semanticMatches": [
        {"term": "side effects", "score": 0.98},
        {"term": "COVID-19 vaccine", "score": 0.95},
        {"term": "safety profile", "score": 0.87}
      ]
    }
  ],
  "relatedQueries": [
    "COVID-19 vaccine efficacy rates",
    "COVID-19 vaccine comparison",
    "Long-term COVID-19 vaccine safety data"
  ],
  "facets": {
    "sources": [
      {"value": "peer-reviewed", "count": 7},
      {"value": "clinical-trials", "count": 3}
    ],
    "publicationYear": [
      {"value": "2024", "count": 8},
      {"value": "2023", "count": 2}
    ]
  }
}
```

## Getting Started

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- AWS CLI configured with appropriate credentials
- Terraform installed

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/air-applied-ai-challenge.git
cd air-applied-ai-challenge
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and configure your settings:
```bash
cp .env.example .env
```

5. Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Infrastructure Deployment

1. Configure AWS credentials:
```bash
aws configure
```

2. Initialize Terraform:
```bash
cd terraform
terraform init
```

3. Deploy the infrastructure:
```bash
terraform apply
```

### CI/CD Pipeline

The project includes a GitHub Actions workflow that:
- Runs tests and linting
- Performs security checks
- Builds and pushes Docker images to ECR
- Deploys to ECS
- Runs infrastructure tests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 