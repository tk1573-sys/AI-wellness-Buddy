"""
Tests for the modular UI package (ui/).

Covers theme generation, chart creation, layout components, and animations.
"""

import pytest


# -----------------------------------------------------------------------
# ui.theme tests
# -----------------------------------------------------------------------

class TestThemeModule:
    """Tests for ui/theme.py"""

    def test_get_theme_css_returns_style_tag(self):
        from ui.theme import get_theme_css
        css = get_theme_css(dark_mode=False, ui_theme='calm', risk_level='low')
        assert '<style>' in css
        assert '</style>' in css

    def test_dark_mode_uses_dark_background(self):
        from ui.theme import get_theme_css
        css = get_theme_css(dark_mode=True, ui_theme='calm', risk_level='low')
        assert '#0f172a' in css  # dark bg color

    def test_light_mode_calm_theme(self):
        from ui.theme import get_theme_css
        css = get_theme_css(dark_mode=False, ui_theme='calm', risk_level='low')
        assert '#f0f4ff' in css

    def test_clinical_theme(self):
        from ui.theme import get_theme_css
        css = get_theme_css(dark_mode=False, ui_theme='clinical', risk_level='low')
        assert '#f8fafc' in css

    def test_modern_theme(self):
        from ui.theme import get_theme_css
        css = get_theme_css(dark_mode=False, ui_theme='modern', risk_level='low')
        assert '#ede9fe' in css

    def test_critical_risk_includes_pulse_bar(self):
        from ui.theme import get_theme_css
        css = get_theme_css(dark_mode=False, ui_theme='calm', risk_level='critical')
        assert 'CRITICAL' in css
        assert 'pulse-bar' in css

    def test_low_risk_no_critical_bar(self):
        from ui.theme import get_theme_css
        css = get_theme_css(dark_mode=False, ui_theme='calm', risk_level='low')
        assert 'CRITICAL — Please reach out' not in css

    def test_contains_animation_keyframes(self):
        from ui.theme import get_theme_css
        css = get_theme_css()
        assert 'gradientBG' in css
        assert 'fadeSlideIn' in css
        assert 'typingBounce' in css

    def test_contains_glassmorphism(self):
        from ui.theme import get_theme_css
        css = get_theme_css()
        assert 'backdrop-filter' in css
        assert 'blur' in css


# -----------------------------------------------------------------------
# ui.charts tests
# -----------------------------------------------------------------------

class TestChartsModule:
    """Tests for ui/charts.py"""

    def test_sentiment_chart_returns_figure(self):
        from ui.charts import create_sentiment_chart
        fig = create_sentiment_chart([0.1, 0.3, -0.2, 0.5])
        assert fig is not None
        assert len(fig.data) == 1

    def test_emotion_donut_returns_figure(self):
        from ui.charts import create_emotion_donut
        fig = create_emotion_donut(['joy', 'sadness'], [5, 3])
        assert fig is not None
        assert fig.data[0].hole == 0.55

    def test_risk_gauge_returns_figure(self):
        from ui.charts import create_risk_gauge
        fig = create_risk_gauge(0.45, 'medium')
        assert fig is not None
        assert fig.data[0].value == 0.45

    def test_history_chart_with_forecast(self):
        from ui.charts import create_history_chart
        forecast = {'predicted_value': 0.6, 'confidence': 'medium', 'interpretation': 'stable'}
        fig = create_history_chart([0.3, 0.4, 0.5], forecast)
        assert len(fig.data) == 2  # main + forecast

    def test_history_chart_without_forecast(self):
        from ui.charts import create_history_chart
        fig = create_history_chart([0.3, 0.4, 0.5])
        assert len(fig.data) == 1

    def test_weekly_chart_returns_figure(self):
        from ui.charts import create_weekly_chart
        fig = create_weekly_chart([0.2, 0.4, 0.6])
        assert fig is not None

    def test_sparkline_returns_figure(self):
        from ui.charts import create_sparkline
        fig = create_sparkline([0.1, 0.2, 0.3])
        assert fig.layout.height == 80

    def test_moving_average_chart(self):
        from ui.charts import create_moving_average_chart
        fig = create_moving_average_chart([0.2, 0.3, 0.4])
        assert fig is not None

    def test_risk_history_chart(self):
        from ui.charts import create_risk_history_chart
        fig = create_risk_history_chart([0.1, 0.35, 0.65])
        assert fig is not None


