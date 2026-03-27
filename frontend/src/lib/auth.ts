/**
 * Authentication utilities.
 *
 * Provides login, signup, logout helpers that call the backend auth endpoints
 * and persist the JWT access token in localStorage.
 */

import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** localStorage key used to store the JWT access token. */
const TOKEN_KEY = "wb_access_token";

/** Returns the stored access token, or null if not present. */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/** Returns true when a token is present in localStorage. */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Authenticates an existing user and stores the returned JWT.
 * Throws an Error with the server's detail message on failure.
 */
export async function loginUser(email: string, password: string): Promise<void> {
  const { data } = await axios.post<{ access_token: string }>(
    `${API_URL}/api/v1/auth/login`,
    { email, password },
  );
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, data.access_token);
  }
}

/**
 * Registers a new user and stores the returned JWT.
 * Throws an Error with the server's detail message on failure.
 */
export async function signupUser(
  email: string,
  username: string,
  password: string,
): Promise<void> {
  const { data } = await axios.post<{ access_token: string }>(
    `${API_URL}/api/v1/auth/signup`,
    { email, username, password },
  );
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, data.access_token);
  }
}

/** Removes the stored token, effectively signing the user out. */
export function logoutUser(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
}
