"""
Reusable HTML layout components for AI Wellness Buddy.

Each function returns an HTML string that can be injected with
``st.markdown(html, unsafe_allow_html=True)``.  Keeping them here
ensures consistency and makes the main ``ui_app.py`` easier to read.
"""

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------

EMO_ICONS = {
    'joy': '😊', 'positive': '😊', 'neutral': '😐',
    'sadness': '😢', 'negative': '😟', 'anger': '😠',
    'fear': '😰', 'anxiety': '😰',
    'crisis': '🆘', 'distress': '🆘',
}

EMO_BUBBLE_CLASS = {
    'joy': 'emo-joy', 'positive': 'emo-joy',
    'neutral': 'emo-neutral',
    'sadness': 'emo-sadness', 'negative': 'emo-sadness',
    'anger': 'emo-anger',
    'fear': 'emo-anxiety', 'anxiety': 'emo-anxiety',
    'crisis': 'emo-crisis', 'distress': 'emo-crisis',
}

RISK_COLOUR = {
    'low':      '🟢',
    'medium':   '🟡',
    'high':     '🔴',
    'critical': '🚨',
}

RISK_LEVEL_VALUES = {'low': 0.10, 'medium': 0.35, 'high': 0.65, 'critical': 0.90}

SOUND_LABELS = {
    'deep_focus': 'Deep Focus',
    'calm_waves': 'Calm Waves',
    'soft_rain': 'Soft Rain',
    'white_noise': 'White Noise',
}

LANG_ICONS = {'english': '🇬🇧', 'tamil': '🇮🇳', 'bilingual': '🇮🇳🇬🇧'}

# Badge styling keyed by risk level → (icon, colour, bg, shadow)
_BADGE_STYLE = {
    'low':      ('🟢', '#5B8CFF', 'rgba(91,140,255,0.10)', 'rgba(91,140,255,0.25)'),
    'medium':   ('🟡', '#FFB74D', 'rgba(255,183,77,0.10)', 'rgba(255,183,77,0.25)'),
    'high':     ('🔴', '#EF5350', 'rgba(239,83,80,0.10)', 'rgba(239,83,80,0.25)'),
    'critical': ('🚨', '#D32F2F', 'rgba(211,47,47,0.12)', 'rgba(211,47,47,0.30)'),
}

# Risk accent colours for the header bar
_RISK_ACCENT = {
    'low': '#5B8CFF', 'medium': '#FFB74D', 'high': '#EF5350', 'critical': '#D32F2F',
}


# -----------------------------------------------------------------------
# Landing / hero
# -----------------------------------------------------------------------

def render_hero_section() -> str:
    """Return HTML for the landing-page hero (logo + title + tagline)."""
    return (
        '<div class="landing-hero">'
        '<div class="hero-logo-glow"></div>'
        '<div class="hero-logo">🌟</div>'
        '<h1 class="hero-title">AI Wellness Buddy</h1>'
        '<p class="hero-tagline">A Safe Space for Emotional Support</p>'
        '</div>'
    )


def render_wellness_illustration() -> str:
    """Return SVG wellness illustration for the landing page."""
    return (
        '<div class="illustration-panel">'
        '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" class="wellness-art">'
        '<defs>'
        '<linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" style="stop-color:#5B8CFF;stop-opacity:0.3"/>'
        '<stop offset="100%" style="stop-color:#9B8CFF;stop-opacity:0.3"/>'
        '</linearGradient>'
        '<linearGradient id="g2" x1="0%" y1="100%" x2="100%" y2="0%">'
        '<stop offset="0%" style="stop-color:#4DD0E1;stop-opacity:0.25"/>'
        '<stop offset="100%" style="stop-color:#FF8A65;stop-opacity:0.2"/>'
        '</linearGradient>'
        '</defs>'
        '<circle cx="100" cy="100" r="80" fill="url(#g1)" class="art-circle-outer"/>'
        '<circle cx="100" cy="100" r="50" fill="url(#g2)" class="art-circle-inner"/>'
        '<circle cx="100" cy="100" r="24" fill="rgba(155,140,255,0.18)" class="art-circle-core"/>'
        '<path d="M100 40 Q130 70 100 100 Q70 130 100 160 Q130 130 100 100 Q70 70 100 40Z" '
        'fill="rgba(91,140,255,0.12)" class="art-leaf"/>'
        '<circle cx="60" cy="60" r="6" fill="rgba(77,208,225,0.3)" class="art-dot art-dot-1"/>'
        '<circle cx="140" cy="70" r="4" fill="rgba(155,140,255,0.3)" class="art-dot art-dot-2"/>'
        '<circle cx="50" cy="140" r="5" fill="rgba(255,138,101,0.25)" class="art-dot art-dot-3"/>'
        '<circle cx="150" cy="135" r="3" fill="rgba(91,140,255,0.3)" class="art-dot art-dot-4"/>'
        '</svg>'
        '</div>'
    )


