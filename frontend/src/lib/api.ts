/**
 * Chat API utilities.
 *
 * Wraps the backend /api/v1/chat, /api/v1/profile, and /api/v1/dashboard
 * endpoints. JWT authentication is handled via HttpOnly cookies set by the
 * backend — axios sends them automatically with `withCredentials: true`.
 * Tokens are never stored in localStorage or sent as URL query parameters.
 *
 * All requests are routed through the Next.js proxy (next.config.js rewrites)
 * so that the browser always communicates with the same origin, eliminating
 * CORS issues and ensuring HttpOnly cookies are forwarded correctly.
 */

import axios from "axios";

// Axios instance — same-origin requests via the Next.js proxy (/api/:path*).
const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
  // Abort requests that take longer than 15 s to prevent the UI from
  // hanging indefinitely on a slow or unresponsive backend.
  timeout: 15000,
});

// -------------------------------------------------------------------------- //
// Retry helpers
// -------------------------------------------------------------------------- //

const MAX_RETRIES = 2;
const RETRY_DELAY_BASE_MS = 500;

function isRetryable(error: unknown): boolean {
  if (!axios.isAxiosError(error)) return false;
  // Timeouts are not retried — the backend is likely still processing,
  // and a duplicate request could create duplicate data.
  if (error.code === "ECONNABORTED") return false;
  // Genuine network failure (DNS, TCP refused, etc.)
  if (!error.response) return true;
  // Service temporarily unavailable
  if (error.response.status === 503) return true;
  return false;
}

const sleep = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

// -------------------------------------------------------------------------- //
// Global interceptors
// -------------------------------------------------------------------------- //

// Request interceptor — log outgoing requests in development.
api.interceptors.request.use((config) => {
  if (process.env.NODE_ENV === "development") {
    console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  }
  return config;
});

// Response interceptor — log responses, retry on transient errors, and redirect to /login on 401.
api.interceptors.response.use(
  (response) => {
    if (process.env.NODE_ENV === "development") {
      console.debug(
        `[API] ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`,
      );
    }
    return response;
  },
  async (error) => {
    if (process.env.NODE_ENV === "development") {
      console.debug(
        `[API] ERROR ${error.response?.status} ${error.config?.method?.toUpperCase()} ${error.config?.url}`,
        error.response?.data,
      );
    }
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 401 &&
      typeof window !== "undefined" &&
      !window.location.pathname.startsWith("/login") &&
      !window.location.pathname.startsWith("/signup")
    ) {
      console.warn("[API] 401 Unauthorized — redirecting to /login");
      // Use window.location.href for a full navigation reset.  The api module
      // is not a React component, so Next.js router hooks are not available here.
      window.location.href = "/login";
    }

    // Retry transient failures (network errors, 503) up to MAX_RETRIES times.
    if (isRetryable(error) && error.config) {
      type RetryConfig = typeof error.config & { _retryCount?: number };
      const config = error.config as RetryConfig;
      const retryCount = config._retryCount ?? 0;
      if (retryCount < MAX_RETRIES) {
        config._retryCount = retryCount + 1;
        const delay = RETRY_DELAY_BASE_MS * 2 ** retryCount; // retry 1: 500 ms, retry 2: 1000 ms
        console.debug(
          `[API] Retrying (${config._retryCount}/${MAX_RETRIES}) in ${delay} ms…`,
        );
        await sleep(delay);
        return api(config);
      }
    }

    return Promise.reject(error);
  },
);

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
// Helper — extracts a human-readable message from any thrown value.
// AxiosErrors carry the server's `detail` field; fall back to err.message.
// -------------------------------------------------------------------------- //

function extractDetailMessage(detail: unknown): string | null {
  if (!detail) return null;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        if (typeof d === "object" && d !== null) {
          // FastAPI validation errors use { msg, type, loc }
          if ("msg" in d) return String((d as { msg: unknown }).msg);
          // Fallback: stringify the object rather than "[object Object]"
          return JSON.stringify(d);
        }
        return String(d);
      })
      .join("; ");
  }
  if (typeof detail === "object" && "message" in detail) {
    return String((detail as { message: string }).message);
  }
  return String(detail);
}

