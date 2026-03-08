"""
Animation helpers for AI Wellness Buddy.

Provides HTML/JS snippets for ambient sound, typing indicators,
floating canvas particles, and breathing meditation that are
injected into the Streamlit page.
"""


# -----------------------------------------------------------------------
# Ambient sound — Web Audio API oscillators
# -----------------------------------------------------------------------

_SOUNDSCAPES = {
    'deep_focus':   {'f1': 174, 't1': 'sine', 'f2': 285, 't2': 'sine', 'hr': 0.3},
    'calm_waves':   {'f1': 136, 't1': 'sine', 'f2': 204, 't2': 'triangle', 'hr': 0.25},
    'soft_rain':    {'f1': 220, 't1': 'triangle', 'f2': 330, 't2': 'sine', 'hr': 0.2},
    'white_noise':  {'f1': 200, 't1': 'sawtooth', 'f2': 400, 't2': 'sine', 'hr': 0.15},
}


def ambient_sound_html(sound_key: str, volume: float) -> str:
    """Return HTML + JS to start/update an ambient oscillator soundscape.

    Parameters
    ----------
    sound_key : str
        One of ``'deep_focus'``, ``'calm_waves'``, ``'soft_rain'``,
        ``'white_noise'``.
    volume : float
        Volume in 0.0 – 0.1 range.
    """
    sc = _SOUNDSCAPES.get(sound_key, _SOUNDSCAPES['deep_focus'])
    return f"""
    <div id="ambient-music-container" style="display:none;">
        <p style="font-size:0.75rem;color:#9B8CFF;">🎵 Ambient active</p>
    </div>
    <script>
    (function() {{
        var vol = {volume};
        var f1 = {sc['f1']}, t1 = '{sc['t1']}';
        var f2 = {sc['f2']}, t2 = '{sc['t2']}';
        var hr = {sc['hr']};
        var soundKey = '{sound_key}';

        if (window._ambientInitialized && window._ambientSoundKey === soundKey) {{
            if (window._ambientGain) {{
                window._ambientGain.gain.setTargetAtTime(vol, window._ambientCtx.currentTime, 0.1);
            }}
            if (window._ambientGain2) {{
                window._ambientGain2.gain.setTargetAtTime(vol * hr, window._ambientCtx.currentTime, 0.1);
            }}
            return;
        }}

        if (window._ambientOsc) {{ try {{ window._ambientOsc.stop(); }} catch(e) {{}} }}
        if (window._ambientOsc2) {{ try {{ window._ambientOsc2.stop(); }} catch(e) {{}} }}
        window._ambientInitialized = false;

        window._ambientInitialized = true;
        window._ambientSoundKey = soundKey;
        try {{
            var ctx = window._ambientCtx || new (window.AudioContext || window.webkitAudioContext)();
            window._ambientCtx = ctx;
            var osc1 = ctx.createOscillator();
            osc1.type = t1;
            osc1.frequency.value = f1;
            var osc2 = ctx.createOscillator();
            osc2.type = t2;
            osc2.frequency.value = f2;
            var gain1 = ctx.createGain();
            var gain2 = ctx.createGain();
            gain1.gain.value = vol;
            gain2.gain.value = vol * hr;
            osc1.connect(gain1);
            osc2.connect(gain2);
            gain1.connect(ctx.destination);
            gain2.connect(ctx.destination);
            osc1.start();
            osc2.start();
            window._ambientOsc = osc1;
            window._ambientOsc2 = osc2;
            window._ambientGain = gain1;
            window._ambientGain2 = gain2;
        }} catch(e) {{}}
    }})();
    </script>
    """


def ambient_stop_html() -> str:
    """Return JS snippet to stop ambient oscillators."""
    return """
    <script>
    (function() {
        if (window._ambientOsc) {
            try { window._ambientOsc.stop(); } catch(e) {}
            window._ambientOsc = null;
        }
        if (window._ambientOsc2) {
            try { window._ambientOsc2.stop(); } catch(e) {}
            window._ambientOsc2 = null;
        }
        window._ambientInitialized = false;
        window._ambientSoundKey = null;
    })();
    </script>
    """


