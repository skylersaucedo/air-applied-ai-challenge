# Facial Recognition Service Flow Diagrams

## Sequence Diagram
```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant FR as Face Recognition Service
    participant S3 as AWS S3
    participant Q as Qdrant
    participant Redis as Redis Cache

    C->>API: POST /api/v1/facial-recognition/detect
    Note over C,API: Send image with config
    
    API->>FR: Process request
    FR->>Redis: Check cache
    
    alt Cache hit
        Redis-->>FR: Return cached result
        FR-->>API: Return result
        API-->>C: Return response
    else Cache miss
        FR->>S3: Upload image
        S3-->>FR: Return S3 URL
        FR->>FR: Detect faces
        FR->>FR: Extract features
        FR->>Q: Match against database
        FR->>Q: Store face vectors
        FR->>Redis: Cache result
        FR-->>API: Return result
        API-->>C: Return response
    end
```

## Process Flow
```mermaid
graph TD
    A[Client Request] --> B{Validate Input}
    B -->|Invalid| C[Return Error]
    B -->|Valid| D{Check Cache}
    D -->|Cache Hit| E[Return Cached Result]
    D -->|Cache Miss| F[Upload to S3]
    F --> G[Process Image]
    G --> H[Detect Faces]
    G --> I[Extract Features]
    G --> J[Analyze Emotions]
    H --> K[Face Matching]
    I --> K
    J --> K
    K --> L[Store Vectors]
    L --> M[Cache Result]
    M --> N[Return Response]
```

## Architecture Overview
```mermaid
graph LR
    A[FastAPI Service] --> B[Face Recognition Service]
    B --> C[AWS S3]
    B --> D[Redis Cache]
    B --> E[Qdrant Vector DB]
    B --> F[Face Model]
    F --> G[Face Detection]
    F --> H[Feature Extraction]
    F --> I[Emotion Analysis]
    F --> J[Face Matching]
``` 