export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    // Request timed out (ECONNABORTED) — backend is slow or overloaded.
    if (err.code === "ECONNABORTED") {
      return "Server is taking too long. Please try again.";
    }
    // Network failure (no response from server at all)
    if (!err.response) {
      return "Unable to reach the server. Please check your connection and try again.";
    }
    const { status, data } = err.response;
    const detail = data?.detail;
    // 503 — service/database unavailable
    if (status === 503) {
      return (
        extractDetailMessage(detail) ??
        "The service is temporarily unavailable. Please try again in a moment."
      );
    }
    return extractDetailMessage(detail) ?? err.message;
  }
  return err instanceof Error ? err.message : "Something went wrong.";
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
  const { data } = await api.post<Record<string, unknown>>(
    `/v1/chat`,
    { message, session_id: sessionId ?? null, language_preference: languagePreference ?? "english" },
  );
  return normalizeChatResponse(data);
}

export async function getChatHistory(): Promise<ChatMessage[]> {
  const { data } = await api.get<ChatMessage[]>(
    `/v1/chat/history`,
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Profile API functions
// -------------------------------------------------------------------------- //

export async function getProfile(): Promise<UserProfile> {
  const { data } = await api.get<UserProfile>(
    `/v1/profile`,
  );
  return data;
}

export async function createProfile(profile: UserProfile): Promise<UserProfile> {
  const { data } = await api.post<UserProfile>(
    `/v1/profile`,
    profile,
  );
  return data;
}

export async function updateProfile(profile: UserProfile): Promise<UserProfile> {
  const { data } = await api.put<UserProfile>(
    `/v1/profile`,
    profile,
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Dashboard API functions
// -------------------------------------------------------------------------- //

export async function getDashboard(): Promise<DashboardData> {
  const { data } = await api.get<DashboardData>(
    `/v1/dashboard`,
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
  const { data } = await api.get<JourneyData>(
    `/v1/journey`,
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
  const { data } = await api.get<WeeklyReportData>(
    `/v1/weekly-report`,
  );
  return data;
}

// -------------------------------------------------------------------------- //
// Insights API types and functions
// -------------------------------------------------------------------------- //

export interface InsightsData {
  dominant_emotion: string;
  personalization_score: number;
  trigger_signals: string[];
  risk_level: string;
  recent_pattern: Record<string, number>;  // emotion -> percentage (0–100, 1 decimal)
  trend: string;
}

export async function getInsights(): Promise<InsightsData> {
  const { data } = await api.get<InsightsData>(
    `/v1/insights`,
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
  // Use a file extension that matches the blob's MIME type so the backend
  // can correctly detect the audio format for conversion.
  const mimeToExt: Record<string, string> = {
    "audio/wav":  "wav",
    "audio/wave": "wav",
    "audio/webm": "webm",
    "audio/ogg":  "ogg",
    "audio/mp4":  "mp4",
    "audio/mpeg": "mp3",
    "audio/mp3":  "mp3",
    "audio/flac": "flac",
  };
  const ext = mimeToExt[audioBlob.type?.split(";")[0]] ?? "webm";
  const form = new FormData();
  form.append("audio", audioBlob, `recording.${ext}`);
  form.append("language_preference", languagePreference);
  const { data } = await api.post<{ transcript: string; language_used: string }>(
    `/v1/voice/transcribe`,
    form,
  );
  return data.transcript;
}

export async function getTts(
  text: string,
  languagePreference: string = "english",
): Promise<Blob> {
  const { data } = await api.post(
    `/v1/voice/tts`,
    { text, language_preference: languagePreference },
    { responseType: "blob" },
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
  const { data } = await api.post<GuardianAlertRecord[]>(
    `/v1/guardian-alert`,
    req,
  );
  return data;
}

export async function getGuardianAlerts(): Promise<GuardianAlertListResponse> {
  const { data } = await api.get<GuardianAlertListResponse>(
    `/v1/guardian-alert`,
  );
  return data;
}
