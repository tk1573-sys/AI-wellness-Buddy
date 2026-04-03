/**
 * CalmModeSidebar — sidebar panel with calm-mode toggle,
 * ambient sound selector/volume, and breathing exercise launcher.
 */

"use client";

import { useState } from "react";
import { Wind } from "lucide-react";
import { AmbientPlayer } from "./AmbientPlayer";
import { BreathingExercise } from "./BreathingExercise";
import { t, type LanguagePreference } from "@/lib/i18n";

interface CalmModeSidebarProps {
  language?: LanguagePreference;
}

export function CalmModeSidebar({ language = "english" }: CalmModeSidebarProps) {
  const [calmMode, setCalmMode] = useState(false);
  const [showBreathing, setShowBreathing] = useState(false);

  return (
    <div className="px-3 py-3 border-t border-glass-border space-y-3">
      {/* Calm mode toggle */}
      <label className="flex items-center justify-between cursor-pointer">
        <span className="text-xs font-medium text-gray-400 flex items-center gap-1.5">
          <Wind className="w-3 h-3" />
          {t("ambient.title", language)}
        </span>
        <button
          type="button"
          role="switch"
          aria-checked={calmMode}
          onClick={() => {
            setCalmMode((c) => !c);
            if (showBreathing) setShowBreathing(false);
          }}
          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
            calmMode ? "bg-brand-600" : "bg-gray-700"
          }`}
        >
          <span
            className={`inline-block h-3.5 w-3.5 rounded-full bg-white shadow transition-transform ${
              calmMode ? "translate-x-4" : "translate-x-0.5"
            }`}
          />
        </button>
      </label>

      {/* Ambient player (only when calm mode on) */}
      {calmMode && (
        <AmbientPlayer language={language} playing={true} />
      )}

      {/* Breathing exercise launcher */}
      <button
        type="button"
        onClick={() => setShowBreathing((s) => !s)}
        className="w-full flex items-center gap-2 px-3 py-2 rounded-xl border border-glass-border text-xs text-gray-400 hover:text-gray-100 hover:bg-white/5 transition-colors"
      >
        🫁 {showBreathing ? t("chat.breathing.stop", language) : t("chat.breathing.start", language)}
      </button>

      {showBreathing && <BreathingExercise language={language} />}
    </div>
  );
}
