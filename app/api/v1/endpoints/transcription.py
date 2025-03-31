from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import structlog
from app.services.transcription_service import TranscriptionService
from app.core.exceptions import APIException

router = APIRouter()
logger = structlog.get_logger()
transcription_service = TranscriptionService()

class TranscriptionRequest(BaseModel):
    """Transcription processing request model"""
    file_id: str
    language: Optional[str] = "en"
    diarization: Optional[bool] = False
    speaker_count: Optional[int] = None

class TranscriptionResponse(BaseModel):
    """Transcription processing response model"""
    file_id: str
    text: str
    segments: List[dict]
    language: str
    duration: float
    speaker_count: Optional[int]
    processing_time: float

class TranscriptionStatusResponse(BaseModel):
    """Transcription processing status response model"""
    file_id: str
    status: str
    progress: float
    error: Optional[str] = None

@router.post("/process", response_model=TranscriptionResponse)
async def process_transcription(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = "en",
    diarization: Optional[bool] = False,
    speaker_count: Optional[int] = None
):
    """
    Process an audio file for transcription
    """
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise APIException(
                status_code=400,
                message="Invalid file type. Only audio files are supported."
            )
        
        # Process the audio
        result = await transcription_service.process_audio(
            file=file,
            language=language,
            diarization=diarization,
            speaker_count=speaker_count
        )
        
        return TranscriptionResponse(
            file_id=result["file_id"],
            text=result["text"],
            segments=result["segments"],
            language=result["language"],
            duration=result["duration"],
            speaker_count=result.get("speaker_count"),
            processing_time=result["processing_time"]
        )
        
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Transcription processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch", response_model=List[TranscriptionResponse])
async def batch_process_transcription(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    language: Optional[str] = "en",
    diarization: Optional[bool] = False,
    speaker_count: Optional[int] = None
):
    """
    Process multiple audio files for transcription in batch
    """
    try:
        results = []
        for file in files:
            if not file.content_type.startswith('audio/'):
                logger.warning("Skipping invalid file type", filename=file.filename)
                continue
                
            result = await transcription_service.process_audio(
                file=file,
                language=language,
                diarization=diarization,
                speaker_count=speaker_count
            )
            results.append(TranscriptionResponse(**result))
            
        return results
        
    except Exception as e:
        logger.error("Batch transcription processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{file_id}", response_model=TranscriptionStatusResponse)
async def get_transcription_status(file_id: str):
    """
    Get the status of a transcription processing job
    """
    try:
        status = await transcription_service.get_status(file_id)
        return TranscriptionStatusResponse(**status)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Failed to get transcription status", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") 