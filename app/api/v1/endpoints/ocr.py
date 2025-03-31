from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import structlog
from app.services.ocr_service import OCRService
from app.core.exceptions import APIException

router = APIRouter()
logger = structlog.get_logger()
ocr_service = OCRService()

class OCRRequest(BaseModel):
    """OCR processing request model"""
    file_id: str
    language: Optional[str] = "en"
    confidence_threshold: Optional[float] = 0.8

class OCRResponse(BaseModel):
    """OCR processing response model"""
    file_id: str
    text: str
    confidence: float
    blocks: List[dict]
    language: str
    processing_time: float

class OCRStatusResponse(BaseModel):
    """OCR processing status response model"""
    file_id: str
    status: str
    progress: float
    error: Optional[str] = None

@router.post("/process", response_model=OCRResponse)
async def process_ocr(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = "en",
    confidence_threshold: Optional[float] = 0.8
):
    """
    Process an image file for OCR
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise APIException(
                status_code=400,
                message="Invalid file type. Only image files are supported."
            )
        
        # Process the image
        result = await ocr_service.process_image(
            file=file,
            language=language,
            confidence_threshold=confidence_threshold
        )
        
        return OCRResponse(
            file_id=result["file_id"],
            text=result["text"],
            confidence=result["confidence"],
            blocks=result["blocks"],
            language=result["language"],
            processing_time=result["processing_time"]
        )
        
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("OCR processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch", response_model=List[OCRResponse])
async def batch_process_ocr(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    language: Optional[str] = "en",
    confidence_threshold: Optional[float] = 0.8
):
    """
    Process multiple images for OCR in batch
    """
    try:
        results = []
        for file in files:
            if not file.content_type.startswith('image/'):
                logger.warning("Skipping invalid file type", filename=file.filename)
                continue
                
            result = await ocr_service.process_image(
                file=file,
                language=language,
                confidence_threshold=confidence_threshold
            )
            results.append(OCRResponse(**result))
            
        return results
        
    except Exception as e:
        logger.error("Batch OCR processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{file_id}", response_model=OCRStatusResponse)
async def get_ocr_status(file_id: str):
    """
    Get the status of an OCR processing job
    """
    try:
        status = await ocr_service.get_status(file_id)
        return OCRStatusResponse(**status)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Failed to get OCR status", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") 