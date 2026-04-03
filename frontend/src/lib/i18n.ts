export type LanguagePreference = "english" | "tamil" | "bilingual";

const translations: Record<string, Record<LanguagePreference, string>> = {
  // Voice / TTS
  "chat.voice.start": {
    english: "Start Voice",
    tamil: "குரல் தொடங்கு",
    bilingual: "Start Voice / குரல் தொடங்கு",
  },
  "chat.voice.stop": {
    english: "Stop Voice",
    tamil: "குரல் நிறுத்து",
    bilingual: "Stop Voice / குரல் நிறுத்து",
  },
  "chat.tts.replay": {
    english: "Replay",
    tamil: "மீண்டும் இயக்கு",
    bilingual: "Replay / மீண்டும் இயக்கு",
  },

  // Breathing
  "breathing.inhale": {
    english: "Inhale",
    tamil: "உள்ளிழுக்கவும்",
    bilingual: "Inhale / உள்ளிழுக்கவும்",
  },
  "breathing.hold": {
    english: "Hold",
    tamil: "பிடித்துக்கொள்",
    bilingual: "Hold / பிடித்துக்கொள்",
  },
  "breathing.exhale": {
    english: "Exhale",
    tamil: "வெளியே விடவும்",
    bilingual: "Exhale / வெளியே விடவும்",
  },

  // Ambient soundscapes (problem-statement keys)
  "ambient.rain": {
    english: "Rain",
    tamil: "மழை",
    bilingual: "Rain / மழை",
  },
  "ambient.focus": {
    english: "Focus",
    tamil: "கவனம்",
    bilingual: "Focus / கவனம்",
  },
  "ambient.waves": {
    english: "Waves",
    tamil: "அலைகள்",
    bilingual: "Waves / அலைகள்",
  },

  // Ambient soundscapes (in-app keys)
  "ambient.deep_focus": {
    english: "Deep Focus",
    tamil: "ஆழமான கவனம்",
    bilingual: "Deep Focus / ஆழமான கவனம்",
  },
  "ambient.calm_waves": {
    english: "Calm Waves",
    tamil: "அமைதியான அலைகள்",
    bilingual: "Calm Waves / அமைதியான அலைகள்",
  },
  "ambient.soft_rain": {
    english: "Soft Rain",
    tamil: "மென்மையான மழை",
    bilingual: "Soft Rain / மென்மையான மழை",
  },
  "ambient.forest": {
    english: "Forest",
    tamil: "காடு",
    bilingual: "Forest / காடு",
  },
  "ambient.title": {
    english: "Ambient Sound",
    tamil: "சூழல் ஒலி",
    bilingual: "Ambient Sound / சூழல் ஒலி",
  },
  "ambient.volume": {
    english: "Volume",
    tamil: "ஒலி அளவு",
    bilingual: "Volume / ஒலி அளவு",
  },

  // Chat UI
  "chat.breathing.prompt": {
    english: "Breathe",
    tamil: "மூச்சு",
    bilingual: "Breathe / மூச்சு",
  },
  "chat.breathing.start": {
    english: "Start Breathing",
    tamil: "மூச்சு தொடங்கு",
    bilingual: "Start Breathing / மூச்சு தொடங்கு",
  },
  "chat.breathing.stop": {
    english: "Stop Breathing",
    tamil: "மூச்சு நிறுத்து",
    bilingual: "Stop Breathing / மூச்சு நிறுத்து",
  },
  "chat.language.label": {
    english: "Language",
    tamil: "மொழி",
    bilingual: "Language / மொழி",
  },
  "chat.placeholder": {
    english: "Type a message…",
    tamil: "ஒரு செய்தி தட்டச்சு செய்யுங்கள்…",
    bilingual: "Type a message… / ஒரு செய்தி தட்டச்சு செய்யுங்கள்…",
  },
  "chat.send": {
    english: "Send",
    tamil: "அனுப்பு",
    bilingual: "Send / அனுப்பு",
  },
  "chat.welcome.title": {
    english: "Welcome",
    tamil: "வரவேற்கிறோம்",
    bilingual: "Welcome / வரவேற்கிறோம்",
  },
  "chat.welcome.subtitle": {
    english: "How are you feeling?",
    tamil: "நீங்கள் எப்படி உணர்கிறீர்கள்?",
    bilingual: "How are you feeling? / நீங்கள் எப்படி உணர்கிறீர்கள்?",
  },

  // Profile / onboarding fields
  age: {
    english: "Age",
    tamil: "வயது",
    bilingual: "Age / வயது",
  },
  baseline_emotion: {
    english: "Baseline Emotion",
    tamil: "அடிப்படை உணர்வு",
    bilingual: "Baseline Emotion / அடிப்படை உணர்வு",
  },
  coping_strategies: {
    english: "Coping Strategies",
    tamil: "சமாளிக்கும் உத்திகள்",
    bilingual: "Coping Strategies / சமாளிக்கும் உத்திகள்",
  },
  exercise_frequency: {
    english: "Exercise Frequency",
    tamil: "உடற்பயிற்சி அதிர்வெண்",
    bilingual: "Exercise Frequency / உடற்பயிற்சி அதிர்வெண்",
  },
  family_background: {
    english: "Family Background",
    tamil: "குடும்ப பின்னணி",
    bilingual: "Family Background / குடும்ப பின்னணி",
  },
  family_responsibilities: {
    english: "Family Responsibilities",
    tamil: "குடும்ப பொறுப்புகள்",
    bilingual: "Family Responsibilities / குடும்ப பொறுப்புகள்",
  },
  gender: {
    english: "Gender",
    tamil: "பாலினம்",
    bilingual: "Gender / பாலினம்",
  },
  language_preference: {
    english: "Language Preference",
    tamil: "மொழி விருப்பம்",
    bilingual: "Language Preference / மொழி விருப்பம்",
  },
  living_situation: {
    english: "Living Situation",
    tamil: "வாழும் நிலை",
    bilingual: "Living Situation / வாழும் நிலை",
  },
  marital_status: {
    english: "Marital Status",
    tamil: "திருமண நிலை",
    bilingual: "Marital Status / திருமண நிலை",
  },
  occupation: {
    english: "Occupation",
    tamil: "தொழில்",
    bilingual: "Occupation / தொழில்",
  },
  personality_type: {
    english: "Personality Type",
    tamil: "ஆளுமை வகை",
    bilingual: "Personality Type / ஆளுமை வகை",
  },
  response_style: {
    english: "Response Style",
    tamil: "பதில் பாணி",
    bilingual: "Response Style / பதில் பாணி",
  },
  safety_check: {
    english: "Safety Check",
    tamil: "பாதுகாப்பு சரிபார்ப்பு",
    bilingual: "Safety Check / பாதுகாப்பு சரிபார்ப்பு",
  },
  sleep_pattern: {
    english: "Sleep Pattern",
    tamil: "தூக்க முறை",
    bilingual: "Sleep Pattern / தூக்க முறை",
  },
  social_support: {
    english: "Social Support",
    tamil: "சமூக ஆதரவு",
    bilingual: "Social Support / சமூக ஆதரவு",
  },
  stress_level: {
    english: "Stress Level",
    tamil: "மன அழுத்த நிலை",
    bilingual: "Stress Level / மன அழுத்த நிலை",
  },
};

/**
 * Returns the translated string for a given key and language.
 * Falls back to the key itself when no translation is defined.
 */
export function t(key: string, language: LanguagePreference = "english"): string {
  return translations[key]?.[language] ?? key;
}

/** Returns the full display label for a language preference. */
export function langLabel(language: LanguagePreference): string {
  switch (language) {
    case "english":
      return "English";
    case "tamil":
      return "தமிழ்";
    case "bilingual":
      return "English / தமிழ்";
  }
}

/** Returns a short display label for a language preference. */
export function langShortLabel(language: LanguagePreference): string {
  switch (language) {
    case "english":
      return "EN";
    case "tamil":
      return "TA";
    case "bilingual":
      return "EN/TA";
  }
}
