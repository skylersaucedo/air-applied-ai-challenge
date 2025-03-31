from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.core.exceptions import APIException
from app.services.facial_recognition_service import FacialRecognitionService

router = APIRouter()
logger = structlog.get_logger()
facial_recognition_service = FacialRecognitionService()


class ImageContent(BaseModel):
    """Image content model"""

    content: str = Field(..., description="Base64 encoded image data")
    format: str = Field(..., description="Image format (e.g., jpg, png)")


class MatchingConfig(BaseModel):
    """Face matching configuration"""

    enabled: bool = False
    threshold: float = 0.8
    databaseId: Optional[str] = None


class FacialRecognitionFeatures(BaseModel):
    """Facial recognition features"""

    detectFaces: bool = True
    landmarks: bool = True
    attributes: bool = True
    matching: MatchingConfig = MatchingConfig()


class FacialRecognitionRequest(BaseModel):
    """Facial recognition processing request model"""

    image: ImageContent
    features: FacialRecognitionFeatures = FacialRecognitionFeatures()
    maxResults: int = 5


class Point(BaseModel):
    """2D point model"""

    x: int
    y: int


class BoundingBox(BaseModel):
    """Bounding box model"""

    topLeft: Point
    bottomRight: Point


class Landmarks(BaseModel):
    """Facial landmarks model"""

    leftEye: Point
    rightEye: Point
    nose: Point
    leftMouth: Point
    rightMouth: Point


class AttributeValue(BaseModel):
    """Attribute value with confidence"""

    value: Any
    confidence: float


class EmotionAttributes(BaseModel):
    """Emotion attributes model"""

    primary: str
    confidence: float
    all: Dict[str, float]


class FaceAttributes(BaseModel):
    """Face attributes model"""

    age: AttributeValue
    gender: AttributeValue
    emotion: EmotionAttributes
    glasses: AttributeValue


class MatchingResult(BaseModel):
    """Face matching result model"""

    matched: bool
    personId: Optional[str] = None
    score: Optional[float] = None
    name: Optional[str] = None


class Face(BaseModel):
    """Face detection result model"""

    boundingBox: BoundingBox
    confidence: float
    landmarks: Optional[Landmarks] = None
    attributes: Optional[FaceAttributes] = None
    matching: Optional[MatchingResult] = None


class Summary(BaseModel):
    """Processing summary model"""

    faceCount: int
    matchedCount: int


class FacialRecognitionResponse(BaseModel):
    """Facial recognition processing response model"""

    status: str
    requestId: str
    processedTime: str
    faces: List[Face]
    summary: Summary


@router.post("/detect", response_model=FacialRecognitionResponse)
async def detect_faces(
    background_tasks: BackgroundTasks, request: FacialRecognitionRequest
):
    """
    Detect faces in an image
    """
    try:
        # Process the image
        result = await facial_recognition_service.detect_faces(
            image_content=request.image.content,
            image_format=request.image.format,
            features=request.features.dict(),
            max_results=request.maxResults,
        )

        return FacialRecognitionResponse(**result)

    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Face detection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/recognize", response_model=FacialRecognitionResponse)
async def recognize_faces(
    background_tasks: BackgroundTasks, request: FacialRecognitionRequest
):
    """
    Recognize faces in an image against reference faces
    """
    try:
        # Process the image
        result = await facial_recognition_service.recognize_faces(
            image_content=request.image.content,
            image_format=request.image.format,
            features=request.features.dict(),
            max_results=request.maxResults,
        )

        return FacialRecognitionResponse(**result)

    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Face recognition failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch", response_model=List[FacialRecognitionResponse])
async def batch_detect_faces(
    background_tasks: BackgroundTasks, requests: List[FacialRecognitionRequest]
):
    """
    Detect faces in multiple images in batch
    """
    try:
        results = []
        for request in requests:
            result = await facial_recognition_service.detect_faces(
                image_content=request.image.content,
                image_format=request.image.format,
                features=request.features.dict(),
                max_results=request.maxResults,
            )
            results.append(FacialRecognitionResponse(**result))

        return results

    except Exception as e:
        logger.error("Batch face detection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/{request_id}", response_model=FacialRecognitionResponse)
async def get_facial_recognition_status(request_id: str):
    """
    Get the status of a facial recognition processing job
    """
    try:
        status = await facial_recognition_service.get_status(request_id)
        return FacialRecognitionResponse(**status)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Failed to get facial recognition status", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