# -----------------------------------------------------------------------
# Typing indicator
# -----------------------------------------------------------------------

TYPING_INDICATOR_HTML = (
    '<div class="typing-indicator">'
    '<span></span><span></span><span></span>'
    '<span class="typing-label">thinking…</span>'
    '</div>'
)


# -----------------------------------------------------------------------
# Floating canvas particles
# -----------------------------------------------------------------------

_CALM_MODE_PARTICLE_SPEED = 0.12
_NORMAL_PARTICLE_SPEED = 0.30
_THEME_PARTICLE_COLORS = {
    'night_sky': 'rgba(148,163,184,',
    'soft_aurora': 'rgba(77,208,225,',
    'ocean_waves': 'rgba(91,140,255,',
}


def canvas_particles_html(theme: str = 'calm_gradient', calm_mode: bool = False) -> str:
    """Return HTML + JS for a lightweight floating particle background.

    Particles drift slowly to create an ambient wellness atmosphere.
    The canvas is fixed behind all content and does not capture pointer
    events.
    """
    speed = _CALM_MODE_PARTICLE_SPEED if calm_mode else _NORMAL_PARTICLE_SPEED
    color = _THEME_PARTICLE_COLORS.get(theme, 'rgba(155,140,255,')
    opacity = 0.35 if calm_mode else 0.5
    html = """
    <canvas id="wellness-particles" data-opacity="__OPACITY__"></canvas>
    <script>
    (function() {
        if (window._particlesInit) return;
        window._particlesInit = true;
        var c = document.getElementById('wellness-particles');
        if (!c) return;
        c.style.opacity = c.dataset.opacity || '0.5';
        var ctx = c.getContext('2d');
        function resize() { c.width = window.innerWidth; c.height = window.innerHeight; }
        resize();
        window.addEventListener('resize', resize);
        var particles = [];
        var count = 40;
        for (var i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * c.width,
                y: Math.random() * c.height,
                r: Math.random() * 2.5 + 1,
                dx: (Math.random() - 0.5) * __SPEED__,
                dy: (Math.random() - 0.5) * __SPEED__,
                o: Math.random() * 0.4 + 0.1
            });
        }
        function draw() {
            ctx.clearRect(0, 0, c.width, c.height);
            for (var i = 0; i < particles.length; i++) {
                var p = particles[i];
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = '__COLOR__' + p.o + ')';
                ctx.shadowBlur = 8;
                ctx.shadowColor = 'rgba(91,140,255,0.3)';
                ctx.fill();
                p.x += p.dx;
                p.y += p.dy;
                if (p.x < 0 || p.x > c.width) p.dx *= -1;
                if (p.y < 0 || p.y > c.height) p.dy *= -1;
            }
            requestAnimationFrame(draw);
        }
        draw();
    })();
    </script>
    """
    return (
        html
        .replace("__OPACITY__", str(opacity))
        .replace("__SPEED__", str(speed))
        .replace("__COLOR__", color)
    )


# -----------------------------------------------------------------------
# Breathing meditation circle
# -----------------------------------------------------------------------

def guided_breathing_message_html() -> str:
    """Return a subtle inhale-hold-exhale guidance text block."""
    return """
    <div class="guided-breathing-msg">
        <span>Inhale</span>
        <span>Hold</span>
        <span>Exhale</span>
    </div>
    """

def breathing_circle_html() -> str:
    """Return HTML/CSS for an animated breathing meditation circle.

    The animation runs on a 10 s loop (CSS ``breatheCircle``):
    0–40 % (4 s) inhale (scale up), 40–60 % (2 s) hold,
    60–100 % (4 s) exhale (scale down).
    """
    return """
    <div class="breathing-container">
        <div class="breathing-circle">
            <span class="breathing-text">Breathe</span>
        </div>
        <p class="breathing-caption">Follow the circle — inhale as it grows, exhale as it shrinks</p>
    </div>
    """
