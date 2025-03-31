"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import facial_recognition, ocr, semantic_search, transcription

app = FastAPI(
    title="Air Applied AI Challenge",
    description="API for the Air Applied AI Challenge",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(transcription.router, prefix="/api/v1/transcription", tags=["Transcription"])
app.include_router(facial_recognition.router, prefix="/api/v1/facial-recognition", tags=["Facial Recognition"])
app.include_router(semantic_search.router, prefix="/api/v1/semantic-search", tags=["Semantic Search"])


@app.get("/")
async def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Air Applied AI Challenge API",
        "docs": "/docs",
        "redoc": "/redoc",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
