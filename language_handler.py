"""
Language handler for bilingual Tamil & English support, including Tanglish
(Tamil written in Roman/English script).

Supported modes:
  'english'   – English only (default)
  'tamil'     – Tamil Unicode script responses
  'bilingual' – Tamil + English mixed (Tanglish-friendly)
"""

import re
import unicodedata


# ---------------------------------------------------------------------------
# Tamil Unicode block: U+0B80 – U+0BFF
# ---------------------------------------------------------------------------
_TAMIL_UNICODE_RANGE = re.compile(r'[\u0B80-\u0BFF]')


# ---------------------------------------------------------------------------
# Tanglish emotion keyword dictionaries
# Tamil words romanised – commonly used in SMS / chat messages.
# ---------------------------------------------------------------------------
TANGLISH_EMOTION_KEYWORDS = {
    'joy': [
        'santhosham', 'santoosham', 'nalla irukken', 'nalla iruken',
        'super', 'makkalu', 'happy pannren', 'happy ah irukken',
        'azhagana', 'arumai', 'romba nalla', 'nallavaru',
        'semma', 'enna vishayam', 'periya santhosham',
    ],
    'sadness': [
        'azhugiren', 'azhugiRen', 'kedachu', 'kedaitu', 'manavanku',
        'dukham', 'vali', 'valikudu', 'valikuthu', 'romba kஷtam',
        'kastam', 'kashtam', 'thaniyaga', 'thaniyaa', 'yaarum illai',
        'romba valikudu', 'dhukam', 'kannu varuthu', 'kaanom',
        'ennaku onnum illai', 'vedikkai', 'niraivu illai',
    ],
    'anger': [
        'kovam', 'ragam', 'kasobu', 'kasappu', 'erichal',
        'erichil', 'kodi', 'pichundu', 'ennaku romba kovam',
        'valikkuthu', 'thittaren', 'thittu', 'pichi',
    ],
    'fear': [
        'bayam', 'bayama', 'bayama iruku', 'prachinnai', 'prachinai',
        'payanam', 'narambhu', 'vilagu', 'atanka', 'aattam',
        'bayangara', 'kakkam', 'latchiyam illai',
    ],
    'anxiety': [
        'tension', 'tensionaa iruku', 'worrying', 'kaalamela',
        'en aagum', 'en pannuvathu', 'thavippu', 'thavikiren',
        'en seivom', 'romba tension', 'mind ah saari', 'saari',
        'thozhil illai', 'vali iruku', 'thalai valikudu',
        'romba stress', 'nerves', 'theriyalai',
    ],
    'crisis': [
        'saaga poiren', 'saaganum', 'saagavendum', 'saavu',
        'velaiyillai vazhka', 'vazhka venam', 'irukka virupu illai',
        'uyir thola poiren', 'suicide pannuven', 'life pochu',
        'maranam', 'maranam thedi', 'vazhkayil nilai illai',
    ],
}

# Tamil Unicode keyword dictionaries (common words in actual Tamil script)
TAMIL_UNICODE_EMOTION_KEYWORDS = {
    'joy': [
        'சந்தோஷம்', 'மகிழ்ச்சி', 'ஆனந்தம்', 'நல்லா இருக்கேன்',
        'சூப்பர்', 'அருமை', 'நன்றாக உள்ளேன்',
    ],
    'sadness': [
        'அழுகிறேன்', 'துக்கம்', 'வலிக்குது', 'வலிக்கிறது',
        'மனவலி', 'தனிமை', 'யாரும் இல்லை', 'கஷ்டம்',
    ],
    'anger': [
        'கோபம்', 'ராகம்', 'எரிச்சல்', 'கோபமாக இருக்கேன்',
    ],
    'fear': [
        'பயம்', 'பயமாக இருக்கு', 'பிரச்சினை', 'அச்சம்',
    ],
    'anxiety': [
        'டென்ஷன்', 'மன அழுத்தம்', 'கவலை', 'கவலையாக உள்ளேன்',
        'தவிக்கிறேன்', 'தவிப்பு',
    ],
    'crisis': [
        'சாகப்போகிறேன்', 'வாழ்க்கை வேண்டாம்', 'தற்கொலை',
        'உயிரை மாய்த்துக்கொள்ள', 'சாவு',
    ],
}


