# OCR Service Flow Diagrams

## Sequence Diagram
```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant OCR as OCR Service
    participant S3 as AWS S3
    participant Q as Qdrant
    participant Redis as Redis Cache

    C->>API: POST /api/v1/ocr/process
    Note over C,API: Send image with config
    
    API->>OCR: Process request
    OCR->>Redis: Check cache
    
    alt Cache hit
        Redis-->>OCR: Return cached result
        OCR-->>API: Return result
        API-->>C: Return response
    else Cache miss
        OCR->>S3: Upload image
        S3-->>OCR: Return S3 URL
        OCR->>OCR: Process image
        OCR->>Q: Store vectors
        OCR->>Redis: Cache result
        OCR-->>API: Return result
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
    G --> H[Extract Text]
    G --> I[Detect Tables]
    G --> J[Analyze Layout]
    H --> K[Combine Results]
    I --> K
    J --> K
    K --> L[Store Vectors]
    L --> M[Cache Result]
    M --> N[Return Response]
```

## Architecture Overview
```mermaid
graph LR
    A[FastAPI Service] --> B[OCR Service]
    B --> C[AWS S3]
    B --> D[Redis Cache]
    B --> E[Qdrant Vector DB]
    B --> F[OCR Model]
    F --> G[Text Detection]
    F --> H[Table Detection]
    F --> I[Layout Analysis]
``` 