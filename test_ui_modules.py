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

    def test_background_theme_aurora_overlay(self):
        from ui.theme import get_theme_css
        css = get_theme_css(background_theme='aurora')
        assert 'rgba(77,208,225,0.12)' in css

    def test_background_theme_ocean_overlay(self):
        from ui.theme import get_theme_css
        css = get_theme_css(background_theme='ocean')
        assert 'rgba(56,189,248,0.10)' in css

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

    def test_emotion_journey_line_chart(self):
        from ui.charts import create_emotion_journey_line
        fig = create_emotion_journey_line([
            {'emotion': 'anxiety', 'risk_score': 0.6},
            {'emotion': 'stress', 'risk_score': 0.7},
        ])
        assert fig is not None
        assert len(fig.data) == 1

    def test_stress_intensity_gauge(self):
        from ui.charts import create_stress_intensity_gauge
        fig = create_stress_intensity_gauge(0.72)
        assert fig is not None
        assert fig.data[0].value == 0.72

    def test_emotion_probability_bar_returns_figure(self):
        from ui.charts import create_emotion_probability_bar
        probs = {'joy': 0.6, 'sadness': 0.2, 'neutral': 0.15, 'anger': 0.05}
        fig = create_emotion_probability_bar(probs)
        assert fig is not None
        assert len(fig.data) == 1
        # Bars should be sorted descending — first bar value is highest prob
        assert fig.data[0].x[0] == 0.6

    def test_emotion_probability_bar_empty_probs(self):
        from ui.charts import create_emotion_probability_bar
        fig = create_emotion_probability_bar({})
        assert fig is not None
        # Defaults to neutral = 1.0
        assert fig.data[0].x[0] == 1.0

    def test_emotion_probability_bar_single_emotion(self):
        from ui.charts import create_emotion_probability_bar
        fig = create_emotion_probability_bar({'crisis': 0.95})
        assert fig is not None
        assert len(fig.data[0].x) == 1


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

    def test_wellness_sidebar_card(self):
        from ui.layout import render_wellness_sidebar_card
        html = render_wellness_sidebar_card("Status", "<p>steady</p>", icon="🧘")
        assert 'wellness-sidebar-card' in html
        assert 'Status' in html

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

    def test_sound_labels_includes_white_noise(self):
        from ui.layout import SOUND_LABELS
        assert 'white_noise' in SOUND_LABELS
        assert SOUND_LABELS['white_noise'] == 'White Noise'

    def test_emotional_avatar_returns_html(self):
        from ui.layout import render_emotional_avatar
        html = render_emotional_avatar('joy')
        assert 'emotional-avatar' in html
        assert '😊' in html
        assert 'Joy' in html
        assert 'avatarBounce' in html

    def test_emotional_avatar_crisis(self):
        from ui.layout import render_emotional_avatar
        html = render_emotional_avatar('crisis')
        assert '⚠️' in html
        assert 'avatarPulse' in html

    def test_emotional_avatar_default_neutral(self):
        from ui.layout import render_emotional_avatar
        html = render_emotional_avatar('unknown_emotion')
        assert '😐' in html
        assert 'Neutral' in html

    def test_emotional_avatar_accepts_avatar_state(self):
        from ui.layout import render_emotional_avatar
        html = render_emotional_avatar('anxiety', avatar_state='bounce', trend='worsening')
        assert 'avatarBounce' in html
        assert 'Worsening' in html

    def test_wellness_illustration_large(self):
        from ui.layout import render_wellness_illustration_large
        html = render_wellness_illustration_large()
        assert '<svg' in html
        assert 'wellness-art-large' in html
        assert 'viewBox="0 0 300 300"' in html
        assert 'art-heart' in html
        assert 'art-mini-leaf' in html


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
        assert 'thinking' in TYPING_INDICATOR_HTML

    def test_ambient_sound_white_noise(self):
        from ui.animations import ambient_sound_html
        html = ambient_sound_html('white_noise', 0.02)
        assert '200' in html  # white_noise frequency
        assert 'sawtooth' in html

    def test_canvas_particles_html(self):
        from ui.animations import canvas_particles_html
        html = canvas_particles_html()
        assert 'wellness-particles' in html
        assert 'canvas' in html.lower()
        assert 'requestAnimationFrame' in html

    def test_canvas_particles_theme_mode(self):
        from ui.animations import canvas_particles_html
        html = canvas_particles_html(theme='night_sky', calm_mode=True)
        assert 'rgba(148,163,184' in html
        assert '0.35' in html

    def test_canvas_particles_updates_existing_instance(self):
        from ui.animations import canvas_particles_html
        html = canvas_particles_html(theme='aurora', calm_mode=True)
        assert 'window._particleColorPrefix' in html
        assert 'window._particleMotion' in html

    def test_breathing_circle_html(self):
        from ui.animations import breathing_circle_html
        html = breathing_circle_html()
        assert 'breathing-container' in html
        assert 'breathing-circle' in html
        assert 'Breathe' in html
        assert 'inhale' in html

    def test_guided_breathing_message_html(self):
        from ui.animations import guided_breathing_message_html
        html = guided_breathing_message_html()
        assert 'guided-breathing-msg' in html
        assert 'Inhale' in html
        assert 'Exhale' in html