# ---------------------------------------------------------------------------
# Bilingual response templates  (Tamil + English)
# ---------------------------------------------------------------------------
BILINGUAL_RESPONSES = {
    'joy': [
        "நல்லது! 😊 That's wonderful to hear. Hold onto this happy feeling — "
        "நீங்கள் மகிழ்ச்சியாக இருப்பது என்னையும் சந்தோஷப்படுத்துகிறது. 💛",
        "Semma! 🌟 I'm really glad you're feeling good. "
        "இந்த நேர்மறையான உணர்வை கொண்டு செல்லுங்கள்!",
    ],
    'neutral': [
        "நான் இங்கே இருக்கிறேன். I'm here for you — no rush, take your time. "
        "என்ன மனசுல இருக்குன்னு சொல்லுங்க, கேக்கிறேன். 💙",
        "Okay-aa irukku. That's okay too. "
        "நான் கேக்கிறேன் — பேசணும்னா பேசலாம். 💙",
    ],
    'sadness': [
        "Romba valikudu-nu theriyuthu. 💙 I hear you — your sadness is real and valid. "
        "நீங்கள் தனியா இல்லை, நான் இங்கே இருக்கிறேன். 💙",
        "துக்கமா இருக்கீங்களா? I'm so sorry you're feeling this way. "
        "பேசணும்னா பேசலாம் — நான் கேக்கிறேன். 💙",
    ],
    'anger': [
        "கோபம் வருவது இயல்புதான். It's completely okay to feel angry. "
        "என்ன நடந்தது-ன்னு சொல்லுங்க — I'm listening without judgment. 💙",
        "Kovam varuthu-nu theriyuthu. That frustration makes sense. "
        "நான் judge பண்ண மாட்டேன் — சொல்லுங்க. 💙",
    ],
    'fear': [
        "பயமா இருக்கீங்களா? You are not facing this fear alone. "
        "நான் இங்கே இருக்கிறேன் — நீங்கள் தனியா இல்லை. 💙",
        "Bayama iruku-nu theriyuthu. I hear you. "
        "உங்களோட பயம் real-aa இருக்கு, and I care deeply. 💙",
    ],
    'anxiety': [
        "Tension-aa irukka? That overwhelm is real. "
        "மெல்ல மூச்சு விடுங்க — நான் இங்கே இருக்கிறேன். 💙",
        "கவலைப்படாதீங்க — I'm right here with you. "
        "Oru step at a time போலாம். 💙",
    ],
    'crisis': [
        "உங்களுக்கு இப்போது உதவி தேவை. Please reach out to a crisis line immediately — "
        "988-ஐ call/text செய்யுங்கள் (24/7 கிடைக்கும்). "
        "உங்கள் உயிர் மிகவும் மதிப்புமிக்கது. நான் இங்கே இருக்கிறேன். 💙",
    ],
}

# Tamil-only response templates
TAMIL_RESPONSES = {
    'joy': [
        "மிகவும் சந்தோஷமாக இருக்கிறது! 😊 இந்த மகிழ்ச்சியை தொடரட்டும். 💛",
        "நல்லது! உங்கள் சந்தோஷம் என்னையும் மகிழ்விக்கிறது. 🌟",
    ],
    'neutral': [
        "நான் இங்கே இருக்கிறேன். என்ன மனசுல இருக்குன்னு சொல்லுங்க. 💙",
        "சரி, நான் கேட்கிறேன். உங்களுக்கு என்ன உதவி வேண்டும்? 💙",
    ],
    'sadness': [
        "மன்னிக்கவும், நீங்கள் இப்படி உணர்கிறீர்கள் என்பது மிகவும் வருந்துகிறது. "
        "நீங்கள் தனியா இல்லை — நான் இங்கே இருக்கிறேன். 💙",
        "உங்கள் துக்கம் உண்மையானது. நான் கேட்கிறேன், நீங்கள் தனியா இல்லை. 💙",
    ],
    'anger': [
        "கோபப்படுவது இயல்புதான். நான் judge பண்ண மாட்டேன் — சொல்லுங்க. 💙",
        "உங்கள் கோபம் புரிகிறது. என்ன நடந்தது? 💙",
    ],
    'fear': [
        "பயப்பட வேண்டாம் — நான் இங்கே இருக்கிறேன். நீங்கள் தனியா இல்லை. 💙",
        "உங்கள் பயம் உண்மையானது. நான் உங்களோடு இருக்கிறேன். 💙",
    ],
    'anxiety': [
        "கவலைப்படாதீங்க — மெல்ல மூச்சு விடுங்க. நான் இங்கே இருக்கிறேன். 💙",
        "டென்ஷன் ஆகாதீங்க. ஒரு நேரத்தில் ஒரு விஷயமாக பார்ப்போம். 💙",
    ],
    'crisis': [
        "உங்களுக்கு இப்போது உதவி தேவை. உடனடியாக 988-ஐ அழைக்கவும் அல்லது "
        "text செய்யவும் (24 மணி நேரமும் கிடைக்கும்). "
        "உங்கள் உயிர் மிகவும் மதிப்புமிக்கது. நான் இங்கே இருக்கிறேன். 💙",
    ],
}


