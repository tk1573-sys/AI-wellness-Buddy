"""
Voice handler for the AI Wellness Buddy.

Provides:
  - text_to_speech(text, lang) → MP3 bytes  (via gTTS, requires internet)
  - transcribe_audio(wav_bytes, lang_hint)  → str  (via SpeechRecognition)

Both functions return None / empty string gracefully when dependencies are
unavailable or the request fails, so the rest of the app always stays usable.

Audio format support:
  - WAV / AIFF / FLAC: handled natively by SpeechRecognition
  - WebM / MP3 / OGG / MP4: converted to WAV via pydub (requires ffmpeg)
    when pydub is installed; otherwise a warning is logged and an empty
    string is returned so the caller can prompt the user to type instead.
"""

import io
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional import: pydub (for non-WAV format conversion)
# ---------------------------------------------------------------------------
try:
    from pydub import AudioSegment as _AudioSegment  # type: ignore
    _PYDUB_AVAILABLE = True
except ImportError:
    _PYDUB_AVAILABLE = False

# ---------------------------------------------------------------------------
# Optional import: gTTS
# ---------------------------------------------------------------------------
try:
    from gtts import gTTS as _gTTS
    _GTTS_AVAILABLE = True
except ImportError:
    _GTTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Optional import: SpeechRecognition
# ---------------------------------------------------------------------------
try:
    import speech_recognition as _sr
    _SR_AVAILABLE = True
    _RECOGNIZER = _sr.Recognizer()
except ImportError:
    _SR_AVAILABLE = False
    _RECOGNIZER = None


