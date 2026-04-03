/**
 * BreathingExercise — animated 4-7-8 breathing guide.
 *
 * Phases:
 *   Inhale  4 s — circle expands
 *   Hold    7 s — circle stays large
 *   Exhale  8 s — circle contracts
 */

"use client";

import { useEffect, useRef, useState } from "react";
import { t, type LanguagePreference } from "@/lib/i18n";

interface BreathingExerciseProps {
  language?: LanguagePreference;
}

type Phase = "inhale" | "hold" | "exhale";

const PHASES: { phase: Phase; duration: number }[] = [
  { phase: "inhale", duration: 4 },
  { phase: "hold", duration: 7 },
  { phase: "exhale", duration: 8 },
];

const PHASE_COLORS: Record<Phase, string> = {
  inhale: "bg-brand-500/40 border-brand-400/60",
  hold: "bg-purple-500/40 border-purple-400/60",
  exhale: "bg-teal-500/30 border-teal-400/50",
};

const PHASE_SIZES: Record<Phase, string> = {
  inhale: "w-36 h-36",
  hold: "w-36 h-36",
  exhale: "w-20 h-20",
};

export function BreathingExercise({ language = "english" }: BreathingExerciseProps) {
  const [phaseIndex, setPhaseIndex] = useState(0);
  const [remaining, setRemaining] = useState(PHASES[0].duration);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);

    setRemaining(PHASES[phaseIndex].duration);

    intervalRef.current = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          setPhaseIndex((pi) => {
            const nextIndex = (pi + 1) % PHASES.length;
            setRemaining(PHASES[nextIndex].duration);
            return nextIndex;
          });
          return prev; // will be overwritten by the setPhaseIndex callback above
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [phaseIndex]);

  const current = PHASES[phaseIndex];

  return (
    <div className="flex flex-col items-center gap-4 py-4">
      {/* Animated circle */}
      <div
        className={`
          rounded-full border-2 flex items-center justify-center transition-all
          ${PHASE_COLORS[current.phase]}
          ${PHASE_SIZES[current.phase]}
          ${current.phase === "inhale" ? "duration-[4000ms]" : current.phase === "exhale" ? "duration-[8000ms]" : "duration-[7000ms]"}
          ease-in-out
        `}
      >
        <span className="text-3xl select-none">
          {current.phase === "inhale" ? "🌬️" : current.phase === "hold" ? "🌀" : "😮‍💨"}
        </span>
      </div>

      {/* Phase label */}
      <p className="text-lg font-semibold text-gray-100">
        {t(`breathing.${current.phase}`, language)}
      </p>

      {/* Countdown */}
      <p className="text-4xl font-bold text-brand-400 tabular-nums">{remaining}</p>

      {/* Instructions */}
      <p className="text-xs text-gray-500 text-center max-w-xs">
        4-7-8 breathing · Inhale 4 s · Hold 7 s · Exhale 8 s
      </p>
    </div>
  );
}
