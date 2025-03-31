from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import structlog
from app.services.ocr_service import OCRService
from app.core.exceptions import APIException

router = APIRouter()
logger = structlog.get_logger()
ocr_service = OCRService()

class ImageContent(BaseModel):
    """Image content model"""
    content: str = Field(..., description="Base64 encoded image data")
    format: str = Field(..., description="Image format (e.g., jpg, png)")

class OCRFeatures(BaseModel):
    """OCR features configuration"""
    detectText: bool = True
    languageHints: List[str] = ["en"]
    extractTables: bool = False
    textDensity: str = "normal"

class OCROptions(BaseModel):
    """OCR processing options"""
    scale: float = 1.0
    enhanceContrast: bool = False
    deskew: bool = True

class OCRRequest(BaseModel):
    """OCR processing request model"""
    image: ImageContent
    features: OCRFeatures = OCRFeatures()
    options: OCROptions = OCROptions()

class Vertex(BaseModel):
    """Vertex model for bounding polygon"""
    x: int
    y: int

class BoundingPoly(BaseModel):
    """Bounding polygon model"""
    vertices: List[Vertex]

class TextAnnotation(BaseModel):
    """Text annotation model"""
    locale: Optional[str] = None
    description: str
    boundingPoly: BoundingPoly
    confidence: Optional[float] = None

class TableCell(BaseModel):
    """Table cell model"""
    text: str
    rowIndex: int
    columnIndex: int
    confidence: float

class Table(BaseModel):
    """Table model"""
    rows: int
    columns: int
    cells: List[TableCell]

class OCRResponse(BaseModel):
    """OCR processing response model"""
    status: str
    requestId: str
    processedTime: str
    textAnnotations: List[TextAnnotation]
    tables: Optional[List[Table]] = None
    confidence: float

class OCRStatusResponse(BaseModel):
    """OCR processing status response model"""
    file_id: str
    status: str
    progress: float
    error: Optional[str] = None

@router.post("/process", response_model=OCRResponse)
async def process_ocr(
    background_tasks: BackgroundTasks,
    request: OCRRequest
):
    """
    Process an image file for OCR
    """
    try:
        # Process the image
        result = await ocr_service.process_image(
            image_content=request.image.content,
            image_format=request.image.format,
            features=request.features.dict(),
            options=request.options.dict()
        )
        
        return OCRResponse(**result)
        
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("OCR processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch", response_model=List[OCRResponse])
async def batch_process_ocr(
    background_tasks: BackgroundTasks,
    requests: List[OCRRequest]
):
    """
    Process multiple images for OCR in batch
    """
    try:
        results = []
        for request in requests:
            result = await ocr_service.process_image(
                image_content=request.image.content,
                image_format=request.image.format,
                features=request.features.dict(),
                options=request.options.dict()
            )
            results.append(OCRResponse(**result))
            
        return results
        
    except Exception as e:
        logger.error("Batch OCR processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{request_id}", response_model=OCRResponse)
async def get_ocr_status(request_id: str):
    """
    Get the status of an OCR processing job
    """
    try:
        status = await ocr_service.get_status(request_id)
        return OCRResponse(**status)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Failed to get OCR status", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") 