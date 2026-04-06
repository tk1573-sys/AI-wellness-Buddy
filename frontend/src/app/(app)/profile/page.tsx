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
import { TriggerHistory } from "@/components/dashboard/TriggerHistory";
import { langLabel, type LanguagePreference } from "@/lib/i18n";
import { GuardianConsentModal } from "@/components/guardian/ConsentModal";

const SLEEP_OPTIONS = ["< 5 hours", "5-6 hours", "6-7 hours", "7-8 hours", "> 8 hours"];
const EXERCISE_OPTIONS = ["Never", "1-2x/week", "3-4x/week", "5+/week", "Daily"];
const SUPPORT_OPTIONS = ["None", "Low", "Moderate", "Strong"];
const PERSONALITY_OPTIONS = ["Introvert", "Extrovert", "Ambivert"];
const BASELINE_EMOTIONS = ["joy", "neutral", "sadness", "anxiety", "anger", "fear", "stress"];
const TRIGGER_KEYS = ["work", "relationships", "finances", "health", "social", "academic", "family"];
const MARITAL_OPTIONS = ["Single", "In a relationship", "Married", "Separated", "Divorced", "Widowed", "Prefer not to say"];
const LIVING_OPTIONS = ["Alone", "With family", "With partner", "With roommates", "Dormitory", "Other"];
const RESPONSIBILITIES_OPTIONS = ["None", "Parent", "Caregiver", "Both", "Other"];
const RESPONSE_STYLE_OPTIONS = ["Formal", "Casual", "Empathetic", "Direct"];
const LANG_OPTIONS: LanguagePreference[] = ["english", "tamil", "bilingual"];

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
  marital_status: "",
  living_situation: "",
  family_responsibilities: "",
  family_background: "",
  trauma_history: [],
  response_style: "",
  safety_check: null,
  personal_triggers: [],
  language_preference: "english",
  enable_guardian_alerts: false,
  guardian_consent_given: false,
  guardian_name: "",
  guardian_email: "",
  guardian_whatsapp: "",
  guardian_relationship: "",
};

