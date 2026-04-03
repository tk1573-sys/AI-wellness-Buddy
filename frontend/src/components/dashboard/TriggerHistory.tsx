/**
 * TriggerHistory — displays personal triggers stored in the user profile,
 * and provides an add-trigger form.
 */

"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { X, Plus } from "lucide-react";
import { updateProfile, type UserProfile } from "@/lib/api";

interface TriggerHistoryProps {
  profile: UserProfile;
  onUpdate: (updated: UserProfile) => void;
}

export function TriggerHistory({ profile, onUpdate }: TriggerHistoryProps) {
  const [input, setInput] = useState("");
  const [saving, setSaving] = useState(false);

  const triggers: string[] = profile.personal_triggers ?? [];

  const handleAdd = async () => {
    const raw = input.trim();
    if (!raw) return;
    // Support comma-separated entries
    const newTriggers = raw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const merged = Array.from(new Set([...triggers, ...newTriggers]));
    setSaving(true);
    try {
      const updated = await updateProfile({ ...profile, personal_triggers: merged });
      onUpdate(updated);
      setInput("");
      toast.success("Triggers saved.");
    } catch {
      toast.error("Failed to save triggers.");
    } finally {
      setSaving(false);
    }
  };

  const handleRemove = async (trigger: string) => {
    const remaining = triggers.filter((t) => t !== trigger);
    setSaving(true);
    try {
      const updated = await updateProfile({ ...profile, personal_triggers: remaining });
      onUpdate(updated);
    } catch {
      toast.error("Failed to remove trigger.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-3">
      {/* Existing triggers as chips */}
      {triggers.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {triggers.map((trigger) => (
            <span
              key={trigger}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-600/20 border border-brand-500/40 text-xs text-brand-300"
            >
              {trigger}
              <button
                type="button"
                onClick={() => handleRemove(trigger)}
                disabled={saving}
                aria-label={`Remove ${trigger}`}
                className="hover:text-red-400 transition-colors disabled:opacity-40"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      ) : (
        <p className="text-xs text-gray-500">No personal triggers recorded yet.</p>
      )}

      {/* Add form */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAdd()}
          placeholder="Add trigger (comma-separated)…"
          className="flex-1 rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          type="button"
          onClick={handleAdd}
          disabled={!input.trim() || saving}
          className="flex items-center gap-1 px-3 py-2 rounded-xl bg-brand-600/30 border border-brand-500/50 text-brand-300 text-sm hover:bg-brand-600/40 disabled:opacity-40 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add
        </button>
      </div>
    </div>
  );
}
