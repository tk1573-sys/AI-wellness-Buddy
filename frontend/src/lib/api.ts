/**
 * Chat API utilities.
 *
 * Wraps the backend /api/v1/chat, /api/v1/profile, and /api/v1/dashboard
 * endpoints. Every request attaches the stored JWT via the Authorization:
 * Bearer header — tokens are never passed as URL query parameters.
 */

import axios from "axios";
import { getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// -------------------------------------------------------------------------- //
// Shared types (mirror the backend Pydantic schemas)
// -------------------------------------------------------------------------- //

export interface ChatMessage {
  role: string;
  content: string;
  emotion?: string | null;
  created_at?: string | null;
}

export interface EmotionScore {
  emotion: string;
  score: number;
}

export interface ChatResponse {
  session_id: string;
  reply?: string;
  response?: string;
  message?: string;
  bot_response?: string;
  response_text?: string;
  text?: string;
  primary_emotion: string;
  confidence: number;
  is_high_risk: boolean;
  escalation_message: string | null;
  scores?: EmotionScore[];
  // Personalization fields
  personalization_score?: number;
  used_triggers?: string[];
  response_type?: "generic" | "personalized";
}

export interface UserProfile {
  id?: number;
  user_id?: number;
  age?: number | null;
  gender?: string | null;
  occupation?: string | null;
  stress_level?: number | null;
  sleep_pattern?: string | null;
  triggers?: Record<string, boolean> | null;
  personality_type?: string | null;
  baseline_emotion?: string | null;
  exercise_frequency?: string | null;
  social_support?: string | null;
  coping_strategies?: string | null;
  // Extended personal history
  marital_status?: string | null;
  living_situation?: string | null;
  family_responsibilities?: string | null;
  family_background?: string | null;
  trauma_history?: string[] | null;
  response_style?: string | null;
  safety_check?: boolean | null;
  personal_triggers?: string[] | null;
  language_preference?: string | null;
  // Guardian / emergency escalation settings
  enable_guardian_alerts?: boolean;
  guardian_consent_given?: boolean;
  guardian_name?: string | null;
  guardian_email?: string | null;
  guardian_whatsapp?: string | null;
  guardian_relationship?: string | null;
}

export interface EmotionPoint {
  timestamp: string;
  emotion: string;
  confidence: number;
  is_high_risk: boolean;
}

export interface EmotionDistribution {
  emotion: string;
  count: number;
}

export interface RiskAlert {
  level: string;
  message: string;
  timestamp: string;
}

export interface DashboardData {
  emotion_trend: EmotionPoint[];
  emotion_distribution: EmotionDistribution[];
  risk_alerts: RiskAlert[];
  mood_trend: string;
  escalation_detected: boolean;
  total_sessions: number;
}

// -------------------------------------------------------------------------- //
// Helper — builds axios Authorization header from the stored JWT.
// Tokens are sent only in the Authorization header, never in the URL.
// -------------------------------------------------------------------------- //

function authedHeaders(): Record<string, string> {
  const token = getToken();
  if (!token) {
    throw new Error("Not authenticated. Please log in.");
  }
  return { Authorization: `Bearer ${token}` };
}

// -------------------------------------------------------------------------- //
// Helper — extracts a human-readable message from any thrown value.
// AxiosErrors carry the server's `detail` field; fall back to err.message.
// -------------------------------------------------------------------------- //

export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (detail) {
      return Array.isArray(detail)
        ? detail.map((d: { msg?: string }) => d.msg ?? String(d)).join("; ")
        : String(detail);
    }
    return err.message;
  }
  return err instanceof Error ? err.message : "Something went wrong.";
}

/**
 * Extracts bot reply text from ChatResponse, supporting multiple possible keys.
 */
function extractBotReply(data: ChatResponse): string {
  // Try all possible response keys in order of preference
  const reply =
    data.reply ??
    data.response ??
    data.message ??
    data.bot_response ??
    data.response_text ??
    data.text ??
    "I'm here with you. Please try again.";

  return reply;
}