# -----------------------------------------------------------------------
# Chat header bar
# -----------------------------------------------------------------------

def render_chat_header(*, accent_color: str = '#5B8CFF',
                       emo_icon: str = '😊',
                       streak: int = 0) -> str:
    """Return HTML for the animated chat header bar."""
    accent = _RISK_ACCENT.get(accent_color, accent_color)  # accept risk-level or raw color
    streak_badge = ''
    if streak >= 7:
        streak_badge = f'<span class="streak-badge streak-fire">🔥 {streak}</span>'
    elif streak >= 3:
        streak_badge = f'<span class="streak-badge streak-warm">⭐ {streak}</span>'
    elif streak >= 1:
        streak_badge = f'<span class="streak-badge">💫 {streak}</span>'
    return (
        f'<div class="chat-header-bar" style="border-top:3px solid {accent};">'
        f'<span class="header-title">🌟 AI Wellness Buddy</span>'
        f'<span class="header-right">'
        f'<span class="emo-state-icon">{emo_icon}</span>'
        f'{streak_badge}'
        f'</span>'
        f'</div>'
    )


# -----------------------------------------------------------------------
# Sidebar components
# -----------------------------------------------------------------------

def render_user_avatar(user_id: str) -> str:
    """Gradient circle avatar with initials."""
    initials = user_id[0].upper() if user_id else '?'
    return (
        f'<div style="text-align:center;margin-bottom:0.75rem;">'
        f'<div style="width:72px;height:72px;border-radius:50%;'
        f'background:linear-gradient(135deg,#5B8CFF,#9B8CFF);'
        f'display:inline-flex;align-items:center;justify-content:center;'
        f'font-size:1.8rem;color:#fff;font-weight:700;letter-spacing:0.5px;'
        f'box-shadow:0 6px 20px rgba(91,140,255,0.35);'
        f'border:3px solid rgba(255,255,255,0.6);">{initials}</div>'
        f'<p style="margin:0.5rem 0 0;font-weight:600;font-size:1.1rem;'
        f'color:#334155;">{user_id}</p></div>'
    )


def render_risk_badge(risk_level: str = 'low') -> str:
    """Colour-coded risk badge."""
    r_icon, r_color, r_bg, r_shadow = _BADGE_STYLE.get(risk_level, _BADGE_STYLE['low'])
    return (
        f'<div style="text-align:center;padding:0.6rem 0.75rem;border-radius:0.75rem;'
        f'background:{r_bg};border:1px solid {r_color};margin-bottom:0.75rem;'
        f'box-shadow:0 2px 12px {r_shadow};backdrop-filter:blur(6px);'
        f'transition:all 0.3s ease;">'
        f'<span style="font-size:1.15rem;font-weight:600;">{r_icon} Risk: '
        f'<strong style="color:{r_color};">{risk_level.upper()}</strong></span></div>'
    )


def render_session_info_card(session_number: int, lang_pref: str,
                             msg_count: int = 0) -> str:
    """Compact card showing session #, language, and message count."""
    lang_icon = LANG_ICONS.get(lang_pref, '🌐')
    return (
        f'<div style="padding:0.5rem 0.75rem;border-radius:0.6rem;'
        f'background:rgba(255,255,255,0.55);backdrop-filter:blur(8px);'
        f'border:1px solid rgba(255,255,255,0.3);margin-bottom:0.5rem;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.03);">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<span style="font-size:0.88rem;color:#475569;">📅 Session #{session_number}</span>'
        f'<span style="font-size:0.88rem;color:#475569;">'
        f'{lang_icon} {lang_pref.capitalize()}</span>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.3rem;">'
        f'<span style="font-size:0.78rem;color:#64748B;">💬 {msg_count} messages</span>'
        f'</div>'
        f'</div>'
    )


