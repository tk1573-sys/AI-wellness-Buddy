"""
UI package for AI Wellness Buddy.

Provides modular, research-grade UI components:
    theme      — CSS generation and theme variables
    animations — Animation CSS and HTML helpers
    charts     — Plotly chart creation functions
    layout     — Reusable layout / HTML components
"""

from ui.theme import get_theme_css            # noqa: F401
from ui.charts import (                       # noqa: F401
    create_sentiment_chart,
    create_emotion_donut,
    create_risk_gauge,
    create_history_chart,
    create_weekly_chart,
    create_sparkline,
    create_moving_average_chart,
    create_risk_history_chart,
    create_emotion_heatmap,
    create_emotion_journey_line,
    create_stress_intensity_gauge,
)
from ui.layout import (                       # noqa: F401
    render_hero_section,
    render_chat_header,
    render_user_avatar,
    render_risk_badge,
    render_concern_badge,
    render_session_info_card,
    render_streak_card,
    render_waveform_section,
    render_wellness_sidebar_card,
    render_session_summary_card,
    render_emotional_avatar,
    render_wellness_illustration_large,
)
from ui.animations import (                   # noqa: F401
    canvas_particles_html,
    breathing_circle_html,
    guided_breathing_message_html,
    breathing_exercise_html,
)