class VoiceHandler:
    """Encapsulates TTS and speech-to-text operations."""

    # Map language preference to BCP-47 tag (used for TTS)
    _LANG_CODES = {
        'english':   'en',
        'tamil':     'ta',
        'bilingual': 'ta',   # Tamil speaker; TTS in Tamil for bilingual
        'tanglish':  'ta',
    }

    # Map language preference to Google STT locale(s).
    # Bilingual / Tanglish: try en-IN first (Tanglish is Latin-script Tamil),
    # then fall back to ta-IN so pure Tamil utterances still work.
    _STT_LOCALES: dict[str, list[str]] = {
        'english':   ['en-IN'],
        'tamil':     ['ta-IN'],
        'bilingual': ['en-IN', 'ta-IN'],  # en-IN first for Tanglish
        'tanglish':  ['en-IN', 'ta-IN'],
    }

    # Magic-byte signatures for audio formats
    _MAGIC_WAV  = b'RIFF'
    _MAGIC_FLAC = b'fLaC'
    _MAGIC_AIFF = b'FORM'
    _MAGIC_OGG  = b'OggS'
    _MAGIC_WEBM = b'\x1a\x45\xdf\xa3'  # EBML header (WebM/MKV)
    _MAGIC_MP3  = (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2', b'ID3')
    _MAGIC_MP4  = b'ftyp'  # at offset 4

    def __init__(self):
        self.tts_available = _GTTS_AVAILABLE
        self.stt_available = _SR_AVAILABLE

    # ------------------------------------------------------------------
    # Text-to-Speech
    # ------------------------------------------------------------------

    def text_to_speech(self, text: str, language_preference: str = 'english') -> bytes | None:
        """
        Convert *text* to MP3 audio bytes using Google TTS.

        Parameters
        ----------
        text : str
            The text to speak.  HTML/Markdown annotations (e.g. ``_(Analysis:…)_``)
            are stripped before synthesis.
        language_preference : str
            User's language preference ('english', 'tamil', 'bilingual').

        Returns
        -------
        bytes
            MP3 audio data, or ``None`` if TTS is unavailable / fails.
        """
        if not _GTTS_AVAILABLE:
            return None

        # Strip Markdown annotations and XAI lines
        clean = _strip_markdown(text)
        if not clean.strip():
            return None

        lang = self._LANG_CODES.get(language_preference, 'en')
        try:
            tts = _gTTS(text=clean, lang=lang, slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            return buf.getvalue()
        except Exception as exc:
            logger.warning("TTS failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Audio format helpers
    # ------------------------------------------------------------------

    def _detect_format(self, audio_bytes: bytes) -> str:
        """Return a best-guess format string ('wav', 'flac', 'aiff', 'webm', 'mp3', 'mp4', 'ogg', 'unknown')."""
        if not audio_bytes or len(audio_bytes) < 12:
            return 'unknown'
        hdr = audio_bytes[:12]
        if hdr[:4] == self._MAGIC_WAV:
            return 'wav'
        if hdr[:4] == self._MAGIC_FLAC:
            return 'flac'
        if hdr[:4] == self._MAGIC_AIFF:
            return 'aiff'
        if hdr[:4] == self._MAGIC_OGG:
            return 'ogg'
        if hdr[:4] == self._MAGIC_WEBM:
            return 'webm'
        if hdr[4:8] == self._MAGIC_MP4:
            return 'mp4'
        for sig in self._MAGIC_MP3:
            if hdr[:len(sig)] == sig:
                return 'mp3'
        return 'unknown'

    def _to_wav_bytes(self, audio_bytes: bytes, src_format: str) -> bytes | None:
        """
        Convert *audio_bytes* to WAV using pydub (requires ffmpeg).

        Returns ``None`` when conversion is not possible.
        """
        if not _PYDUB_AVAILABLE:
            logger.warning(
                "pydub is not installed — cannot convert %s audio to WAV. "
                "Install pydub and ffmpeg for WebM/MP3 support.",
                src_format,
            )
            return None
        try:
            seg = _AudioSegment.from_file(io.BytesIO(audio_bytes), format=src_format)
            buf = io.BytesIO()
            seg.export(buf, format='wav')
            return buf.getvalue()
        except Exception as exc:
            logger.warning("Audio conversion (%s → wav) failed: %s", src_format, exc)
            return None

    # ------------------------------------------------------------------
    # Speech-to-Text
    # ------------------------------------------------------------------

    def transcribe_audio(self, audio_bytes: bytes,
                         language_preference: str = 'english') -> str:
        """
        Transcribe audio bytes to text using Google Speech Recognition.

        Supports WAV, AIFF, and FLAC natively.  WebM, MP3, MP4, and OGG are
        converted to WAV via pydub when pydub + ffmpeg are installed.

        For the ``bilingual`` / ``tanglish`` preference, recognition is first
        attempted with ``en-IN`` (Tanglish / Latin-script Tamil) and then with
        ``ta-IN`` as a fallback so pure Tamil utterances are also captured.

        Parameters
        ----------
        audio_bytes : bytes
            Raw audio from the browser microphone or audio_recorder_streamlit.
        language_preference : str
            Hints the recognition locale(s).

        Returns
        -------
        str
            Transcribed text, or empty string when recognition fails.
        """
        if not _SR_AVAILABLE or not audio_bytes:
            return ''

        locales = self._STT_LOCALES.get(language_preference, ['en-IN'])

        # Detect and (if necessary) convert audio format
        fmt = self._detect_format(audio_bytes)
        logger.debug("STT audio format detected: %s", fmt)

        if fmt not in ('wav', 'flac', 'aiff'):
            if fmt == 'unknown':
                # Assume WAV — audio_recorder_streamlit may omit RIFF header
                # details on some browsers; let SpeechRecognition try anyway.
                logger.debug("Unknown audio format; attempting WAV parse.")
            else:
                converted = self._to_wav_bytes(audio_bytes, fmt)
                if converted is None:
                    logger.warning(
                        "Cannot transcribe %s audio without pydub+ffmpeg.", fmt
                    )
                    return ''
                audio_bytes = converted
                fmt = 'wav'

        return self._recognize_with_fallback(audio_bytes, locales)

    def _recognize_with_fallback(self, wav_bytes: bytes, locales: list[str]) -> str:
        """
        Try Google STT with each locale in *locales* and return the first
        non-empty result.  Returns empty string if all attempts fail.
        """
        for locale in locales:
            result = self._recognize_once(wav_bytes, locale)
            if result:
                logger.debug("STT succeeded with locale=%s", locale)
                return result
        return ''

    def _recognize_once(self, wav_bytes: bytes, locale: str) -> str:
        """Attempt recognition with a single locale. Returns '' on failure."""
        try:
            audio_file = io.BytesIO(wav_bytes)
            with _sr.AudioFile(audio_file) as source:
                audio = _RECOGNIZER.record(source)
            return _RECOGNIZER.recognize_google(audio, language=locale)
        except _sr.UnknownValueError:
            logger.debug("STT: could not understand audio (locale=%s)", locale)
            return ''
        except _sr.RequestError as exc:
            logger.warning("STT request failed (locale=%s): %s", locale, exc)
            return ''
        except Exception as exc:
            logger.warning("STT unexpected error (locale=%s): %s", locale, exc)
            return ''


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_markdown(text: str) -> str:
    """Remove Markdown annotations and XAI lines from a response string."""
    import re
    # Remove XAI annotation lines: _(Analysis: …)_  — uses non-backtracking pattern
    text = re.sub(r'_\(Analysis:[^)]*\)_', '', text)
    # Remove bold **…**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove italic _…_ or *…*
    text = re.sub(r'[_*](.*?)[_*]', r'\1', text)
    # Remove emoji characters that gTTS might stumble over (keep Unicode letters)
    text = re.sub(r'[^\w\s\u0B80-\u0BFF.,!?\'\"—–\-]', '', text)
    # Collapse multiple spaces / blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
