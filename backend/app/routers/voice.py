"""Voice router — speech-to-text (STT) and text-to-speech (TTS).

Endpoints:
    POST /api/v1/voice/transcribe  – WAV/audio → transcript
    POST /api/v1/voice/tts         – text + language → MP3 audio
"""

from __future__ import annotations

import asyncio
import logging
import sys
import time

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel

from app.routers.auth import get_current_user
from app.utils import find_project_root

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice"])

# Add project root so VoiceHandler can be imported
_root = find_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Lazy import — VoiceHandler handles missing gtts/speech_recognition gracefully
try:
    from voice_handler import VoiceHandler as _VoiceHandler  # type: ignore
    _voice_handler = _VoiceHandler()
except Exception:  # noqa: BLE001
    _voice_handler = None  # type: ignore[assignment]

_SUPPORTED_LANGUAGES = {"english", "tamil", "bilingual"}


def _get_handler():
    if _voice_handler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice services are not available on this server.",
        )
    return _voice_handler


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #

class TranscriptResponse(BaseModel):
    transcript: str
    language_used: str


class TtsRequest(BaseModel):
    text: str
    language_preference: str = "english"


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #

@router.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio recording from the microphone (WAV/WebM/MP3/FLAC/OGG)"),
    language_preference: str = Form(default="english"),
    _user=Depends(get_current_user),
):
    """Transcribe uploaded audio to text using Google Speech Recognition.

    The ``language_preference`` form field can be ``english``, ``tamil``, or
    ``bilingual``.  Bilingual / Tanglish input is attempted first with the
    ``en-IN`` locale (Latin-script Tamil / code-switching) and then with
    ``ta-IN`` as a fallback.

    Supported formats: WAV, AIFF, FLAC (native); WebM, MP3, OGG, MP4
    (via pydub + ffmpeg when installed).  An empty string is returned when
    speech cannot be recognised or when the STT dependency is not installed.
    """
    handler = _get_handler()

    lang = language_preference.lower()
    if lang not in _SUPPORTED_LANGUAGES:
        lang = "english"

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio data received.",
        )

    # Offload blocking SpeechRecognition (network I/O to Google STT) to a
    # thread so the async event loop stays responsive during transcription.
    t0 = time.perf_counter()
    transcript: str = await asyncio.to_thread(
        handler.transcribe_audio, audio_bytes, lang
    )
    logger.info(
        "STT lang=%s transcript_length=%d latency=%.3fs",
        lang, len(transcript), time.perf_counter() - t0,
    )
    return TranscriptResponse(transcript=transcript, language_used=lang)


@router.post("/tts")
async def text_to_speech(
    req: TtsRequest,
    _user=Depends(get_current_user),
):
    """Convert text to MP3 speech using Google TTS.

    Returns the raw MP3 bytes with ``Content-Type: audio/mpeg``.
    Returns 503 if TTS is unavailable.
    """
    handler = _get_handler()

    lang = (req.language_preference or "english").lower()
    if lang not in _SUPPORTED_LANGUAGES:
        lang = "english"

    text = req.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="text must not be empty.",
        )

    # Offload blocking gTTS synthesis (HTTP round-trip to Google) to a thread
    # so the async event loop stays responsive for concurrent requests.
    t0 = time.perf_counter()
    mp3_bytes = await asyncio.to_thread(handler.text_to_speech, text, lang)
    if not mp3_bytes:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TTS service unavailable or failed to generate audio.",
        )

    logger.info(
        "TTS lang=%s bytes=%d latency=%.3fs",
        lang, len(mp3_bytes), time.perf_counter() - t0,
    )
    return Response(content=mp3_bytes, media_type="audio/mpeg")
