"""
Theme engine for AI Wellness Buddy.

Generates the complete CSS stylesheet based on runtime configuration
(dark mode, UI theme variant, risk level).  All CSS variables are
computed here so that the rest of the UI code can remain style-agnostic.
"""


# -----------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------

def get_theme_css(*, dark_mode: bool = False, ui_theme: str = 'calm',
                  risk_level: str = 'low') -> str:
    """Return the full CSS stylesheet as a string.

    Parameters
    ----------
    dark_mode : bool
        Whether dark mode is active.
    ui_theme : str
        One of ``'calm'``, ``'clinical'``, ``'modern'``.
    risk_level : str
        One of ``'low'``, ``'medium'``, ``'high'``, ``'critical'``.
    """
    tv = _theme_vars(dark_mode, ui_theme)
    rv = _risk_vars(risk_level)
    critical_bar = _critical_bar_css() if risk_level == 'critical' else ''
    return _BASE_CSS.format(**tv, **rv, critical_bar_css=critical_bar)


# -----------------------------------------------------------------------
# Theme variable helpers
# -----------------------------------------------------------------------

_LIGHT_THEMES = {
    'calm': 'linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 25%, #fff5f0 50%, #f0fffe 75%, #f0f4ff 100%)',
    'clinical': 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #f8fafc 100%)',
    'modern': 'linear-gradient(135deg, #ede9fe 0%, #e0f2fe 25%, #fce7f3 50%, #e0f2fe 75%, #ede9fe 100%)',
}


def _theme_vars(dark: bool, theme: str) -> dict:
    if dark:
        return dict(
            bg_gradient='linear-gradient(135deg, #0f172a 0%, #1e1b4b 25%, #1a1a2e 50%, #0f172a 75%, #1e1b4b 100%)',
            card_bg='rgba(30,27,75,0.60)',
            card_border='rgba(91,140,255,0.15)',
            text_primary='#e2e8f0',
            text_secondary='#94a3b8',
            text_heading='#f1f5f9',
            sidebar_bg='linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(30,27,75,0.95) 100%)',
            form_bg='rgba(30,27,75,0.65)',
            input_bg='rgba(30,27,75,0.80)',
            particle_color='rgba(91,140,255,0.06)',
            h4_color='#cbd5e1',
        )
    return dict(
        bg_gradient=_LIGHT_THEMES.get(theme, _LIGHT_THEMES['calm']),
        card_bg='rgba(255,255,255,0.65)',
        card_border='rgba(255,255,255,0.35)',
        text_primary='#475569',
        text_secondary='#64748B',
        text_heading='#1e293b',
        sidebar_bg='linear-gradient(180deg, rgba(91,140,255,0.05) 0%, rgba(155,140,255,0.05) 50%, rgba(77,208,225,0.03) 100%)',
        form_bg='rgba(255,255,255,0.60)',
        input_bg='rgba(255,255,255,0.75)',
        particle_color='rgba(91,140,255,0.04)',
        h4_color='#334155',
    )


_RISK_GLOW = {
    'low':      'rgba(91,140,255,0.18)',
    'medium':   'rgba(255,183,77,0.22)',
    'high':     'rgba(239,83,80,0.18)',
    'critical': 'rgba(211,47,47,0.28)',
}
_RISK_BORDER = {
    'low':      'transparent',
    'medium':   'rgba(255,183,77,0.4)',
    'high':     'rgba(239,83,80,0.45)',
    'critical': '#D32F2F',
}


def _risk_vars(risk_level: str) -> dict:
    return dict(
        glow_color=_RISK_GLOW.get(risk_level, _RISK_GLOW['low']),
        border_color=_RISK_BORDER.get(risk_level, 'transparent'),
    )


