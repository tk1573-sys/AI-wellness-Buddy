/**
 * Onboarding — multi-step profile setup shown after signup.
 *
 * Step 1: Basic Info
 * Step 2: Emotional History
 * Step 3: Trigger Identification
 * Step 4: Lifestyle Habits
 * Step 5: Personal Background (language, family, trauma, safety)
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { clsx } from "clsx";
import { createProfile, UserProfile } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
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

const STEPS = [
  { title: "Basic Info", description: "Tell us a bit about yourself" },
  { title: "Emotional History", description: "Help us understand your emotional baseline" },
  { title: "Trigger Identification", description: "What tends to affect your mood?" },
  { title: "Lifestyle Habits", description: "Your daily habits shape your wellbeing" },
  { title: "Personal Background", description: "Optional context to personalize support" },
  { title: "Guardian Alerts", description: "Optional safety net during high-risk moments" },
];

const EMPTY: UserProfile = {
  age: undefined,
  gender: "",
  occupation: "",
  stress_level: 5,
  sleep_pattern: "",
  triggers: {},
  personality_type: "",
  baseline_emotion: "",
  exercise_frequency: "",
  social_support: "",
  coping_strategies: "",
  // Extended
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

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<UserProfile>(EMPTY);
  const [traumaInput, setTraumaInput] = useState("");
  const [personalTriggerInput, setPersonalTriggerInput] = useState("");
  const [saving, setSaving] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);

  const set = (field: keyof UserProfile, value: unknown) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const toggleTrigger = (key: string) =>
    setForm((prev) => ({
      ...prev,
      triggers: { ...prev.triggers, [key]: !prev.triggers?.[key] },
    }));

  const handleNext = () => {
    if (step < STEPS.length - 1) setStep((s) => s + 1);
  };
  const handleBack = () => {
    if (step > 0) setStep((s) => s - 1);
  };

  const handleFinish = async () => {
    setSaving(true);
    try {
      // Merge trauma and personal trigger freetext inputs if any
      const finalForm: UserProfile = {
        ...form,
        trauma_history:
          traumaInput.trim()
            ? [...(form.trauma_history ?? []), traumaInput.trim()]
            : form.trauma_history,
        personal_triggers:
          personalTriggerInput.trim()
            ? [
                ...(form.personal_triggers ?? []),
                ...personalTriggerInput.split(",").map((s) => s.trim()).filter(Boolean),
              ]
            : form.personal_triggers,
      };
      await createProfile(finalForm);
      toast.success("Profile saved! Welcome 🌟");
      router.replace("/chat");
    } catch {
      toast.error("Failed to save profile. You can update it later in Settings.");
      router.replace("/chat");
    } finally {
      setSaving(false);
    }
  };

  const handleSkip = () => {
    router.replace("/chat");
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      {/* Background blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-brand-600/10 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 rounded-full bg-purple-600/10 blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <span className="text-5xl">🌟</span>
          <h1 className="text-2xl font-bold text-gray-100 mt-3">Set Up Your Profile</h1>
          <p className="text-gray-400 text-sm mt-1">
            Help us personalize your wellness experience
          </p>
        </div>

        {/* Progress indicator */}
        <div className="flex items-center gap-2 mb-6">
          {STEPS.map((s, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div
                className={clsx(
                  "h-1.5 w-full rounded-full transition-colors",
                  i <= step ? "bg-brand-500" : "bg-gray-700"
                )}
              />
              <span className={clsx("text-[10px] hidden sm:block", i === step ? "text-brand-400" : "text-gray-600")}>
                {s.title}
              </span>
            </div>
          ))}
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-glass-border bg-glass p-6 backdrop-blur-sm space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-100">{STEPS[step].title}</h2>
            <p className="text-xs text-gray-400">{STEPS[step].description}</p>
          </div>

          {/* Step 1: Basic Info */}
          {step === 0 && (
            <div className="space-y-4">
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
                placeholder="e.g. Software Engineer, Student…"
              />
            </div>
          )}

          {/* Step 2: Emotional History */}
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Usual Emotional State</label>
                <select
                  value={form.baseline_emotion ?? ""}
                  onChange={(e) => set("baseline_emotion", e.target.value)}
                  className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  <option value="">Select your baseline emotion</option>
                  {BASELINE_EMOTIONS.map((e) => (
                    <option key={e} value={e}>{e.charAt(0).toUpperCase() + e.slice(1)}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-2">
                  Current Stress Level: <span className="text-gray-200">{form.stress_level}/10</span>
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
                  <span>Very Low (1)</span><span>Very High (10)</span>
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Personality Type</label>
                <div className="flex gap-2">
                  {PERSONALITY_OPTIONS.map((p) => (
                    <button
                      key={p}
                      onClick={() => set("personality_type", p)}
                      className={clsx(
                        "flex-1 py-2 rounded-xl text-sm border transition-colors",
                        form.personality_type === p
                          ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                          : "border-glass-border text-gray-400 hover:text-gray-200"
                      )}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Triggers */}
          {step === 2 && (
            <div className="space-y-4">
              <p className="text-xs text-gray-500">Select all that apply to you.</p>
              <div className="flex flex-wrap gap-2">
                {TRIGGER_KEYS.map((key) => (
                  <button
                    key={key}
                    onClick={() => toggleTrigger(key)}
                    className={clsx(
                      "px-4 py-2 rounded-full text-sm border transition-colors",
                      form.triggers?.[key]
                        ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                        : "border-glass-border text-gray-400 hover:text-gray-200"
                    )}
                  >
                    {key.charAt(0).toUpperCase() + key.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 4: Lifestyle */}
          {step === 3 && (
            <div className="space-y-4">
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
                  <label className="block text-xs text-gray-400 mb-1">Exercise</label>
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
                  placeholder="e.g. meditation, journaling, exercise…"
                  className="w-full resize-none rounded-xl border border-glass-border bg-white/5 px-4 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
            </div>
          )}

          {/* Step 5: Personal Background */}
          {step === 4 && (
            <div className="space-y-4">
              {/* Language preference */}
              <div>
                <label className="block text-xs text-gray-400 mb-1">Preferred Language / மொழி</label>
                <div className="flex gap-2">
                  {LANG_OPTIONS.map((lang) => (
                    <button
                      key={lang}
                      type="button"
                      onClick={() => set("language_preference", lang)}
                      className={clsx(
                        "flex-1 py-2 rounded-xl text-xs border transition-colors",
                        form.language_preference === lang
                          ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                          : "border-glass-border text-gray-400 hover:text-gray-200"
                      )}
                    >
                      {langLabel(lang)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Response style */}
              <div>
                <label className="block text-xs text-gray-400 mb-1">Preferred Response Style</label>
                <div className="grid grid-cols-2 gap-2">
                  {RESPONSE_STYLE_OPTIONS.map((style) => (
                    <button
                      key={style}
                      type="button"
                      onClick={() => set("response_style", style)}
                      className={clsx(
                        "py-2 rounded-xl text-xs border transition-colors",
                        form.response_style === style
                          ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                          : "border-glass-border text-gray-400 hover:text-gray-200"
                      )}
                    >
                      {style}
                    </button>
                  ))}
                </div>
              </div>

              {/* Marital + Living */}
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

              {/* Family responsibilities */}
              <div>
                <label className="block text-xs text-gray-400 mb-1">Family Responsibilities</label>
                <div className="flex flex-wrap gap-2">
                  {RESPONSIBILITIES_OPTIONS.map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => set("family_responsibilities", r)}
                      className={clsx(
                        "px-3 py-1.5 rounded-full text-xs border transition-colors",
                        form.family_responsibilities === r
                          ? "bg-brand-600/30 border-brand-500/50 text-brand-300"
                          : "border-glass-border text-gray-400 hover:text-gray-200"
                      )}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>

              {/* Safety check */}
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
                      className={clsx(
                        "flex-1 py-1.5 rounded-xl text-xs border transition-colors",
                        form.safety_check === value
                          ? value === false
                            ? "bg-red-900/30 border-red-500/50 text-red-300"
                            : "bg-brand-600/30 border-brand-500/50 text-brand-300"
                          : "border-glass-border text-gray-400 hover:text-gray-200"
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                {form.safety_check === false && (
                  <p className="text-xs text-amber-400 mt-2">
                    🛡️ Your safety matters. If you&apos;re in an unsafe situation, please call{" "}
                    <strong>988</strong> (Suicide &amp; Crisis Lifeline) or text <strong>HOME</strong>{" "}
                    to <strong>741741</strong> (Crisis Text Line, 24/7).
                  </p>
                )}
              </div>

              {/* Personal triggers (free text) */}
              <div>
                <label className="block text-xs text-gray-400 mb-1">
                  Personal Triggers (optional, comma-separated)
                </label>
                <input
                  type="text"
                  value={personalTriggerInput}
                  onChange={(e) => setPersonalTriggerInput(e.target.value)}
                  placeholder="e.g. exam pressure, loneliness, night shifts…"
                  className="w-full rounded-xl border border-glass-border bg-white/5 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              {/* Trauma history */}
              <div>
                <label className="block text-xs text-gray-400 mb-1">
                  Any significant loss or trauma to be aware of? (optional)
                </label>
                <textarea
                  value={traumaInput}
                  onChange={(e) => setTraumaInput(e.target.value)}
                  rows={2}
                  placeholder="This is optional and confidential…"
                  className="w-full resize-none rounded-xl border border-glass-border bg-white/5 px-4 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
            </div>
          )}

          {/* Step 6: Guardian Alerts */}
          {step === 5 && (
            <div className="space-y-4">
              <div className="rounded-xl border border-amber-500/30 bg-amber-900/10 p-4 text-sm text-amber-200 space-y-1">
                <p className="font-medium">🛡️ Optional: Emergency Safety Net</p>
                <p className="text-xs text-gray-400">
                  You can designate a trusted person to be notified if a high-risk distress
                  signal is detected. This is entirely optional and requires your explicit consent.
                </p>
              </div>

              {/* Enable toggle */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-200">Enable guardian notifications</p>
                  <p className="text-xs text-gray-500">Consent required before enabling</p>
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
                <div className="space-y-3 border-t border-amber-500/20 pt-3">
                  <p className="text-xs text-amber-300/80">✅ Consent granted</p>
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
                    label="Guardian WhatsApp"
                    value={form.guardian_whatsapp ?? ""}
                    onChange={(e) => set("guardian_whatsapp", e.target.value)}
                    placeholder="+1234567890"
                  />
                </div>
              )}

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
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between pt-2">
            <div className="flex gap-2">
              {step > 0 && (
                <Button variant="ghost" onClick={handleBack}>
                  ← Back
                </Button>
              )}
              <Button variant="ghost" onClick={handleSkip} className="text-gray-500">
                Skip for now
              </Button>
            </div>

            {step < STEPS.length - 1 ? (
              <Button onClick={handleNext}>
                Next →
              </Button>
            ) : (
              <Button onClick={handleFinish} loading={saving}>
                Finish Setup ✓
              </Button>
            )}
          </div>
        </div>

        <p className="text-center text-xs text-gray-600 mt-4">
          Step {step + 1} of {STEPS.length}
        </p>
      </div>
    </div>
  );
}