def render_streak_card(streak: int) -> str:
    """Streak display card with emoji and label."""
    streak_emoji = "🔥" if streak >= 3 else "⭐" if streak >= 1 else "💤"
    streak_label = (
        "on fire!" if streak >= 7
        else "growing!" if streak >= 3
        else "building" if streak >= 1
        else "start today"
    )
    return (
        f'<div style="text-align:center;padding:0.65rem 0.75rem;border-radius:0.75rem;'
        f'background:linear-gradient(135deg,rgba(77,208,225,0.10),rgba(155,140,255,0.10));'
        f'border:1px solid rgba(155,140,255,0.15);'
        f'box-shadow:0 2px 10px rgba(77,208,225,0.08);margin:0.5rem 0 0.75rem;">'
        f'<span style="font-size:1.6rem;">{streak_emoji}</span><br>'
        f'<strong style="font-size:1.2rem;color:#334155;">{streak}</strong>'
        f'<span style="font-size:0.85rem;color:#64748B;margin-left:0.25rem;">'
        f'positive streak</span><br>'
        f'<span style="font-size:0.75rem;color:#9B8CFF;font-style:italic;">'
        f'{streak_label}</span></div>'
    )


# -----------------------------------------------------------------------
# Calm mode / ambient
# -----------------------------------------------------------------------

def render_waveform_section(sound_key: str) -> str:
    """Return waveform bars + sound label for calm mode."""
    label = SOUND_LABELS.get(sound_key, 'Ambient')
    bars = '<span class="waveform-bar"></span>' * 8
    return (
        '<div class="calm-active-bg"></div>'
        '<div style="text-align:center;margin:0.25rem 0 0.5rem;">'
        f'<div class="waveform-vis">{bars}</div>'
        f'<span style="font-size:0.72rem;color:#9B8CFF;letter-spacing:0.04em;">'
        f'🎵 {label}</span>'
        '</div>'
    )


# -----------------------------------------------------------------------
# Session summary card
# -----------------------------------------------------------------------

def render_session_summary_card(*, dominant_emotion: str = 'neutral',
                                message_count: int = 0,
                                risk_level: str = 'low',
                                streak: int = 0) -> str:
    """Animated end-of-session summary card."""
    emo_icon = EMO_ICONS.get(dominant_emotion, '😐')
    risk_icon = RISK_COLOUR.get(risk_level, '⬜')
    return (
        '<div class="session-summary-card">'
        '<h3 style="margin:0 0 0.75rem;">Session Complete ✨</h3>'
        f'<div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;">'
        f'<div>'
        f'<span style="font-size:2rem;">{emo_icon}</span><br>'
        f'<span style="font-size:0.85rem;color:#64748B;">Dominant Emotion</span><br>'
        f'<strong>{dominant_emotion.capitalize()}</strong>'
        f'</div>'
        f'<div>'
        f'<span style="font-size:2rem;">💬</span><br>'
        f'<span style="font-size:0.85rem;color:#64748B;">Messages</span><br>'
        f'<strong>{message_count}</strong>'
        f'</div>'
        f'<div>'
        f'<span style="font-size:2rem;">{risk_icon}</span><br>'
        f'<span style="font-size:0.85rem;color:#64748B;">Risk Level</span><br>'
        f'<strong>{risk_level.capitalize()}</strong>'
        f'</div>'
        f'<div>'
        f'<span style="font-size:2rem;">🔥</span><br>'
        f'<span style="font-size:0.85rem;color:#64748B;">Mood Streak</span><br>'
        f'<strong>{streak}</strong>'
        f'</div>'
        f'</div>'
        '</div>'
    )


# -----------------------------------------------------------------------
# Emotion-reactive CSS flag
# -----------------------------------------------------------------------

def render_emotion_flag(dominant_emotion: str) -> str:
    """Hidden div that triggers CSS sibling selectors for emotion-reactive
    assistant bubble colours."""
    emo_class = EMO_BUBBLE_CLASS.get(dominant_emotion, 'emo-neutral')
    return f'<div class="emo-reactive-flag {emo_class}" style="display:none;"></div>'


# -----------------------------------------------------------------------
# Dynamic emotional avatar
# -----------------------------------------------------------------------

# Extended avatar mapping with animation hints
_AVATAR_MAP = {
    'joy':      ('😊', '#4DD0E1', 'avatarBounce'),
    'positive': ('😊', '#4DD0E1', 'avatarBounce'),
    'neutral':  ('😐', '#9B8CFF', 'avatarGlow'),
    'sadness':  ('😢', '#5B8CFF', 'avatarGlow'),
    'negative': ('😟', '#5B8CFF', 'avatarGlow'),
    'anger':    ('😠', '#EF5350', 'avatarPulse'),
    'fear':     ('😰', '#FFB74D', 'avatarPulse'),
    'anxiety':  ('😟', '#FFB74D', 'avatarPulse'),
    'stress':   ('😓', '#FF8A65', 'avatarPulse'),
    'crisis':   ('⚠️', '#D32F2F', 'avatarPulse'),
    'distress': ('⚠️', '#D32F2F', 'avatarPulse'),
}


