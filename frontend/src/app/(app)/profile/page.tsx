/**
 * Profile page — view and edit the user's mental health profile.
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { getProfile, updateProfile, UserProfile } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

const SLEEP_OPTIONS = ["< 5 hours", "5-6 hours", "6-7 hours", "7-8 hours", "> 8 hours"];
const EXERCISE_OPTIONS = ["Never", "1-2x/week", "3-4x/week", "5+/week", "Daily"];
const SUPPORT_OPTIONS = ["None", "Low", "Moderate", "Strong"];
const PERSONALITY_OPTIONS = ["Introvert", "Extrovert", "Ambivert"];
const BASELINE_EMOTIONS = ["joy", "neutral", "sadness", "anxiety", "anger", "fear", "stress"];
const TRIGGER_KEYS = ["work", "relationships", "finances", "health", "social", "academic", "family"];

const EMPTY: UserProfile = {
  age: undefined,
  gender: "",
  occupation: "",
  stress_level: undefined,
  sleep_pattern: "",
  triggers: {},
  personality_type: "",
  baseline_emotion: "",
  exercise_frequency: "",
  social_support: "",
  coping_strategies: "",
};

export default function ProfilePage() {
  const router = useRouter();
  const [form, setForm] = useState<UserProfile>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    getProfile()
      .then((p) => setForm({ ...EMPTY, ...p }))
      .catch(() => {/* no profile yet — use empty form */})
      .finally(() => setLoading(false));
  }, [router]);

  const set = (field: keyof UserProfile, value: unknown) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const toggleTrigger = (key: string) =>
    setForm((prev) => ({
      ...prev,
      triggers: { ...prev.triggers, [key]: !prev.triggers?.[key] },
    }));

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile(form);
      toast.success("Profile saved!");
    } catch {
      toast.error("Failed to save profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="animate-pulse text-center space-y-2">
          <div className="text-4xl">👤</div>
          <p>Loading profile…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-2xl mx-auto space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Your Profile</h1>
          <p className="text-sm text-gray-400 mt-1">
            This information helps personalize your wellness experience.
          </p>
        </div>

        {/* Basic Info */}
        <section className="rounded-xl border border-glass-border bg-glass p-5 backdrop-blur-sm space-y-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Basic Info</h2>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Age"
              type="number"
              value={form.age ?? ""}
              onChange={(e) => set("age", e.target.value ? Number(e.target.value) : undefined)}
              placeholder="e.g. 25"
            />
            <div>
              <label className="block text-xs text-gray-400 mb-1">Gender</label>
              <select
                value={form.gender ?? ""}
                onChange={(e) => set("gender", e.target.value)}
                className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Select</option>
                {["Male", "Female", "Non-binary", "Prefer not to say"].map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            </div>
          </div>
          <Input
            label="Occupation"
            value={form.occupation ?? ""}
            onChange={(e) => set("occupation", e.target.value)}
            placeholder="e.g. Software Engineer"
          />
        </section>

        {/* Emotional History */}
        <section className="rounded-xl border border-glass-border bg-glass p-5 backdrop-blur-sm space-y-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Emotional History</h2>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Baseline Emotion</label>
            <select
              value={form.baseline_emotion ?? ""}
              onChange={(e) => set("baseline_emotion", e.target.value)}
              className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">Select your usual emotional state</option>
              {BASELINE_EMOTIONS.map((e) => (
                <option key={e} value={e}>{e.charAt(0).toUpperCase() + e.slice(1)}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-2">
              Stress Level: <span className="text-gray-200">{form.stress_level ?? "–"}/10</span>
            </label>
            <input
              type="range"
              min={1}
              max={10}
              value={form.stress_level ?? 5}
              onChange={(e) => set("stress_level", Number(e.target.value))}
              className="w-full accent-brand-500"
            />
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>Low (1)</span><span>High (10)</span>
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Personality Type</label>
            <select
              value={form.personality_type ?? ""}
              onChange={(e) => set("personality_type", e.target.value)}
              className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">Select</option>
              {PERSONALITY_OPTIONS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
        </section>

        {/* Triggers */}
        <section className="rounded-xl border border-glass-border bg-glass p-5 backdrop-blur-sm space-y-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Triggers</h2>
          <p className="text-xs text-gray-500">Select the areas that often cause stress or negative emotions.</p>
          <div className="flex flex-wrap gap-2">
            {TRIGGER_KEYS.map((key) => (
              <button
                key={key}
                onClick={() => toggleTrigger(key)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                  form.triggers?.[key]
                    ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                    : "border-glass-border text-gray-400 hover:text-gray-200 hover:border-gray-500"
                }`}
              >
                {key.charAt(0).toUpperCase() + key.slice(1)}
              </button>
            ))}
          </div>
        </section>

        {/* Lifestyle Habits */}
        <section className="rounded-xl border border-glass-border bg-glass p-5 backdrop-blur-sm space-y-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Lifestyle Habits</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Sleep Pattern</label>
              <select
                value={form.sleep_pattern ?? ""}
                onChange={(e) => set("sleep_pattern", e.target.value)}
                className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Select</option>
                {SLEEP_OPTIONS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Exercise Frequency</label>
              <select
                value={form.exercise_frequency ?? ""}
                onChange={(e) => set("exercise_frequency", e.target.value)}
                className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Select</option>
                {EXERCISE_OPTIONS.map((ex) => (
                  <option key={ex} value={ex}>{ex}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Social Support Level</label>
            <select
              value={form.social_support ?? ""}
              onChange={(e) => set("social_support", e.target.value)}
              className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">Select</option>
              {SUPPORT_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Coping Strategies</label>
            <textarea
              value={form.coping_strategies ?? ""}
              onChange={(e) => set("coping_strategies", e.target.value)}
              rows={3}
              placeholder="e.g. meditation, journaling, exercise, talking to friends…"
              className="w-full resize-none rounded-xl border border-glass-border bg-white/5 px-4 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
        </section>

        <Button onClick={handleSave} loading={saving} className="w-full">
          Save Profile
        </Button>
      </div>
    </div>
  );
}
