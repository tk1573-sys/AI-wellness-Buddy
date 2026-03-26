/**
 * Shared Playwright test helpers and fixtures.
 *
 * Provides:
 *   - apiURL   — the backend base URL
 *   - uniqueEmail / uniqueUsername — helpers to generate unique test credentials
 *   - signupViaAPI / loginViaAPI   — fast API-level auth helpers
 */

import { test as base } from "@playwright/test";

export const apiURL =
  process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000";

/** Generate a unique e-mail address for each test run to avoid conflicts. */
export function uniqueEmail(): string {
  return `e2e_${Date.now()}_${Math.floor(Math.random() * 9999)}@example.com`;
}

/** Generate a unique username (alphanumeric, ≤ 20 chars). */
export function uniqueUsername(): string {
  return `user_${Date.now()}`.slice(0, 20);
}

/** Sign up a user directly through the API and return the access token. */
export async function signupViaAPI(
  email: string,
  username: string,
  password: string
): Promise<string> {
  const res = await fetch(`${apiURL}/api/v1/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, username, password }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Signup failed (${res.status}): ${body}`);
  }
  const data = await res.json();
  return data.access_token as string;
}

/** Log in a user directly through the API and return the access token. */
export async function loginViaAPI(
  email: string,
  password: string
): Promise<string> {
  const res = await fetch(`${apiURL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Login failed (${res.status}): ${body}`);
  }
  const data = await res.json();
  return data.access_token as string;
}

export { base as test };
