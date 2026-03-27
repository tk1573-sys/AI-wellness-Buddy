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

export interface ChatResponse {
  session_id: string;
  reply: string;
  primary_emotion: string;
  confidence: number;
  is_high_risk: boolean;
  escalation_message: string | null;
  scores?: Array<Record<string, unknown>>;
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
// Chat API functions
// -------------------------------------------------------------------------- //

export async function sendMessage(
  message: string,
  sessionId?: string,
): Promise<ChatResponse> {
  const params = authedParams();
  const { data } = await axios.post<ChatResponse>(
    `${API_URL}/api/v1/chat`,
    { message, session_id: sessionId ?? null },
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
