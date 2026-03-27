/**
 * Chat API utilities.
 *
 * Wraps the backend /api/v1/chat endpoints.  Every request attaches the stored
 * JWT via the `token` query parameter that the backend expects.
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
// API functions
// -------------------------------------------------------------------------- //

/**
 * Sends a user message to the AI Wellness Buddy.
 *
 * @param message   The user's text.
 * @param sessionId Optional existing session ID to continue a conversation.
 * @returns         The assistant's response with emotion analysis.
 */
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

/**
 * Fetches the authenticated user's chat history.
 *
 * @returns Array of chat messages ordered oldest-first.
 */
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