// -------------------------------------------------------------------------- //
// Chat API functions
// -------------------------------------------------------------------------- //

// -------------------------------------------------------------------------- //
// Normalise the reply field — the backend may return the assistant text
// under any of the following keys depending on version or model adapter.
// -------------------------------------------------------------------------- //

function normalizeChatResponse(raw: Record<string, unknown>): ChatResponse {
  const reply = (
    (raw.reply as string | undefined) ||
    (raw.response as string | undefined) ||
    (raw.message as string | undefined) ||
    (raw.bot_response as string | undefined) ||
    (raw.response_text as string | undefined) ||
    ""
  );
  return {
    session_id:           String(raw.session_id           ?? ""),
    reply,
    primary_emotion:      String(raw.primary_emotion      ?? "neutral"),
    confidence:           Number(raw.confidence           ?? 0),
    is_high_risk:         Boolean(raw.is_high_risk        ?? false),
    escalation_message:   (raw.escalation_message as string | null) ?? null,
    scores:               (raw.scores                    ?? []) as ChatResponse["scores"],
    personalization_score: Number(raw.personalization_score ?? 0),
    used_triggers:        (raw.used_triggers             ?? []) as string[],
    response_type:        ((raw.response_type as string) === "personalized"
                            ? "personalized"
                            : "generic"),
  };
}

export async function sendMessage(
  message: string,
  sessionId?: string,
  languagePreference?: string,
): Promise<ChatResponse> {
  const { data } = await axios.post<Record<string, unknown>>(
    `${API_URL}/api/v1/chat`,
    { message, session_id: sessionId ?? null, language_preference: languagePreference ?? "english" },
    { headers: authedHeaders() },
  );
<<<<<<< HEAD
  
  // Log the raw API response for debugging
  console.log("CHAT API RESPONSE:", data);
  
  // Ensure we have a valid reply
  if (
    !data.reply &&
    !data.response &&
    !data.message &&
    !data.bot_response &&
    !data.response_text &&
    !data.text
  ) {
    console.warn("No valid response text found in API response. Available fields:", Object.keys(data));
  }
  
  // Extract the bot reply using the helper function
  const reply = extractBotReply(data);
  
  return {
    ...data,
    reply, // Normalize to 'reply' key
  };
=======
  return normalizeChatResponse(data);
>>>>>>> 4362f5eb8d9a4933237299b50fce9fb5d12654d1
}

