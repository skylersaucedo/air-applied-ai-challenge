import time

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentation
from prometheus_client import Counter, Histogram

from app.api.v1.endpoints import facial_recognition, ocr, semantic_search, transcription
from app.core.config import settings
from app.core.exceptions import APIException
from app.core.middleware import RequestLoggingMiddleware

# Initialize structured logger
logger = structlog.get_logger()

# Initialize metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Air AI Integration Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)

# Initialize OpenTelemetry instrumentation
FastAPIInstrumentation.instrument_app(app)


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(
        time.time() - start_time
    )

    return response


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    logger.error(
        "API exception",
        error=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# Include routers
app.include_router(ocr.router, prefix=f"{settings.API_V1_STR}/ocr", tags=["OCR"])
app.include_router(
    transcription.router,
    prefix=f"{settings.API_V1_STR}/transcription",
    tags=["Transcription"],
)
app.include_router(
    facial_recognition.router,
    prefix=f"{settings.API_V1_STR}/facial-recognition",
    tags=["Facial Recognition"],
)
app.include_router(
    semantic_search.router,
    prefix=f"{settings.API_V1_STR}/semantic-search",
    tags=["Semantic Search"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