export default function ProfilePage() {
  const router = useRouter();
  const [form, setForm] = useState<UserProfile>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    getProfile()
      .then((p) => setForm({ ...EMPTY, ...p }))
      .catch(() => setLoadError(true))
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

  if (loadError) {
    // Show a non-fatal warning; user can still fill and save the form below.
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
        {loadError && (
          <div className="rounded-xl border border-amber-500/30 bg-amber-900/20 px-4 py-3 text-sm text-amber-200">
            ⚠️ Could not load your existing profile. You can fill in your details below and save.
          </div>
        )}

        {/* Language Preference */}
        <section className="rounded-xl border border-glass-border bg-glass p-5 backdrop-blur-sm space-y-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Language / மொழி</h2>
          <div className="flex gap-2">
            {LANG_OPTIONS.map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => set("language_preference", lang)}
                className={`flex-1 py-2 rounded-xl text-xs border transition-colors ${
                  form.language_preference === lang
                    ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                    : "border-glass-border text-gray-400 hover:text-gray-200"
                }`}
              >
                {langLabel(lang)}
              </button>
            ))}
          </div>
        </section>

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

        {/* Personal Trigger History */}
        <section className="rounded-xl border border-glass-border bg-glass p-5 backdrop-blur-sm space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Personal Trigger Log</h2>
            <p className="text-xs text-gray-500 mt-1">Free-text triggers captured from your sessions.</p>
          </div>
          <TriggerHistory profile={form} onUpdate={(updated) => setForm({ ...form, ...updated })} />
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

        {/* Extended Personal Background */}
        <section className="rounded-xl border border-glass-border bg-glass p-5 backdrop-blur-sm space-y-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Personal Background</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Relationship Status</label>
              <select
                value={form.marital_status ?? ""}
                onChange={(e) => set("marital_status", e.target.value)}
                className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-xs text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Select (optional)</option>
                {MARITAL_OPTIONS.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Living Situation</label>
              <select
                value={form.living_situation ?? ""}
                onChange={(e) => set("living_situation", e.target.value)}
                className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-xs text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Select (optional)</option>
                {LIVING_OPTIONS.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Family Responsibilities</label>
            <div className="flex flex-wrap gap-2">
              {RESPONSIBILITIES_OPTIONS.map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => set("family_responsibilities", r)}
                  className={`px-3 py-1.5 rounded-full text-xs border transition-colors ${
                    form.family_responsibilities === r
                      ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                      : "border-glass-border text-gray-400 hover:text-gray-200"
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Preferred Response Style</label>
            <div className="grid grid-cols-2 gap-2">
              {RESPONSE_STYLE_OPTIONS.map((style) => (
                <button
                  key={style}
                  type="button"
                  onClick={() => set("response_style", style)}
                  className={`py-1.5 rounded-xl text-xs border transition-colors ${
                    form.response_style === style
                      ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                      : "border-glass-border text-gray-400 hover:text-gray-200"
                  }`}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Family Background (optional)</label>
            <textarea
              value={form.family_background ?? ""}
              onChange={(e) => set("family_background", e.target.value)}
              rows={2}
              placeholder="Any family context that affects your wellbeing…"
              className="w-full resize-none rounded-xl border border-glass-border bg-white/5 px-4 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-2">
              Do you feel safe with your family / guardians? (optional)
            </label>
            <div className="flex gap-3">
              {[
                { label: "Yes", value: true },
                { label: "No", value: false },
                { label: "Prefer not to say", value: null },
              ].map(({ label, value }) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => set("safety_check", value)}
                  className={`flex-1 py-1.5 rounded-xl text-xs border transition-colors ${
                    form.safety_check === value
                      ? value === false
                        ? "bg-red-900/30 border-red-500/50 text-red-300"
                        : "bg-brand-600/30 border-brand-500/50 text-brand-300"
                      : "border-glass-border text-gray-400 hover:text-gray-200"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            {form.safety_check === false && (
              <p className="text-xs text-amber-400 mt-2">
                🛡️ Please reach out to a trusted person or crisis line if you ever feel unsafe.
              </p>
            )}
          </div>
        </section>

        {/* Guardian / Emergency Escalation */}
        <section className="rounded-xl border border-amber-500/30 bg-amber-900/10 p-5 backdrop-blur-sm space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-amber-300 uppercase tracking-wide">🛡️ Guardian Alerts</h2>
            <p className="text-xs text-gray-400 mt-1">
              Designate a trusted person to be notified during high-risk emotional distress.
            </p>
          </div>

          {/* Enable toggle */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-200">Notify my guardian during high-risk emotional distress</p>
              <p className="text-xs text-gray-500">Requires explicit consent and guardian contact info</p>
            </div>
            <button
              type="button"
              onClick={() => {
                if (!form.enable_guardian_alerts) {
                  setShowConsentModal(true);
                } else {
                  set("enable_guardian_alerts", false);
                  set("guardian_consent_given", false);
                }
              }}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                form.enable_guardian_alerts ? "bg-amber-500" : "bg-gray-600"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  form.enable_guardian_alerts ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          {form.enable_guardian_alerts && (
            <div className="space-y-3 pt-1 border-t border-amber-500/20">
              <p className="text-xs text-amber-300/80">
                ✅ Consent given — alerts will be sent when high-risk distress is detected.
              </p>
              <Input
                label="Guardian Name"
                value={form.guardian_name ?? ""}
                onChange={(e) => set("guardian_name", e.target.value)}
                placeholder="e.g. Mom, Dr. Smith"
              />
              <div>
                <label className="block text-xs text-gray-400 mb-1">Relationship</label>
                <select
                  value={form.guardian_relationship ?? ""}
                  onChange={(e) => set("guardian_relationship", e.target.value)}
                  className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  <option value="">Select relationship</option>
                  {["Parent", "Sibling", "Partner", "Friend", "Therapist", "Doctor", "Other"].map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
              <Input
                label="Guardian Email"
                type="email"
                value={form.guardian_email ?? ""}
                onChange={(e) => set("guardian_email", e.target.value)}
                placeholder="guardian@example.com"
              />
              <Input
                label="Guardian WhatsApp Number"
                value={form.guardian_whatsapp ?? ""}
                onChange={(e) => set("guardian_whatsapp", e.target.value)}
                placeholder="+1234567890 (with country code)"
              />
              <p className="text-xs text-gray-500">
                At least one of Email or WhatsApp is required for alerts to be sent.
              </p>
            </div>
          )}
        </section>

        {showConsentModal && (
          <GuardianConsentModal
            onAccept={() => {
              set("enable_guardian_alerts", true);
              set("guardian_consent_given", true);
              setShowConsentModal(false);
            }}
            onDecline={() => setShowConsentModal(false)}
          />
        )}

        <Button onClick={handleSave} loading={saving} className="w-full">
          Save Profile
        </Button>
      </div>
    </div>
  );
}