def _critical_bar_css() -> str:
    return """
    .main::before {
        content: '🚨 CRITICAL — Please reach out for support';
        display: block;
        text-align: center;
        padding: 0.5rem;
        background: linear-gradient(90deg, #D32F2F, #EF5350, #D32F2F);
        color: #fff;
        font-weight: 700;
        font-size: 0.9rem;
        animation: pulse-bar 1.5s ease-in-out infinite;
        border-radius: 0 0 0.5rem 0.5rem;
    }
    @keyframes pulse-bar {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    """


# -----------------------------------------------------------------------
# Master CSS template — uses {variable} placeholders filled at runtime
# -----------------------------------------------------------------------

_BASE_CSS = """
<style>
/* ---- Google Font ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ---- Animated gradient background ---- */
@keyframes gradientBG {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
.stApp {{
    background: {bg_gradient};
    background-size: 400% 400%;
    animation: gradientBG 20s ease infinite;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

/* ---- Floating particles (pure CSS) ---- */
.stApp::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        radial-gradient(2px 2px at 20% 30%, {particle_color}, transparent),
        radial-gradient(2px 2px at 40% 70%, {particle_color}, transparent),
        radial-gradient(2px 2px at 60% 40%, {particle_color}, transparent),
        radial-gradient(2px 2px at 80% 60%, {particle_color}, transparent),
        radial-gradient(3px 3px at 10% 80%, {particle_color}, transparent),
        radial-gradient(3px 3px at 70% 20%, {particle_color}, transparent),
        radial-gradient(2px 2px at 50% 50%, {particle_color}, transparent),
        radial-gradient(2px 2px at 90% 90%, {particle_color}, transparent);
    background-size: 200% 200%;
    animation: particleDrift 30s linear infinite;
}}
@keyframes particleDrift {{
    0%   {{ background-position: 0% 0%; }}
    50%  {{ background-position: 100% 100%; }}
    100% {{ background-position: 0% 0%; }}
}}

/* ---- Premium typography hierarchy ---- */
h1, h2, h3 {{ color: {text_heading}; letter-spacing: -0.02em; font-weight: 700; }}
h4 {{ color: {h4_color}; font-weight: 600; letter-spacing: -0.01em; }}
p, li, span {{ color: {text_primary}; }}
.stCaption, caption {{ color: {text_secondary}; letter-spacing: 0.02em; text-transform: uppercase; font-size: 0.72rem; }}

/* ---- Glassmorphism chat cards — depth layered ---- */
.stChatMessage {{
    padding: 1.1rem 1.3rem;
    border-radius: 1.25rem;
    background: {card_bg};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {card_border};
    box-shadow: 0 4px 24px {glow_color}, inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 0.8rem;
    animation: fadeSlideIn 0.45s cubic-bezier(0.22,1,0.36,1);
    transition: box-shadow 0.3s ease, transform 0.3s ease;
    position: relative;
    z-index: 1;
}}
.stChatMessage:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 32px {glow_color};
}}
@keyframes fadeSlideIn {{
    from {{ opacity: 0; transform: translateY(16px) scale(0.98); }}
    to   {{ opacity: 1; transform: translateY(0) scale(1); }}
}}

/* ---- User vs assistant message distinction ---- */
.stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    border-left: 3px solid #5B8CFF;
}}
.stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    border-left: 3px solid #9B8CFF;
}}

/* ---- Typing indicator animation ---- */
.typing-indicator {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 0;
}}
.typing-indicator span {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #9B8CFF;
    animation: typingBounce 1.2s ease-in-out infinite;
    box-shadow: 0 0 6px rgba(155,140,255,0.4);
}}
.typing-indicator span:nth-child(2) {{ animation-delay: 0.15s; }}
.typing-indicator span:nth-child(3) {{ animation-delay: 0.3s; }}
@keyframes typingBounce {{
    0%, 60%, 100% {{ transform: translateY(0); opacity: 0.4; }}
    30% {{ transform: translateY(-8px); opacity: 1; }}
}}

/* ---- AI responding glow ---- */
@keyframes assistantGlow {{
    0%, 100% {{ box-shadow: 0 0 12px rgba(155,140,255,0.15); }}
    50% {{ box-shadow: 0 0 24px rgba(155,140,255,0.30); }}
}}
.typing-indicator {{
    animation: assistantGlow 2s ease-in-out infinite;
    border-radius: 1rem;
    padding: 8px 12px;
}}

/* ---- Premium chat input bar ---- */
[data-testid="stChatInput"] {{
    background: {input_bg} !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 1.25rem !important;
    border: 1px solid rgba(91,140,255,0.18) !important;
    box-shadow: 0 4px 28px rgba(91,140,255,0.10);
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: #5B8CFF !important;
    box-shadow: 0 4px 32px rgba(91,140,255,0.20);
}}
[data-testid="stChatInput"] textarea {{
    font-size: 0.98rem;
    color: {text_primary};
}}
/* Send button ripple glow */
[data-testid="stChatInput"] button {{
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-radius: 50%;
}}
[data-testid="stChatInput"] button:hover {{
    transform: scale(1.12);
    box-shadow: 0 0 16px rgba(91,140,255,0.4);
}}
[data-testid="stChatInput"] button:active {{
    transform: scale(0.95);
    box-shadow: 0 0 24px rgba(91,140,255,0.5);
}}

/* ---- Sidebar polish ---- */
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.5rem;
    background: {sidebar_bg};
}}
section[data-testid="stSidebar"] .stMarkdown p {{
    font-size: 0.9rem;
    color: {text_primary};
}}

/* ---- Tab labels with slide transition ---- */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.25rem;
}}
.stTabs [data-baseweb="tab"] {{
    font-weight: 600;
    font-size: 0.95rem;
    border-radius: 0.5rem 0.5rem 0 0;
    padding: 0.6rem 1rem;
    transition: color 0.3s ease, background 0.3s ease, box-shadow 0.3s ease, transform 0.2s ease;
    letter-spacing: 0.01em;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: #5B8CFF;
    background: rgba(91,140,255,0.06);
    box-shadow: 0 -2px 10px rgba(91,140,255,0.10);
    transform: translateY(-1px);
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    box-shadow: 0 -2px 14px rgba(91,140,255,0.14);
}}
/* Tab content slide */
.stTabs [data-baseweb="tab-panel"] {{
    animation: tabSlideIn 0.35s ease-out;
}}
@keyframes tabSlideIn {{
    from {{ opacity: 0; transform: translateX(12px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}

/* ---- Metric cards — glassmorphism with hover tilt ---- */
[data-testid="stMetric"] {{
    background: {card_bg};
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 0.75rem;
    padding: 0.8rem;
    border: 1px solid {card_border};
    box-shadow: 0 2px 16px rgba(0,0,0,0.04);
    transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), box-shadow 0.3s ease;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-3px) perspective(600px) rotateX(1deg);
    box-shadow: 0 8px 28px rgba(91,140,255,0.14);
}}

/* ---- Button hover glow ---- */
.stButton > button {{
    border-radius: 0.5rem;
    transition: all 0.3s cubic-bezier(0.22,1,0.36,1);
    border: 1px solid rgba(91,140,255,0.2);
    font-weight: 500;
    letter-spacing: 0.01em;
    position: relative;
    overflow: hidden;
}}
.stButton > button:hover {{
    box-shadow: 0 0 20px rgba(91,140,255,0.28);
    border-color: #5B8CFF;
    transform: translateY(-2px);
}}
.stButton > button:active {{
    transform: translateY(0);
    box-shadow: 0 0 8px rgba(91,140,255,0.15);
}}
.stButton > button::after {{
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    width: 0; height: 0;
    border-radius: 50%;
    background: rgba(91,140,255,0.15);
    transform: translate(-50%, -50%);
    transition: width 0.4s ease, height 0.4s ease;
}}
.stButton > button:active::after {{
    width: 200px;
    height: 200px;
}}

/* ---- Toggle styling ---- */
[data-testid="stToggle"] label {{
    font-weight: 500;
}}

/* ---- Expander styling ---- */
.streamlit-expanderHeader {{
    font-weight: 600;
}}

/* ---- Header area ---- */
.main-header {{
    text-align: center;
    padding: 2rem 0 1.25rem 0;
}}
.main-header h1 {{
    font-size: 2.6rem;
    margin-bottom: 0;
    background: linear-gradient(135deg, #5B8CFF, #9B8CFF, #FF8A65);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    letter-spacing: -0.03em;
}}
.main-header p {{
    color: {text_secondary};
    font-size: 0.95rem;
    margin-top: 0.25rem;
    letter-spacing: 0.02em;
}}

/* ---- Risk-level atmospheric border ---- */
.main .block-container {{
    border-top: 3px solid {border_color};
    transition: border-color 0.5s ease;
}}

/* ---- Critical pulsing warning bar ---- */
{critical_bar_css}

/* ---- Smooth card hover elevation ---- */
.stExpander {{
    transition: box-shadow 0.3s ease, transform 0.3s ease;
    border-radius: 0.75rem;
}}
.stExpander:hover {{
    box-shadow: 0 4px 20px rgba(91,140,255,0.10);
    transform: translateY(-2px);
}}

/* ---- Profile setup form glassmorphism ---- */
[data-testid="stForm"] {{
    background: {form_bg};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 1rem;
    border: 1px solid {card_border};
    padding: 1.5rem;
    box-shadow: 0 4px 28px rgba(91,140,255,0.10);
}}

/* ---- Slider styling ---- */
[data-testid="stSlider"] {{
    padding-top: 0;
}}

/* ---- Plotly chart containers with shimmer loading ---- */
[data-testid="stPlotlyChart"] {{
    border-radius: 0.75rem;
    overflow: hidden;
    animation: shimmerIn 0.6s ease-out;
}}
@keyframes shimmerIn {{
    from {{ opacity: 0.3; }}
    to   {{ opacity: 1; }}
}}

/* ---- Selectbox & form inputs ---- */
[data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {{
    font-weight: 500;
    font-size: 0.88rem;
    letter-spacing: 0.01em;
}}

/* ---- Animated donut chart transitions ---- */
[data-testid="stPlotlyChart"] .slice {{
    transition: transform 0.3s ease;
}}

/* ---- Volume slider thumb glow ---- */
[data-testid="stSlider"] [role="slider"] {{
    box-shadow: 0 0 8px rgba(91,140,255,0.3);
    transition: box-shadow 0.3s ease;
}}
[data-testid="stSlider"] [role="slider"]:hover {{
    box-shadow: 0 0 16px rgba(91,140,255,0.5);
}}

/* ---- Page transitions ---- */
.main .block-container {{
    animation: pageTransition 0.5s ease-out;
}}
@keyframes pageTransition {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* =============================================
   LANDING SCREEN — Hero & Illustration
   ============================================= */

/* Hero section */
.landing-hero {{
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    animation: heroFadeIn 0.8s ease-out;
}}
@keyframes heroFadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* Floating logo with radial glow */
.hero-logo {{
    font-size: 4.5rem;
    display: inline-block;
    animation: logoFloat 4s ease-in-out infinite;
    position: relative;
    z-index: 2;
    filter: drop-shadow(0 4px 20px rgba(91,140,255,0.3));
}}
@keyframes logoFloat {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-10px); }}
}}
.hero-logo-glow {{
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(91,140,255,0.25) 0%, rgba(155,140,255,0.12) 50%, transparent 70%);
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    top: 1.5rem;
    z-index: 1;
    animation: breatheGlow 3s ease-in-out infinite;
}}
@keyframes breatheGlow {{
    0%, 100% {{ transform: translateX(-50%) scale(1); opacity: 0.6; }}
    50% {{ transform: translateX(-50%) scale(1.15); opacity: 1; }}
}}

/* Hero title and tagline */
.hero-title {{
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #5B8CFF, #9B8CFF, #FF8A65);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
    margin: 0.25rem 0 0;
}}
.hero-tagline {{
    color: {text_secondary};
    font-size: 1rem;
    letter-spacing: 0.03em;
    animation: taglineFade 1.2s ease-out 0.4s both;
}}
@keyframes taglineFade {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* Illustration panel */
.illustration-panel {{
    text-align: center;
    padding: 2rem 0;
    animation: heroFadeIn 1s ease-out 0.3s both;
}}
.wellness-art {{
    width: 80%;
    max-width: 220px;
    height: auto;
    filter: drop-shadow(0 8px 32px rgba(91,140,255,0.15));
}}
.art-circle-outer {{
    animation: artPulse 6s ease-in-out infinite;
    transform-origin: center;
}}
.art-circle-inner {{
    animation: artPulse 6s ease-in-out infinite 1s;
    transform-origin: center;
}}
.art-circle-core {{
    animation: artPulse 4s ease-in-out infinite 0.5s;
    transform-origin: center;
}}
@keyframes artPulse {{
    0%, 100% {{ opacity: 0.7; }}
    50% {{ opacity: 1; }}
}}
.art-leaf {{
    animation: leafSway 8s ease-in-out infinite;
    transform-origin: 100px 100px;
}}
@keyframes leafSway {{
    0%, 100% {{ transform: rotate(0deg); }}
    50% {{ transform: rotate(6deg); }}
}}
.art-dot {{
    animation: dotDrift 5s ease-in-out infinite;
}}
.art-dot-1 {{ animation-delay: 0s; }}
.art-dot-2 {{ animation-delay: 1.2s; }}
.art-dot-3 {{ animation-delay: 2.4s; }}
.art-dot-4 {{ animation-delay: 3.6s; }}
@keyframes dotDrift {{
    0%, 100% {{ transform: translate(0, 0); opacity: 0.5; }}
    50% {{ transform: translate(4px, -4px); opacity: 1; }}
}}

/* =============================================
   ANIMATED HEADER BAR (chat interface)
   ============================================= */

.chat-header-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 1.25rem;
    border-radius: 0.75rem;
    background: {card_bg};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {card_border};
    margin-bottom: 0.75rem;
    animation: headerShimmer 3s ease-in-out infinite, fadeSlideIn 0.5s ease-out;
    box-shadow: 0 2px 16px rgba(91,140,255,0.08);
    position: relative;
    overflow: hidden;
}}
.chat-header-bar::after {{
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
    animation: shimmerSlide 4s ease-in-out infinite;
}}
@keyframes shimmerSlide {{
    0% {{ left: -100%; }}
    100% {{ left: 200%; }}
}}
.header-title {{
    font-weight: 700;
    font-size: 1.1rem;
    color: {text_heading};
    letter-spacing: -0.01em;
}}
.header-right {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.emo-state-icon {{
    font-size: 1.4rem;
    animation: emoIconBounce 3s ease-in-out infinite;
}}
@keyframes emoIconBounce {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.15); }}
}}

/* Streak badge */
.streak-badge {{
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 1rem;
    background: rgba(155,140,255,0.12);
    color: #9B8CFF;
    animation: badgePop 0.5s cubic-bezier(0.22,1,0.36,1);
}}
.streak-badge.streak-fire {{
    background: rgba(239,83,80,0.12);
    color: #EF5350;
    animation: badgePop 0.5s cubic-bezier(0.22,1,0.36,1), badgeGlow 2s ease-in-out infinite;
}}
.streak-badge.streak-warm {{
    background: rgba(255,183,77,0.12);
    color: #FFB74D;
}}
@keyframes badgePop {{
    from {{ transform: scale(0.5); opacity: 0; }}
    to   {{ transform: scale(1); opacity: 1; }}
}}
@keyframes badgeGlow {{
    0%, 100% {{ box-shadow: 0 0 4px rgba(239,83,80,0.2); }}
    50% {{ box-shadow: 0 0 12px rgba(239,83,80,0.4); }}
}}

/* =============================================
   EMOTION-REACTIVE ASSISTANT BUBBLES
   ============================================= */

.emo-joy ~ div .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    border-left-color: #4DD0E1;
    box-shadow: 0 4px 24px rgba(77,208,225,0.15), inset 0 1px 0 rgba(77,208,225,0.08);
}}
.emo-anxiety ~ div .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    border-left-color: #FFB74D;
    box-shadow: 0 4px 24px rgba(255,183,77,0.15), inset 0 1px 0 rgba(255,183,77,0.08);
}}
.emo-sadness ~ div .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    border-left-color: #5B8CFF;
    box-shadow: 0 4px 24px rgba(91,140,255,0.18), inset 0 1px 0 rgba(91,140,255,0.08);
}}
.emo-anger ~ div .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    border-left-color: #EF5350;
    box-shadow: 0 4px 24px rgba(239,83,80,0.12), inset 0 1px 0 rgba(239,83,80,0.06);
}}
.emo-crisis ~ div .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    border-left-color: #D32F2F;
    box-shadow: 0 4px 24px rgba(211,47,47,0.18), inset 0 1px 0 rgba(211,47,47,0.08);
}}

/* =============================================
   CALM MODE VISUALIZATION
   ============================================= */

/* Pulsing background when calm mode active */
.calm-active-bg {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(ellipse at center, rgba(91,140,255,0.04) 0%, transparent 70%);
    animation: calmPulse 4s ease-in-out infinite;
}}
@keyframes calmPulse {{
    0%, 100% {{ opacity: 0.4; transform: scale(1); }}
    50% {{ opacity: 0.8; transform: scale(1.02); }}
}}

/* Waveform visualization */
.waveform-bar {{
    display: inline-block;
    width: 3px;
    margin: 0 1px;
    border-radius: 2px;
    background: linear-gradient(to top, #5B8CFF, #9B8CFF);
    animation: waveAnimate 1.2s ease-in-out infinite;
    vertical-align: bottom;
}}
.waveform-bar:nth-child(1) {{ height: 12px; animation-delay: 0s; }}
.waveform-bar:nth-child(2) {{ height: 18px; animation-delay: 0.1s; }}
.waveform-bar:nth-child(3) {{ height: 24px; animation-delay: 0.2s; }}
.waveform-bar:nth-child(4) {{ height: 16px; animation-delay: 0.3s; }}
.waveform-bar:nth-child(5) {{ height: 20px; animation-delay: 0.4s; }}
.waveform-bar:nth-child(6) {{ height: 14px; animation-delay: 0.5s; }}
.waveform-bar:nth-child(7) {{ height: 22px; animation-delay: 0.6s; }}
.waveform-bar:nth-child(8) {{ height: 10px; animation-delay: 0.7s; }}
@keyframes waveAnimate {{
    0%, 100% {{ transform: scaleY(0.5); opacity: 0.5; }}
    50% {{ transform: scaleY(1); opacity: 1; }}
}}

/* =============================================
   SESSION END — SUMMARY ANIMATION
   ============================================= */

@keyframes summarySlideUp {{
    from {{ opacity: 0; transform: translateY(30px) scale(0.95); }}
    to   {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
.session-summary-card {{
    animation: summarySlideUp 0.6s cubic-bezier(0.22,1,0.36,1);
    background: {card_bg};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 1rem;
    padding: 1.5rem;
    border: 1px solid {card_border};
    box-shadow: 0 8px 40px rgba(91,140,255,0.12);
    text-align: center;
    margin: 1rem 0;
}}

@keyframes headerShimmer {{
    0%, 100% {{ box-shadow: 0 2px 16px rgba(91,140,255,0.08); }}
    50% {{ box-shadow: 0 2px 24px rgba(91,140,255,0.14); }}
}}
</style>
"""
