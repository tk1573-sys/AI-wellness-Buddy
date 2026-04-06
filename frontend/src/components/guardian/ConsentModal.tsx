/**
 * GuardianConsentModal
 *
 * Displayed before guardian alerts are enabled.  The user must explicitly
 * accept the terms before the setting is saved — auto-sending is never done
 * without this consent.
 */

"use client";

import { Button } from "@/components/ui/Button";

interface GuardianConsentModalProps {
  onAccept: () => void;
  onDecline: () => void;
}

export function GuardianConsentModal({ onAccept, onDecline }: GuardianConsentModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="relative w-full max-w-md rounded-2xl border border-amber-500/30 bg-gray-900 p-6 shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-start gap-3">
          <span className="text-3xl">🛡️</span>
          <div>
            <h2 className="text-lg font-semibold text-gray-100">Enable Guardian Alerts</h2>
            <p className="text-xs text-gray-400 mt-0.5">Please read carefully before proceeding</p>
          </div>
        </div>

        {/* Body */}
        <div className="text-sm text-gray-300 space-y-3 border-t border-white/10 pt-4">
          <p>
            By enabling guardian alerts, you agree that the AI Wellness Buddy may send
            automatic notifications to your designated guardian when a{" "}
            <span className="font-medium text-amber-300">high-risk or critical</span> distress
            signal is detected in your sessions.
          </p>
          <ul className="list-disc list-inside space-y-1 text-gray-400 text-xs pl-1">
            <li>Alerts are sent only when consent is explicitly granted (this screen).</li>
            <li>Your guardian will receive your alias, risk level, and a brief summary.</li>
            <li>You can withdraw consent at any time from your Profile settings.</li>
            <li>No chat content is shared — only risk metadata.</li>
          </ul>
          <p className="text-xs text-gray-500">
            Channels: Email and / or WhatsApp — depending on what you configure.
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={onDecline}
            className="flex-1 py-2 rounded-xl text-sm border border-glass-border text-gray-400 hover:text-gray-200 transition-colors"
          >
            Cancel
          </button>
          <Button onClick={onAccept} className="flex-1">
            I Consent — Enable Alerts
          </Button>
        </div>
      </div>
    </div>
  );
}
