from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog
from app.services.facial_recognition_service import FacialRecognitionService
from app.core.exceptions import APIException

router = APIRouter()
logger = structlog.get_logger()
facial_recognition_service = FacialRecognitionService()

class FacialRecognitionRequest(BaseModel):
    """Facial recognition processing request model"""
    file_id: str
    detection_threshold: Optional[float] = 0.6
    recognition_threshold: Optional[float] = 0.8
    return_embeddings: Optional[bool] = False

class FaceDetection(BaseModel):
    """Face detection result model"""
    face_id: str
    bounding_box: Dict[str, float]
    confidence: float
    landmarks: Optional[List[Dict[str, float]]] = None
    embedding: Optional[List[float]] = None

class FacialRecognitionResponse(BaseModel):
    """Facial recognition processing response model"""
    file_id: str
    faces: List[FaceDetection]
    total_faces: int
    processing_time: float

class FacialRecognitionStatusResponse(BaseModel):
    """Facial recognition processing status response model"""
    file_id: str
    status: str
    progress: float
    error: Optional[str] = None

@router.post("/detect", response_model=FacialRecognitionResponse)
async def detect_faces(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    detection_threshold: Optional[float] = 0.6,
    recognition_threshold: Optional[float] = 0.8,
    return_embeddings: Optional[bool] = False
):
    """
    Detect faces in an image
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise APIException(
                status_code=400,
                message="Invalid file type. Only image files are supported."
            )
        
        # Process the image
        result = await facial_recognition_service.detect_faces(
            file=file,
            detection_threshold=detection_threshold,
            recognition_threshold=recognition_threshold,
            return_embeddings=return_embeddings
        )
        
        return FacialRecognitionResponse(
            file_id=result["file_id"],
            faces=result["faces"],
            total_faces=result["total_faces"],
            processing_time=result["processing_time"]
        )
        
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Face detection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/recognize", response_model=Dict[str, Any])
async def recognize_faces(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    reference_faces: List[UploadFile] = File(...),
    threshold: Optional[float] = 0.8
):
    """
    Recognize faces in an image against reference faces
    """
    try:
        # Validate file types
        if not file.content_type.startswith('image/'):
            raise APIException(
                status_code=400,
                message="Invalid file type. Only image files are supported."
            )
        
        # Process the images
        result = await facial_recognition_service.recognize_faces(
            file=file,
            reference_faces=reference_faces,
            threshold=threshold
        )
        
        return result
        
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Face recognition failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch", response_model=List[FacialRecognitionResponse])
async def batch_detect_faces(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    detection_threshold: Optional[float] = 0.6,
    recognition_threshold: Optional[float] = 0.8,
    return_embeddings: Optional[bool] = False
):
    """
    Detect faces in multiple images in batch
    """
    try:
        results = []
        for file in files:
            if not file.content_type.startswith('image/'):
                logger.warning("Skipping invalid file type", filename=file.filename)
                continue
                
            result = await facial_recognition_service.detect_faces(
                file=file,
                detection_threshold=detection_threshold,
                recognition_threshold=recognition_threshold,
                return_embeddings=return_embeddings
            )
            results.append(FacialRecognitionResponse(**result))
            
        return results
        
    except Exception as e:
        logger.error("Batch face detection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{file_id}", response_model=FacialRecognitionStatusResponse)
async def get_facial_recognition_status(file_id: str):
    """
    Get the status of a facial recognition processing job
    """
    try:
        status = await facial_recognition_service.get_status(file_id)
        return FacialRecognitionStatusResponse(**status)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Failed to get facial recognition status", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") 