# -----------------------------------------------------------------------
# ui.layout tests
# -----------------------------------------------------------------------

class TestLayoutModule:
    """Tests for ui/layout.py"""

    def test_hero_section_content(self):
        from ui.layout import render_hero_section
        html = render_hero_section()
        assert 'AI Wellness Buddy' in html
        assert 'hero-logo' in html
        assert 'Safe Space' in html

    def test_wellness_illustration_svg(self):
        from ui.layout import render_wellness_illustration
        html = render_wellness_illustration()
        assert '<svg' in html
        assert 'wellness-art' in html

    def test_chat_header_with_streak(self):
        from ui.layout import render_chat_header
        html = render_chat_header(accent_color='low', emo_icon='😊', streak=5)
        assert 'streak-badge' in html
        assert '⭐' in html
        assert '5' in html

    def test_chat_header_fire_streak(self):
        from ui.layout import render_chat_header
        html = render_chat_header(accent_color='low', emo_icon='😊', streak=10)
        assert 'streak-fire' in html

    def test_user_avatar(self):
        from ui.layout import render_user_avatar
        html = render_user_avatar('TestUser')
        assert 'T' in html  # first letter
        assert 'TestUser' in html

    def test_risk_badge_levels(self):
        from ui.layout import render_risk_badge
        for level in ['low', 'medium', 'high', 'critical']:
            html = render_risk_badge(level)
            assert level.upper() in html

    def test_session_info_card(self):
        from ui.layout import render_session_info_card
        html = render_session_info_card(5, 'english', 12)
        assert 'Session #5' in html
        assert '12 messages' in html

    def test_streak_card(self):
        from ui.layout import render_streak_card
        html = render_streak_card(3)
        assert '🔥' in html
        assert '3' in html

    def test_waveform_section(self):
        from ui.layout import render_waveform_section
        html = render_waveform_section('deep_focus')
        assert 'waveform-bar' in html
        assert 'Deep Focus' in html

    def test_session_summary_card(self):
        from ui.layout import render_session_summary_card
        html = render_session_summary_card(
            dominant_emotion='joy',
            message_count=15,
            risk_level='low',
            streak=3,
        )
        assert 'Session Complete' in html
        assert '15' in html
        assert 'Joy' in html

    def test_emotion_flag(self):
        from ui.layout import render_emotion_flag
        html = render_emotion_flag('anxiety')
        assert 'emo-anxiety' in html

    def test_constants_exported(self):
        from ui.layout import EMO_ICONS, RISK_COLOUR, RISK_LEVEL_VALUES, SOUND_LABELS
        assert EMO_ICONS['joy'] == '😊'
        assert RISK_COLOUR['critical'] == '🚨'
        assert RISK_LEVEL_VALUES['high'] == 0.65
        assert SOUND_LABELS['soft_rain'] == 'Soft Rain'


# -----------------------------------------------------------------------
# ui.animations tests
# -----------------------------------------------------------------------

class TestAnimationsModule:
    """Tests for ui/animations.py"""

    def test_ambient_sound_html(self):
        from ui.animations import ambient_sound_html
        html = ambient_sound_html('deep_focus', 0.03)
        assert 'AudioContext' in html
        assert '174' in html  # deep_focus frequency

    def test_ambient_sound_calm_waves(self):
        from ui.animations import ambient_sound_html
        html = ambient_sound_html('calm_waves', 0.05)
        assert '136' in html  # calm_waves frequency

    def test_ambient_stop_html(self):
        from ui.animations import ambient_stop_html
        html = ambient_stop_html()
        assert 'ambientOsc' in html
        assert 'stop()' in html

    def test_typing_indicator_html(self):
        from ui.animations import TYPING_INDICATOR_HTML
        assert 'typing-indicator' in TYPING_INDICATOR_HTML
        assert '<span>' in TYPING_INDICATOR_HTML
