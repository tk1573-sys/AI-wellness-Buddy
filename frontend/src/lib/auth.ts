/**
 * Authentication utilities.
 *
 * JWT tokens are stored as HttpOnly cookies set by the backend.
 * The browser sends the cookie automatically with every credentialed request.
 * A lightweight non-HttpOnly presence flag (`wb_logged_in`) lets the frontend
 * know whether a session exists without exposing the token to JavaScript.
 */

import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Non-HttpOnly cookie name used only as a client-side "logged-in" flag. */
const SESSION_FLAG = "wb_logged_in";

/** Returns true when the logged-in flag cookie is present. */
export function isAuthenticated(): boolean {
  return Cookies.get(SESSION_FLAG) === "1";
}

/** @deprecated Token is now stored in an HttpOnly cookie.  Returns null. */
export function getToken(): string | null {
  return null;
}

/**
 * Authenticates an existing user.
 * The backend sets the HttpOnly `wb_access_token` cookie in the response.
 * We set a non-HttpOnly presence flag so the frontend can detect the session.
 * Throws an Error with the server's detail message on failure.
 */
export async function loginUser(email: string, password: string): Promise<void> {
  await axios.post(
    `${API_URL}/api/v1/auth/login`,
    { email, password },
    { withCredentials: true },
  );
  Cookies.set(SESSION_FLAG, "1", { sameSite: "strict" });
}

/**
 * Registers a new user.
 * The backend sets the HttpOnly `wb_access_token` cookie in the response.
 * Throws an Error with the server's detail message on failure.
 */
export async function signupUser(
  email: string,
  username: string,
  password: string,
): Promise<void> {
  await axios.post(
    `${API_URL}/api/v1/auth/signup`,
    { email, username, password },
    { withCredentials: true },
  );
  Cookies.set(SESSION_FLAG, "1", { sameSite: "strict" });
}

/**
 * Signs the user out by calling the backend logout endpoint (clears the
 * HttpOnly cookie server-side) and removing the presence flag.
 */
export async function logoutUser(): Promise<void> {
  try {
    await axios.post(
      `${API_URL}/api/v1/auth/logout`,
      {},
      { withCredentials: true },
    );
  } catch {
    // Best-effort — clear the flag regardless of server response.
  } finally {
    Cookies.remove(SESSION_FLAG);
  }
}
