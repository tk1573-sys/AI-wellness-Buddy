/**
 * AmbientPlayer — plays looping ambient tones via the Web Audio API.
 *
 * Four soundscapes are synthesised procedurally (no external audio files):
 *   deep_focus  — 174 Hz sine (Solfeggio healing tone)
 *   calm_waves  — amplitude-modulated 80 Hz (wave pulse effect)
 *   soft_rain   — white-noise burst pattern
 *   forest      — layered 285 Hz + 528 Hz (nature harmonics)
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Music, VolumeX } from "lucide-react";
import { t, type LanguagePreference } from "@/lib/i18n";

type Soundscape = "deep_focus" | "calm_waves" | "soft_rain" | "forest";

interface AmbientPlayerProps {
  language?: LanguagePreference;
  soundscape?: Soundscape;
  volume?: number;       // 0.0 – 1.0
  playing?: boolean;
}

function createAmbient(
  ctx: AudioContext,
  soundscape: Soundscape,
  volume: number,
): { gainNode: GainNode; stop: () => void } {
  const masterGain = ctx.createGain();
  masterGain.gain.value = volume;
  masterGain.connect(ctx.destination);

  const nodes: AudioNode[] = [];

  const addOsc = (freq: number, type: OscillatorType = "sine", gain = 0.3) => {
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = type;
    osc.frequency.value = freq;
    g.gain.value = gain;
    osc.connect(g);
    g.connect(masterGain);
    osc.start();
    nodes.push(osc, g);
    return osc;
  };

  if (soundscape === "deep_focus") {
    addOsc(174, "sine", 0.35);
    addOsc(174 * 2, "sine", 0.08);
  } else if (soundscape === "calm_waves") {
    const carrier = addOsc(80, "sine", 0.4);
    const lfo = ctx.createOscillator();
    const lfoGain = ctx.createGain();
    lfo.frequency.value = 0.1;    // 0.1 Hz (10-second period) → slow wave pulse
    lfoGain.gain.value = 0.3;
    lfo.connect(lfoGain);
    lfoGain.connect((carrier as OscillatorNode & { frequency: AudioParam }).frequency);
    lfo.start();
    nodes.push(lfo, lfoGain);
  } else if (soundscape === "soft_rain") {
    // White noise via a buffer
    const bufSize = ctx.sampleRate * 2;
    const buffer = ctx.createBuffer(1, bufSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufSize; i++) data[i] = Math.random() * 2 - 1;
    const src = ctx.createBufferSource();
    src.buffer = buffer;
    src.loop = true;
    const filter = ctx.createBiquadFilter();
    filter.type = "bandpass";
    filter.frequency.value = 3000;
    filter.Q.value = 0.5;
    const noiseGain = ctx.createGain();
    noiseGain.gain.value = 0.2;
    src.connect(filter);
    filter.connect(noiseGain);
    noiseGain.connect(masterGain);
    src.start();
    nodes.push(src, filter, noiseGain);
  } else if (soundscape === "forest") {
    addOsc(285, "sine", 0.25);
    addOsc(528, "sine", 0.15);
    addOsc(396, "sine", 0.10);
  }

  return {
    gainNode: masterGain,
    stop: () => {
      nodes.forEach((n) => {
        try { (n as OscillatorNode | AudioBufferSourceNode).stop?.(); } catch { /* noop */ }
        n.disconnect();
      });
      masterGain.disconnect();
    },
  };
}

const SOUNDSCAPES: { key: Soundscape; i18nKey: string }[] = [
  { key: "deep_focus", i18nKey: "ambient.deep_focus" },
  { key: "calm_waves", i18nKey: "ambient.calm_waves" },
  { key: "soft_rain", i18nKey: "ambient.soft_rain" },
  { key: "forest", i18nKey: "ambient.forest" },
];

export function AmbientPlayer({
  language = "english",
  soundscape: initialSoundscape = "deep_focus",
  volume: initialVolume = 0.4,
  playing: initialPlaying = false,
}: AmbientPlayerProps) {
  const [soundscape, setSoundscape] = useState<Soundscape>(initialSoundscape);
  const [volume, setVolume] = useState(initialVolume);
  const [playing, setPlaying] = useState(initialPlaying);

  const ctxRef = useRef<AudioContext | null>(null);
  const ambientRef = useRef<{ gainNode: GainNode; stop: () => void } | null>(null);

  const stopAmbient = useCallback(() => {
    ambientRef.current?.stop();
    ambientRef.current = null;
  }, []);

  const startAmbient = useCallback(() => {
    if (!ctxRef.current || ctxRef.current.state === "closed") {
      ctxRef.current = new AudioContext();
    }
    if (ctxRef.current.state === "suspended") {
      ctxRef.current.resume();
    }
    stopAmbient();
    ambientRef.current = createAmbient(ctxRef.current, soundscape, volume);
  }, [soundscape, volume, stopAmbient]);

  useEffect(() => {
    if (playing) {
      startAmbient();
    } else {
      stopAmbient();
    }
    return stopAmbient;
  }, [playing, soundscape]);

  // Volume change without restart
  useEffect(() => {
    if (ambientRef.current) {
      ambientRef.current.gainNode.gain.value = volume;
    }
  }, [volume]);

  const togglePlay = () => {
    setPlaying((p) => !p);
  };

  return (
    <div className="space-y-3">
      {/* Play / stop toggle */}
      <button
        type="button"
        onClick={togglePlay}
        className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl border text-sm font-medium transition-colors ${
          playing
            ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
            : "border-glass-border text-gray-400 hover:text-gray-100 hover:bg-white/5"
        }`}
      >
        {playing ? <VolumeX className="w-4 h-4" /> : <Music className="w-4 h-4" />}
        {playing ? "Stop Ambient" : t("ambient.title", language)}
      </button>

      {/* Soundscape selector */}
      <div className="grid grid-cols-2 gap-1.5">
        {SOUNDSCAPES.map(({ key, i18nKey }) => (
          <button
            key={key}
            type="button"
            onClick={() => setSoundscape(key)}
            className={`px-2 py-1.5 rounded-lg border text-xs transition-colors ${
              soundscape === key
                ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                : "border-glass-border text-gray-500 hover:text-gray-300"
            }`}
          >
            {t(i18nKey, language)}
          </button>
        ))}
      </div>

      {/* Volume slider */}
      <div className="space-y-1">
        <label className="flex items-center justify-between text-xs text-gray-500">
          <span>{t("ambient.volume", language)}</span>
          <span>{Math.round(volume * 100)}%</span>
        </label>
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={volume}
          onChange={(e) => setVolume(Number(e.target.value))}
          className="w-full accent-brand-500"
        />
      </div>
    </div>
  );
}