class LanguageHandler:
    """
    Detects and handles Tamil Unicode, Tanglish, and English text.
    Provides bilingual emotion keyword lookup and response selection.
    """

    SUPPORTED_LANGUAGES = ('english', 'tamil', 'bilingual')
    DEFAULT_LANGUAGE = 'english'

    def __init__(self):
        self._tanglish_flat: dict[str, str] = {}   # keyword → emotion
        self._tamil_flat: dict[str, str] = {}       # keyword → emotion
        self._build_lookup_tables()

    def _build_lookup_tables(self):
        for emotion, words in TANGLISH_EMOTION_KEYWORDS.items():
            for w in words:
                self._tanglish_flat[w.lower()] = emotion
        for emotion, words in TAMIL_UNICODE_EMOTION_KEYWORDS.items():
            for w in words:
                self._tamil_flat[w] = emotion

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------

    def detect_script(self, text: str) -> str:
        """
        Return the dominant script in ``text``.

        Returns
        -------
        'tamil'    – contains Tamil Unicode characters
        'tanglish' – Latin script but matches Tanglish keyword list
        'english'  – default
        """
        if _TAMIL_UNICODE_RANGE.search(text):
            return 'tamil'
        text_lower = text.lower()
        for kw in self._tanglish_flat:
            if kw in text_lower:
                return 'tanglish'
        return 'english'

    def is_tanglish(self, text: str) -> bool:
        return self.detect_script(text) == 'tanglish'

    def is_tamil_unicode(self, text: str) -> bool:
        return self.detect_script(text) == 'tamil'

    # ------------------------------------------------------------------
    # Emotion detection for Tamil / Tanglish
    # ------------------------------------------------------------------

    def detect_tanglish_emotion(self, text: str) -> str | None:
        """
        Return the most severe emotion matched by Tanglish keywords,
        or ``None`` if no match.
        """
        text_lower = text.lower()
        severity_order = ['crisis', 'sadness', 'fear', 'anxiety', 'anger', 'joy']
        matched: dict[str, int] = {}
        for kw, emotion in self._tanglish_flat.items():
            if kw in text_lower:
                matched[emotion] = matched.get(emotion, 0) + 1
        if not matched:
            return None
        # Return by severity
        for emo in severity_order:
            if emo in matched:
                return emo
        return max(matched, key=matched.get)

    def detect_tamil_unicode_emotion(self, text: str) -> str | None:
        """
        Return the most severe emotion matched by Tamil Unicode keywords,
        or ``None`` if no match.
        """
        severity_order = ['crisis', 'sadness', 'fear', 'anxiety', 'anger', 'joy']
        matched: dict[str, int] = {}
        for kw, emotion in self._tamil_flat.items():
            if kw in text:
                matched[emotion] = matched.get(emotion, 0) + 1
        if not matched:
            return None
        for emo in severity_order:
            if emo in matched:
                return emo
        return max(matched, key=matched.get)

    def get_tanglish_keywords_for_emotion(self, emotion: str) -> list[str]:
        """Return the Tanglish keywords for a given emotion."""
        return TANGLISH_EMOTION_KEYWORDS.get(emotion, [])

    def get_tamil_keywords_for_emotion(self, emotion: str) -> list[str]:
        """Return the Tamil Unicode keywords for a given emotion."""
        return TAMIL_UNICODE_EMOTION_KEYWORDS.get(emotion, [])

    # ------------------------------------------------------------------
    # Response selection
    # ------------------------------------------------------------------

    def get_response_pool(self, emotion: str, language_preference: str) -> list[str]:
        """
        Return the response pool for an emotion in the requested language.
        Falls back to English templates if no bilingual/Tamil template exists.
        """
        if language_preference == 'tamil':
            return TAMIL_RESPONSES.get(emotion, [])
        if language_preference == 'bilingual':
            return BILINGUAL_RESPONSES.get(emotion, [])
        return []   # caller falls back to English

    # ------------------------------------------------------------------
    # Greeting helpers
    # ------------------------------------------------------------------

    def get_greeting(self, language_preference: str) -> str:
        greetings = {
            'tamil': (
                "வணக்கம்! 🌟 நான் உங்களுக்கு உதவ இங்கே இருக்கிறேன். "
                "இன்று நீங்கள் எப்படி உணர்கிறீர்கள்?"
            ),
            'bilingual': (
                "வணக்கம் / Hello! 🌟 I'm here to support you. "
                "இன்று நீங்கள் எப்படி உணர்கிறீர்கள்? How are you feeling today?"
            ),
        }
        return greetings.get(language_preference, '')

    # ------------------------------------------------------------------
    # TTS language code helper
    # ------------------------------------------------------------------

    def get_tts_lang_code(self, language_preference: str, detected_script: str) -> str:
        """
        Return the BCP-47 language tag for Google TTS.
        Tamil script → 'ta', bilingual/tanglish → 'ta' for Tamil parts,
        English → 'en'.
        """
        if language_preference == 'tamil' or detected_script == 'tamil':
            return 'ta'
        return 'en'
