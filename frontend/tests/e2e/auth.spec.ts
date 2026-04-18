/**
 * Auth Flow — end-to-end tests
 *
 * Covers:
 *   1. Signup  → token stored → redirect to /chat
 *   2. Login   → token stored → redirect to /chat
 *   3. Invalid login → error toast shown, user stays on /login
 *
 * All backend API calls are intercepted with page.route() so the tests
 * run fully in CI without a live backend.
 */

import { test, expect, type Page } from "@playwright/test";

// Backend origin as seen by the browser (matches NEXT_PUBLIC_API_URL default)
const API = "http://localhost:8000";

// Fake JWT returned by the mocked auth endpoints
const FAKE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.token";

/** Clear localStorage before each test so tokens never leak between tests. */
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => window.localStorage.clear());
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Set up the mock auth endpoints and a stub history endpoint. */
async function mockAuthSuccess(
  page: Page,
  endpoint: "signup" | "login",
  status = 200,
) {
  await page.route(`${API}/api/v1/auth/${endpoint}`, (route) =>
    route.fulfill({
      status,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: FAKE_TOKEN,
        token_type: "bearer",
        expires_in: 3600,
      }),
    }),
  );

  // Stub chat history so the /chat page loads cleanly after redirect
  await page.route(`${API}/api/v1/chat/history*`, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    }),
  );
}

async function mockAuthFailure(page: Page, endpoint: "signup" | "login") {
  await page.route(`${API}/api/v1/auth/${endpoint}`, (route) =>
    route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Incorrect email or password." }),
    }),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test.describe("Auth Flow", () => {
  test("signup → session flag set → redirect to /chat", async ({ page }) => {
    await mockAuthSuccess(page, "signup", 201);
    await page.goto("/signup");

    // Fill the registration form
    await page.fill("#email", "e2etest@example.com");
    await page.fill("#username", "e2euser");
    await page.fill("#password", "Passw0rd!");

    await page.click('button[type="submit"]');

    // New users are redirected through the onboarding flow before reaching /chat.
    await page.waitForURL(/\/(onboarding|chat)/, { timeout: 10_000 });
    expect(page.url()).toMatch(/\/(onboarding|chat)/);

    // Session presence flag must be set in the wb_logged_in cookie.
    // The JWT itself lives in an HttpOnly cookie set by the backend; only
    // the non-HttpOnly flag is readable from JavaScript.
    const cookies = await page.context().cookies();
    const flag = cookies.find((c) => c.name === "wb_logged_in");
    expect(flag?.value).toBe("1");
  });

  test("login → session flag set → redirect to /chat", async ({ page }) => {
    await mockAuthSuccess(page, "login");
    await page.goto("/login");

    await page.fill("#email", "e2etest@example.com");
    await page.fill("#password", "Passw0rd!");

    await page.click('button[type="submit"]');

    await page.waitForURL("**/chat", { timeout: 10_000 });
    expect(page.url()).toContain("/chat");

    // The wb_logged_in flag cookie must be present after a successful login.
    const cookies = await page.context().cookies();
    const flag = cookies.find((c) => c.name === "wb_logged_in");
    expect(flag?.value).toBe("1");
  });

  test("invalid login → error toast shown, stays on /login", async ({
    page,
  }) => {
    await mockAuthFailure(page, "login");
    await page.goto("/login");

    await page.fill("#email", "wrong@example.com");
    await page.fill("#password", "BadPass99!");

    await page.click('button[type="submit"]');

    // react-hot-toast renders a live-region with role="status"
    await expect(page.locator('[role="status"]').first()).toBeVisible({
      timeout: 5_000,
    });

    // Must NOT have navigated away from the login page
    expect(page.url()).toContain("/login");
  });

  test("signup form client-side validation — invalid email", async ({
    page,
  }) => {
    await page.goto("/signup");

    await page.fill("#email", "not-an-email");
    await page.fill("#username", "user");
    await page.fill("#password", "Passw0rd!");

    await page.click('button[type="submit"]');

    // The form shows an inline validation error (no API call made)
    await expect(page.getByText("Enter a valid email.")).toBeVisible({
      timeout: 3_000,
    });
  });

  test("login form client-side validation — empty password", async ({
    page,
  }) => {
    await page.goto("/login");

    await page.fill("#email", "test@example.com");
    // Leave password blank

    await page.click('button[type="submit"]');

    await expect(page.getByText("Password is required.")).toBeVisible({
      timeout: 3_000,
    });
  });
});