export async function getChatHistory(): Promise<ChatMessage[]> {
  const { data } = await axios.get<ChatMessage[]>(
    `${API_URL}/api/v1/chat/history`,
    { headers: authedHeaders() },
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Profile API functions
// -------------------------------------------------------------------------- //

export async function getProfile(): Promise<UserProfile> {
  const { data } = await axios.get<UserProfile>(
    `${API_URL}/api/v1/profile`,
    { headers: authedHeaders() },
  );
  return data;
}

export async function createProfile(profile: UserProfile): Promise<UserProfile> {
  const { data } = await axios.post<UserProfile>(
    `${API_URL}/api/v1/profile`,
    profile,
    { headers: authedHeaders() },
  );
  return data;
}

export async function updateProfile(profile: UserProfile): Promise<UserProfile> {
  const { data } = await axios.put<UserProfile>(
    `${API_URL}/api/v1/profile`,
    profile,
    { headers: authedHeaders() },
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Dashboard API functions
// -------------------------------------------------------------------------- //

export async function getDashboard(): Promise<DashboardData> {
  const { data } = await axios.get<DashboardData>(
    `${API_URL}/api/v1/dashboard`,
    { headers: authedHeaders() },
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Journey API types and functions
// -------------------------------------------------------------------------- //

export interface JourneyPoint {
  timestamp: string;
  emotion: string;
  confidence: number;
  risk_score: number;
  is_high_risk: boolean;
}

export interface HeatmapCell {
  hour: number;
  emotion: string;
  intensity: number;
}

export interface MovingAveragePoint {
  index: number;
  avg_risk: number;
}

export interface JourneyData {
  journey_points: JourneyPoint[];
  heatmap: HeatmapCell[];
  moving_average: MovingAveragePoint[];
  latest_risk_score: number;
  stability_index: number;
  volatility_label: string;
  cdi_score: number;
  cdi_level: string;
  total_points: number;
}

export async function getJourney(): Promise<JourneyData> {
  const { data } = await axios.get<JourneyData>(
    `${API_URL}/api/v1/journey`,
    { headers: authedHeaders() },
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Weekly Report API types and functions
// -------------------------------------------------------------------------- //

export interface DailyCount {
  date: string;
  count: number;
  dominant_emotion: string;
  avg_confidence: number;
}

export interface WeeklySessionSummary {
  timestamp: string;
  dominant_emotion: string;
  confidence: number;
  is_high_risk: boolean;
}

export interface WeeklyEmotionCount {
  emotion: string;
  count: number;
}

export interface WeeklyReportData {
  summary_text: string;
  daily_breakdown: DailyCount[];
  session_summaries: WeeklySessionSummary[];
  emotion_distribution: WeeklyEmotionCount[];
  total_sessions: number;
  high_risk_count: number;
  dominant_emotion_week: string;
  mood_direction: string;
}

export async function getWeeklyReport(): Promise<WeeklyReportData> {
  const { data } = await axios.get<WeeklyReportData>(
    `${API_URL}/api/v1/weekly-report`,
    { headers: authedHeaders() },
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Voice API functions
// -------------------------------------------------------------------------- //

export async function transcribeVoice(
  audioBlob: Blob,
  languagePreference: string = "english",
): Promise<string> {
  const form = new FormData();
  form.append("audio", audioBlob, "recording.wav");
  form.append("language_preference", languagePreference);
  const { data } = await axios.post<{ transcript: string; language_used: string }>(
    `${API_URL}/api/v1/voice/transcribe`,
    form,
    { headers: authedHeaders() },
  );
  return data.transcript;
}

export async function getTts(
  text: string,
  languagePreference: string = "english",
): Promise<Blob> {
  const { data } = await axios.post(
    `${API_URL}/api/v1/voice/tts`,
    { text, language_preference: languagePreference },
    {
      headers: authedHeaders(),
      responseType: "blob",
    },
  );
  return data as Blob;
}

// -------------------------------------------------------------------------- //
// Guardian Alert API types and functions
// -------------------------------------------------------------------------- //

export interface GuardianAlertRecord {
  id: number;
  user_id: number;
  risk_level: string;
  risk_reason: string | null;
  channel: string;
  delivery_status: string;
  is_test: boolean;
  timestamp: string;
}

export interface GuardianAlertListResponse {
  alerts: GuardianAlertRecord[];
  total: number;
}

export interface GuardianAlertTriggerRequest {
  risk_level: "high" | "critical";
  risk_reason?: string | null;
  channels: Array<"email" | "whatsapp">;
  // Set to true for test/verification — no real notification is sent
  is_test?: boolean;
}

export async function triggerGuardianAlert(
  req: GuardianAlertTriggerRequest,
): Promise<GuardianAlertRecord[]> {
  const { data } = await axios.post<GuardianAlertRecord[]>(
    `${API_URL}/api/v1/guardian-alert`,
    req,
    { headers: authedHeaders() },
  );
  return data;
}

export async function getGuardianAlerts(): Promise<GuardianAlertListResponse> {
  const { data } = await axios.get<GuardianAlertListResponse>(
    `${API_URL}/api/v1/guardian-alert`,
    { headers: authedHeaders() },
  );
  return data;
}
