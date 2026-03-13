"""
Voice handler for the AI Wellness Buddy.

Provides:
  - text_to_speech(text, lang) → MP3 bytes  (via gTTS, requires internet)
  - transcribe_audio(wav_bytes, lang_hint)  → str  (via SpeechRecognition)

Both functions return None / empty string gracefully when dependencies are
unavailable or the request fails, so the rest of the app always stays usable.
"""

import io
import logging

logger = logging.getLogger(__name__)

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

    # Map language preference to BCP-47 tag
    _LANG_CODES = {
        'english':   'en',
        'tamil':     'ta',
        'bilingual': 'ta',   # Tamil speaker; TTS in Tamil for bilingual
        'tanglish':  'ta',
    }

    # Map BCP-47 tag to Google STT locale
    _STT_LOCALE = {
        'en': 'en-IN',   # Indian English preferred for Tanglish users
        'ta': 'ta-IN',   # Tamil (India)
    }

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
    # Speech-to-Text
    # ------------------------------------------------------------------

    def transcribe_audio(self, audio_bytes: bytes,
                         language_preference: str = 'english') -> str:
        """
        Transcribe WAV audio bytes to text using Google Speech Recognition.

        Parameters
        ----------
        audio_bytes : bytes
            Raw WAV audio from the browser microphone.
        language_preference : str
            Hints the recognition locale.

        Returns
        -------
        str
            Transcribed text.  Returns empty string when:
            - ``audio_bytes`` is empty or ``None``
            - ``SpeechRecognition`` is not installed (``stt_available`` is False)
            - The audio cannot be understood
            - The Google STT service request fails
        """
        if not _SR_AVAILABLE or not audio_bytes:
            return ''

        lang_code = self._LANG_CODES.get(language_preference, 'en')
        locale = self._STT_LOCALE.get(lang_code, 'en-IN')

        try:
            audio_file = io.BytesIO(audio_bytes)
            with _sr.AudioFile(audio_file) as source:
                audio = _RECOGNIZER.record(source)
            return _RECOGNIZER.recognize_google(audio, language=locale)
        except _sr.UnknownValueError:
            logger.debug("STT: could not understand audio")
            return ''
        except _sr.RequestError as exc:
            logger.warning("STT request failed: %s", exc)
            return ''
        except Exception as exc:
            logger.warning("STT unexpected error: %s", exc)
            return ''


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_markdown(text: str) -> str:
    """Remove Markdown annotations and XAI lines from a response string."""
    import re
    # Remove XAI annotation lines: _(Analysis: …)_
    text = re.sub(r'_\(Analysis:.*?\)_', '', text, flags=re.DOTALL)
    # Remove bold **…**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove italic _…_ or *…*
    text = re.sub(r'[_*](.*?)[_*]', r'\1', text)
    # Remove emoji characters that gTTS might stumble over (keep Unicode letters)
    text = re.sub(r'[^\w\s\u0B80-\u0BFF.,!?\'\"—–\-]', '', text)
    # Collapse multiple spaces / blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