def render_emotional_avatar(emotion: str = 'neutral') -> str:
    """Return HTML for a dynamic emotional avatar with glow and animation.

    The avatar changes icon and colour based on the detected emotion,
    and includes a subtle CSS animation.
    """
    icon, color, anim = _AVATAR_MAP.get(emotion, _AVATAR_MAP['neutral'])
    label = emotion.capitalize() if emotion in _AVATAR_MAP else 'Neutral'
    return (
        f'<div class="emotional-avatar" style="--avatar-color:{color};">'
        f'<div class="avatar-glow" style="background:radial-gradient(circle,{color}33 0%,transparent 70%);"></div>'
        f'<span class="avatar-icon {anim}">{icon}</span>'
        f'<span class="avatar-label">{label}</span>'
        f'</div>'
    )


# -----------------------------------------------------------------------
# Enhanced wellness illustration (larger SVG)
# -----------------------------------------------------------------------

def render_wellness_illustration_large() -> str:
    """Return a larger, more detailed SVG wellness illustration.

    Includes floating circles, leaves, soft shapes, and abstract
    wellness visuals suitable for the landing page hero section.
    """
    return (
        '<div class="illustration-panel-large">'
        '<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" class="wellness-art-large">'
        '<defs>'
        '<linearGradient id="gl1" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" style="stop-color:#5B8CFF;stop-opacity:0.25"/>'
        '<stop offset="100%" style="stop-color:#9B8CFF;stop-opacity:0.25"/>'
        '</linearGradient>'
        '<linearGradient id="gl2" x1="0%" y1="100%" x2="100%" y2="0%">'
        '<stop offset="0%" style="stop-color:#4DD0E1;stop-opacity:0.2"/>'
        '<stop offset="100%" style="stop-color:#FF8A65;stop-opacity:0.15"/>'
        '</linearGradient>'
        '<radialGradient id="gr1" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" style="stop-color:#9B8CFF;stop-opacity:0.2"/>'
        '<stop offset="100%" style="stop-color:transparent"/>'
        '</radialGradient>'
        '</defs>'
        # Outer rings
        '<circle cx="150" cy="150" r="130" fill="none" stroke="url(#gl1)" '
        'stroke-width="1" opacity="0.4" class="art-ring art-ring-1"/>'
        '<circle cx="150" cy="150" r="105" fill="url(#gl1)" class="art-circle-outer"/>'
        '<circle cx="150" cy="150" r="70" fill="url(#gl2)" class="art-circle-inner"/>'
        '<circle cx="150" cy="150" r="35" fill="rgba(155,140,255,0.18)" class="art-circle-core"/>'
        # Heart/leaf motif
        '<path d="M150 60 Q190 100 150 150 Q110 200 150 240 Q190 200 150 150 Q110 100 150 60Z" '
        'fill="rgba(91,140,255,0.10)" class="art-leaf"/>'
        '<path d="M100 100 Q130 80 150 100 Q170 80 200 100 Q200 140 150 180 Q100 140 100 100Z" '
        'fill="rgba(239,83,80,0.06)" class="art-heart"/>'
        # Decorative floating dots
        '<circle cx="70" cy="70" r="8" fill="rgba(77,208,225,0.3)" class="art-dot art-dot-1"/>'
        '<circle cx="230" cy="80" r="5" fill="rgba(155,140,255,0.3)" class="art-dot art-dot-2"/>'
        '<circle cx="55" cy="220" r="6" fill="rgba(255,138,101,0.25)" class="art-dot art-dot-3"/>'
        '<circle cx="245" cy="210" r="4" fill="rgba(91,140,255,0.3)" class="art-dot art-dot-4"/>'
        '<circle cx="120" cy="40" r="3" fill="rgba(77,208,225,0.25)" class="art-dot art-dot-1"/>'
        '<circle cx="200" cy="260" r="5" fill="rgba(155,140,255,0.2)" class="art-dot art-dot-3"/>'
        # Small leaf shapes
        '<path d="M70 180 Q85 165 90 185 Q75 195 70 180Z" fill="rgba(77,208,225,0.15)" class="art-mini-leaf"/>'
        '<path d="M220 120 Q235 105 240 125 Q225 135 220 120Z" fill="rgba(155,140,255,0.15)" class="art-mini-leaf"/>'
        '</svg>'
        '</div>'
    )
