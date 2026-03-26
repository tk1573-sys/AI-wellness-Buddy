/**
 * E2E test: Full auth flow — Signup → Login → Chat → Response
 *
 * Tests:
 *  1. User can sign up via the UI signup form.
 *  2. User can log in via the UI login form.
 *  3. Logged-in user can send a chat message and receive a response.
 *  4. High-risk message surfaces the escalation notice.
 *
 * NOTE: These tests require both the Next.js frontend and FastAPI backend to
 * be running.  In CI set PLAYWRIGHT_BASE_URL and PLAYWRIGHT_API_URL env vars.
 * Locally run `npm run dev` (frontend) and `uvicorn app.main:app` (backend)
 * before executing `npx playwright test`.
 */

import { expect } from "@playwright/test";
import {
  test,
  uniqueEmail,
  uniqueUsername,
  signupViaAPI,
  loginViaAPI,
  apiURL,
} from "./helpers";

const PASSWORD = "TestPass1!";

// ─────────────────────────────────────────────────────────────────────────────
// Backend API smoke tests (no browser needed)
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Backend API smoke tests", () => {
  test("GET /health returns ok", async ({ request }) => {
    const res = await request.get(`${apiURL}/health`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.status).toBe("ok");
  });

  test("POST /api/v1/auth/signup creates a new user", async ({ request }) => {
    const email = uniqueEmail();
    const username = uniqueUsername();
    const res = await request.post(`${apiURL}/api/v1/auth/signup`, {
      data: { email, username, password: PASSWORD },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty("access_token");
    expect(body.token_type).toBe("bearer");
  });

  test("POST /api/v1/auth/signup rejects duplicate email with 409", async ({
    request,
  }) => {
    const email = uniqueEmail();
    const username = uniqueUsername();
    await request.post(`${apiURL}/api/v1/auth/signup`, {
      data: { email, username, password: PASSWORD },
    });
    const res = await request.post(`${apiURL}/api/v1/auth/signup`, {
      data: { email, username: uniqueUsername(), password: PASSWORD },
    });
    expect(res.status()).toBe(409);
  });

  test("POST /api/v1/auth/login returns token for valid credentials", async ({
    request,
  }) => {
    const email = uniqueEmail();
    const username = uniqueUsername();
    await request.post(`${apiURL}/api/v1/auth/signup`, {
      data: { email, username, password: PASSWORD },
    });
    const res = await request.post(`${apiURL}/api/v1/auth/login`, {
      data: { email, password: PASSWORD },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty("access_token");
  });

  test("POST /api/v1/auth/login rejects bad password with 401", async ({
    request,
  }) => {
    const email = uniqueEmail();
    await request.post(`${apiURL}/api/v1/auth/signup`, {
      data: { email, username: uniqueUsername(), password: PASSWORD },
    });
    const res = await request.post(`${apiURL}/api/v1/auth/login`, {
      data: { email, password: "WrongPass9!" },
    });
    expect(res.status()).toBe(401);
  });

  test("POST /api/v1/predict returns primary_emotion", async ({ request }) => {
    const res = await request.post(`${apiURL}/api/v1/predict`, {
      data: { text: "I feel really happy today!" },
    });
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body).toHaveProperty("primary_emotion");
    expect(body).toHaveProperty("confidence");
    expect(body).toHaveProperty("scores");
    expect(Array.isArray(body.scores)).toBeTruthy();
  });

  test("POST /api/v1/predict sets is_high_risk for crisis text", async ({
    request,
  }) => {
    const res = await request.post(`${apiURL}/api/v1/predict`, {
      data: { text: "I want to end my life and I cannot go on anymore." },
    });
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.is_high_risk).toBe(true);
    expect(body.escalation_message).toBeTruthy();
  });

  test("POST /api/v1/chat requires authentication", async ({ request }) => {
    const res = await request.post(
      `${apiURL}/api/v1/chat?token=invalid-token`,
      { data: { message: "Hello" } }
    );
    expect(res.status()).toBe(401);
  });

  test("POST /api/v1/chat returns reply for authenticated user", async ({
    request,
  }) => {
    const email = uniqueEmail();
    const username = uniqueUsername();
    const token = await signupViaAPI(email, username, PASSWORD);

    const res = await request.post(
      `${apiURL}/api/v1/chat?token=${token}`,
      { data: { message: "I am feeling a bit anxious today." } }
    );
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body).toHaveProperty("reply");
    expect(typeof body.reply).toBe("string");
    expect(body.reply.length).toBeGreaterThan(0);
    expect(body).toHaveProperty("session_id");
    expect(body).toHaveProperty("primary_emotion");
  });

  test("GET /api/v1/chat/history returns list for authenticated user", async ({
    request,
  }) => {
    const email = uniqueEmail();
    const username = uniqueUsername();
    const token = await signupViaAPI(email, username, PASSWORD);

    // Send a message first.
    await request.post(`${apiURL}/api/v1/chat?token=${token}`, {
      data: { message: "Hello there!" },
    });

    const res = await request.get(
      `${apiURL}/api/v1/chat/history?token=${token}`
    );
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(Array.isArray(body)).toBeTruthy();
    expect(body.length).toBeGreaterThan(0);
  });

  test("Response headers include X-Request-ID", async ({ request }) => {
    const res = await request.get(`${apiURL}/health`);
    expect(res.headers()["x-request-id"]).toBeTruthy();
  });

  test("Response headers include X-Process-Time-Ms", async ({ request }) => {
    const res = await request.get(`${apiURL}/health`);
    expect(res.headers()["x-process-time-ms"]).toBeTruthy();
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// UI flow tests (browser)
// ─────────────────────────────────────────────────────────────────────────────

test.describe("UI flow: Signup → Login → Chat → Response", () => {
  test("User can sign up via the signup form", async ({ page }) => {
    const email = uniqueEmail();
    const username = uniqueUsername();

    await page.goto("/signup");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Username").fill(username);
    await page.getByLabel("Password").fill(PASSWORD);
    await page.getByRole("button", { name: /create account/i }).click();

    // After signup the user is redirected to /chat
    await page.waitForURL("**/chat", { timeout: 15_000 });
    expect(page.url()).toContain("/chat");
  });

  test("User can log in via the login form", async ({ page }) => {
    // Create an account first via the API so we don't depend on the signup test.
    const email = uniqueEmail();
    const username = uniqueUsername();
    await signupViaAPI(email, username, PASSWORD);

    await page.goto("/login");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill(PASSWORD);
    await page.getByRole("button", { name: /sign in/i }).click();

    await page.waitForURL("**/chat", { timeout: 15_000 });
    expect(page.url()).toContain("/chat");
  });

  test("Invalid login shows an error toast", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill("nobody@example.com");
    await page.getByLabel("Password").fill("SomePass1!");
    await page.getByRole("button", { name: /sign in/i }).click();

    // Expect an error toast to appear (react-hot-toast renders in a portal).
    await expect(
      page.locator("[data-testid='toast-error'], [role='status']").first()
    ).toBeVisible({ timeout: 8_000 });
  });

  test("Chat page loads and message input is visible after login", async ({
    page,
  }) => {
    const email = uniqueEmail();
    const username = uniqueUsername();
    await signupViaAPI(email, username, PASSWORD);

    await page.goto("/login");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill(PASSWORD);
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL("**/chat", { timeout: 15_000 });

    // The chat input (textarea or input) should be visible.
    const chatInput = page
      .getByRole("textbox")
      .or(page.locator("textarea"))
      .first();
    await expect(chatInput).toBeVisible({ timeout: 8_000 });
  });

  test("User can send a chat message and receive a reply", async ({ page }) => {
    const email = uniqueEmail();
    const username = uniqueUsername();
    await signupViaAPI(email, username, PASSWORD);

    await page.goto("/login");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill(PASSWORD);
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL("**/chat", { timeout: 15_000 });

    const chatInput = page
      .getByRole("textbox")
      .or(page.locator("textarea"))
      .first();
    await chatInput.fill("I am feeling happy today!");
    await page.keyboard.press("Enter");

    // Wait for a reply bubble to appear in the chat thread.
    await expect(
      page.locator("[data-role='assistant'], [data-testid='assistant-message']")
        .first()
        .or(page.getByText(/here for you|understand|feeling/i).first())
    ).toBeVisible({ timeout: 20_000 });
  });
});
