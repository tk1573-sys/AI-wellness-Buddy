/**
 * Chat API utilities.
 *
 * Wraps the backend /api/v1/chat, /api/v1/profile, and /api/v1/dashboard
 * endpoints. Every request attaches the stored JWT via the `token` query
 * parameter that the backend expects.
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
  reply: string;
  primary_emotion: string;
  confidence: number;
  is_high_risk: boolean;
  escalation_message: string | null;
  scores?: EmotionScore[];
  // Personalization fields
  personalization_score: number;
  used_triggers: string[];
  response_type: "generic" | "personalized";
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
// Helper — builds an axios instance with the token attached
// -------------------------------------------------------------------------- //

function authedParams(): { token: string } {
  const token = getToken();
  if (!token) {
    throw new Error("Not authenticated. Please log in.");
  }
  return { token };
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

// -------------------------------------------------------------------------- //
// Chat API functions
// -------------------------------------------------------------------------- //

export async function sendMessage(
  message: string,
  sessionId?: string,
  languagePreference?: string,
): Promise<ChatResponse> {
  const params = authedParams();
  const { data } = await axios.post<ChatResponse>(
    `${API_URL}/api/v1/chat`,
    { message, session_id: sessionId ?? null, language_preference: languagePreference ?? "english" },
    {
      params,
      headers: { Authorization: `Bearer ${params.token}` },
    },
  );
  return data;
}

export async function getChatHistory(): Promise<ChatMessage[]> {
  const params = authedParams();
  const { data } = await axios.get<ChatMessage[]>(
    `${API_URL}/api/v1/chat/history`,
    {
      params,
      headers: { Authorization: `Bearer ${params.token}` },
    },
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Profile API functions
// -------------------------------------------------------------------------- //

export async function getProfile(): Promise<UserProfile> {
  const params = authedParams();
  const { data } = await axios.get<UserProfile>(
    `${API_URL}/api/v1/profile`,
    { params, headers: { Authorization: `Bearer ${params.token}` } },
  );
  return data;
}

export async function createProfile(profile: UserProfile): Promise<UserProfile> {
  const params = authedParams();
  const { data } = await axios.post<UserProfile>(
    `${API_URL}/api/v1/profile`,
    profile,
    { params, headers: { Authorization: `Bearer ${params.token}` } },
  );
  return data;
}

export async function updateProfile(profile: UserProfile): Promise<UserProfile> {
  const params = authedParams();
  const { data } = await axios.put<UserProfile>(
    `${API_URL}/api/v1/profile`,
    profile,
    { params, headers: { Authorization: `Bearer ${params.token}` } },
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Dashboard API functions
// -------------------------------------------------------------------------- //

export async function getDashboard(): Promise<DashboardData> {
  const params = authedParams();
  const { data } = await axios.get<DashboardData>(
    `${API_URL}/api/v1/dashboard`,
    { params, headers: { Authorization: `Bearer ${params.token}` } },
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
  const params = authedParams();
  const { data } = await axios.get<JourneyData>(
    `${API_URL}/api/v1/journey`,
    { params, headers: { Authorization: `Bearer ${params.token}` } },
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
  const params = authedParams();
  const { data } = await axios.get<WeeklyReportData>(
    `${API_URL}/api/v1/weekly-report`,
    { params, headers: { Authorization: `Bearer ${params.token}` } },
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
  const params = authedParams();
  const form = new FormData();
  form.append("audio", audioBlob, "recording.wav");
  form.append("language_preference", languagePreference);
  const { data } = await axios.post<{ transcript: string; language_used: string }>(
    `${API_URL}/api/v1/voice/transcribe`,
    form,
    {
      params,
      headers: {
        Authorization: `Bearer ${params.token}`,
        "Content-Type": "multipart/form-data",
      },
    },
  );
  return data.transcript;
}

export async function getTts(
  text: string,
  languagePreference: string = "english",
): Promise<Blob> {
  const params = authedParams();
  const { data } = await axios.post(
    `${API_URL}/api/v1/voice/tts`,
    { text, language_preference: languagePreference },
    {
      params,
      headers: { Authorization: `Bearer ${params.token}` },
      responseType: "blob",
    },
  );
  return data as Blob;
}
