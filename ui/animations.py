"""
Animation helpers for AI Wellness Buddy.

Provides HTML/JS snippets for ambient sound and typing indicators
that are injected into the Streamlit page.
"""


# -----------------------------------------------------------------------
# Ambient sound — Web Audio API oscillators
# -----------------------------------------------------------------------

_SOUNDSCAPES = {
    'deep_focus': {'f1': 174, 't1': 'sine', 'f2': 285, 't2': 'sine', 'hr': 0.3},
    'calm_waves': {'f1': 136, 't1': 'sine', 'f2': 204, 't2': 'triangle', 'hr': 0.25},
    'soft_rain':  {'f1': 220, 't1': 'triangle', 'f2': 330, 't2': 'sine', 'hr': 0.2},
}


def ambient_sound_html(sound_key: str, volume: float) -> str:
    """Return HTML + JS to start/update an ambient oscillator soundscape.

    Parameters
    ----------
    sound_key : str
        One of ``'deep_focus'``, ``'calm_waves'``, ``'soft_rain'``.
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
    '</div>'
)
