# Transcription Service Flow Diagrams

## Sequence Diagram
```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant TS as Transcription Service
    participant S3 as AWS S3
    participant SQS as AWS SQS
    participant Q as Qdrant
    participant Redis as Redis Cache

    C->>API: POST /api/v1/transcription/process
    Note over C,API: Send audio with config
    
    API->>TS: Process request
    TS->>Redis: Check cache
    
    alt Cache hit
        Redis-->>TS: Return cached result
        TS-->>API: Return result
        API-->>C: Return response
    else Cache miss
        TS->>S3: Upload audio
        S3-->>TS: Return S3 URL
        TS->>SQS: Queue transcription job
        TS-->>API: Return job ID
        API-->>C: Return job ID
        
        loop Until complete
            TS->>SQS: Check job status
            SQS-->>TS: Update status
        end
        
        TS->>Q: Store vectors
        TS->>Redis: Cache result
        TS-->>API: Return result
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
    F --> G[Queue Processing]
    G --> H[Process Audio]
    H --> I[Speech Recognition]
    H --> J[Speaker Diarization]
    H --> K[Generate Timestamps]
    I --> L[Combine Results]
    J --> L
    K --> L
    L --> M[Store Vectors]
    M --> N[Cache Result]
    N --> O[Return Response]
```

## Architecture Overview
```mermaid
graph LR
    A[FastAPI Service] --> B[Transcription Service]
    B --> C[AWS S3]
    B --> D[Redis Cache]
    B --> E[Qdrant Vector DB]
    B --> F[AWS SQS]
    B --> G[Speech Model]
    G --> H[ASR Engine]
    G --> I[Speaker ID]
    G --> J[Timestamp Gen]
``` 