# -----------------------------------------------------------------------
# New: ui.charts — emotion heatmap tests
# -----------------------------------------------------------------------

class TestHeatmapChart:
    """Tests for the emotion heatmap chart."""

    def test_emotion_heatmap_returns_figure(self):
        from ui.charts import create_emotion_heatmap
        timeline = [
            {'joy': 0.8, 'neutral': 0.1, 'sadness': 0.0, 'anger': 0.0, 'fear': 0.0, 'crisis': 0.0},
            {'joy': 0.3, 'neutral': 0.5, 'sadness': 0.1, 'anger': 0.0, 'fear': 0.1, 'crisis': 0.0},
        ]
        fig = create_emotion_heatmap(timeline)
        assert fig is not None
        assert fig.data[0].type == 'heatmap'

    def test_emotion_heatmap_has_correct_axes(self):
        from ui.charts import create_emotion_heatmap
        timeline = [
            {'joy': 0.5, 'sadness': 0.3},
            {'joy': 0.2, 'sadness': 0.6},
            {'joy': 0.7, 'sadness': 0.1},
        ]
        fig = create_emotion_heatmap(timeline)
        # Should have 6 rows (emotions) and 3 columns (messages)
        assert len(fig.data[0].z) == 6
        assert len(fig.data[0].x) == 3

    def test_emotion_heatmap_missing_keys(self):
        from ui.charts import create_emotion_heatmap
        # Some emotions missing — should default to 0
        timeline = [{'joy': 0.5}, {'sadness': 0.8}]
        fig = create_emotion_heatmap(timeline)
        assert fig is not None


# -----------------------------------------------------------------------
# New: theme CSS — new component styles
# -----------------------------------------------------------------------

class TestThemeNewComponents:
    """Tests for new CSS in theme.py."""

    def test_breathing_circle_css(self):
        from ui.theme import get_theme_css
        css = get_theme_css()
        assert 'breathing-circle' in css
        assert 'breatheCircle' in css

    def test_emotional_avatar_css(self):
        from ui.theme import get_theme_css
        css = get_theme_css()
        assert 'emotional-avatar' in css
        assert 'avatarBounce' in css
        assert 'avatarGlow' in css
        assert 'avatarPulse' in css

    def test_typing_label_css(self):
        from ui.theme import get_theme_css
        css = get_theme_css()
        assert 'typing-label' in css
        assert 'typingLabelFade' in css

    def test_motion_system_keyframes(self):
        from ui.theme import get_theme_css
        css = get_theme_css(background_theme='night_sky')
        assert 'fadeInUp' in css
        assert 'softPulse' in css
        assert 'floatingMotion' in css
        assert 'breathingGlow' in css
        assert 'gradientShift' in css

    def test_large_illustration_css(self):
        from ui.theme import get_theme_css
        css = get_theme_css()
        assert 'illustration-panel-large' in css
        assert 'wellness-art-large' in css
        assert 'art-heart' in css
