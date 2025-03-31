from typing import List, Optional

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.core.exceptions import APIException
from app.services.transcription_service import TranscriptionService

router = APIRouter()
logger = structlog.get_logger()
transcription_service = TranscriptionService()


class AudioContent(BaseModel):
    """Audio content model"""

    content: str = Field(..., description="Base64 encoded audio data")
    format: str = Field(..., description="Audio format (e.g., mp3, wav)")


class TranscriptionConfig(BaseModel):
    """Transcription configuration"""

    language: str = "en-US"
    alternativeLanguages: List[str] = []
    enableWordTimestamps: bool = True
    enableSpeakerDiarization: bool = False
    maxSpeakers: Optional[int] = None
    filterProfanity: bool = False
    model: str = "standard"
    audioChannels: int = 1
    sampleRateHertz: int = 44100


class TranscriptionRequest(BaseModel):
    """Transcription processing request model"""

    audio: AudioContent
    config: TranscriptionConfig = TranscriptionConfig()


class Segment(BaseModel):
    """Transcript segment model"""

    speakerId: Optional[int] = None
    text: str
    startTime: str
    endTime: str
    confidence: float


class Word(BaseModel):
    """Word model with timing"""

    word: str
    startTime: str
    endTime: str
    confidence: float
    speakerId: Optional[int] = None


class Metadata(BaseModel):
    """Processing metadata"""

    processingTime: str
    audioQuality: str
    backgroundNoise: str


class TranscriptionResponse(BaseModel):
    """Transcription processing response model"""

    status: str
    requestId: str
    duration: str
    transcript: str
    confidence: float
    segments: List[Segment]
    words: List[Word]
    metadata: Metadata


@router.post("/process", response_model=TranscriptionResponse)
async def process_transcription(
    background_tasks: BackgroundTasks, request: TranscriptionRequest
):
    """
    Process an audio file for transcription
    """
    try:
        # Process the audio
        result = await transcription_service.process_audio(
            audio_content=request.audio.content,
            audio_format=request.audio.format,
            config=request.config.dict(),
        )

        return TranscriptionResponse(**result)

    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Transcription processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch", response_model=List[TranscriptionResponse])
async def batch_process_transcription(
    background_tasks: BackgroundTasks, requests: List[TranscriptionRequest]
):
    """
    Process multiple audio files for transcription in batch
    """
    try:
        results = []
        for request in requests:
            result = await transcription_service.process_audio(
                audio_content=request.audio.content,
                audio_format=request.audio.format,
                config=request.config.dict(),
            )
            results.append(TranscriptionResponse(**result))

        return results

    except Exception as e:
        logger.error("Batch transcription processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/{request_id}", response_model=TranscriptionResponse)
async def get_transcription_status(request_id: str):
    """
    Get the status of a transcription processing job
    """
    try:
        status = await transcription_service.get_status(request_id)
        return TranscriptionResponse(**status)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Failed to get transcription status", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
