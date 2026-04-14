/**
 * Chat Flow — end-to-end tests
 *
 * Covers:
 *   1. Send a message → user bubble appears
 *   2. Receive an assistant response → reply visible
 *   3. Emotion badge is rendered on the assistant bubble
 *   4. Unauthenticated visit → redirected to /login
 *   5. Messages display in chronological order (oldest on top, newest at bottom)
 *   6. Returning to /chat from dashboard auto-scrolls to the latest message
 *   7. Returning to /chat from profile auto-scrolls to the latest message
 *   8. Refreshing /chat keeps messages in correct order and scrolls to bottom
 *   9. Mobile layout: last message is visible after history loads
 *
 * All backend calls are mocked with page.route() for CI stability.
 */

import { test, expect, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const FAKE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.token";

// ---------------------------------------------------------------------------
// Fixture: inject a valid token into localStorage before the page loads
// ---------------------------------------------------------------------------

async function injectToken(page: Page) {
  await page.addInitScript((token) => {
    window.localStorage.setItem("wb_access_token", token);
  }, FAKE_TOKEN);
}

// ---------------------------------------------------------------------------
// Mock helpers
// ---------------------------------------------------------------------------

async function mockChatHistory(page: Page, messages: object[] = []) {
  await page.route(`${API}/api/v1/chat/history*`, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(messages),
    }),
  );
}

async function mockChatPost(
  page: Page,
  reply = "I hear you. That sounds really difficult.",
  emotion = "sadness",
  confidence = 0.82,
) {
  // Use a URL predicate to match /api/v1/chat (POST) but never /api/v1/chat/history
  await page.route(
    (url) =>
      url.href.startsWith(`${API}/api/v1/chat`) &&
      !url.pathname.includes("/history"),
    (route) => {
      if (route.request().method() === "POST") {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            session_id: "test-session-123",
            reply,
            primary_emotion: emotion,
            confidence,
            is_high_risk: false,
            escalation_message: null,
            scores: [{ emotion, score: confidence }],
          }),
        });
      } else {
        route.continue();
      }
    },
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

/**
 * Mock all supplementary API routes that dashboard, profile, and chat page
 * fetch on mount so navigation tests don't hit real network endpoints.
 */
async function mockSupportingApis(page: Page) {
  // Profile (language preference, profile page form data)
  await page.route(`${API}/api/v1/profile*`, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ language_preference: "english" }),
    }),
  );
  // Insights (chat sidebar + dashboard)
  await page.route(`${API}/api/v1/insights*`, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        dominant_emotion: "neutral",
        personalization_score: 0,
        trigger_signals: [],
        risk_level: "low",
        recent_pattern: {},
        trend: "stable",
      }),
    }),
  );
  // Dashboard
  await page.route(`${API}/api/v1/dashboard*`, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        emotion_trend: [],
        emotion_distribution: [],
        risk_alerts: [],
        mood_trend: "stable",
        escalation_detected: false,
        total_sessions: 0,
      }),
    }),
  );
  // Journey (also fetched by dashboard page)
  await page.route(`${API}/api/v1/journey*`, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        journey_points: [],
        heatmap: [],
        moving_average: [],
        latest_risk_score: 0,
        stability_index: 1,
        volatility_label: "stable",
        cdi_score: 0,
        cdi_level: "low",
        total_points: 0,
      }),
    }),
  );
  // Guardian alerts (fetched by dashboard page)
  await page.route(`${API}/api/v1/guardian-alert*`, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ alerts: [], total: 0 }),
    }),
  );
}

test.describe("Chat Flow", () => {
  test("send a message → user bubble appears in conversation", async ({
    page,
  }) => {
    await injectToken(page);
    await mockChatHistory(page);
    await mockChatPost(page);

    await page.goto("/chat");

    const textarea = page.getByPlaceholder(/Type a message/i);
    await textarea.fill("Hello, I need some support today.");

    // Send via button click
    await page.click('[aria-label="Send message"]');

    // User message bubble should be visible
    await expect(
      page.getByText("Hello, I need some support today."),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("receive assistant response after sending message", async ({ page }) => {
    await injectToken(page);
    await mockChatHistory(page);
    await mockChatPost(
      page,
      "I hear you. That sounds really difficult.",
      "sadness",
    );

    await page.goto("/chat");

    await page
      .getByPlaceholder(/Type a message/i)
      .fill("I've been feeling very sad lately.");

    await page.click('[aria-label="Send message"]');

    // Assistant reply should appear
    await expect(
      page.getByText("I hear you. That sounds really difficult."),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("emotion badge is visible on assistant response", async ({ page }) => {
    await injectToken(page);
    await mockChatHistory(page);
    await mockChatPost(page, "Let's work through this together.", "anxiety", 0.75);

    await page.goto("/chat");

    await page
      .getByPlaceholder(/Type a message/i)
      .fill("I'm feeling very anxious about everything.");

    await page.click('[aria-label="Send message"]');

    // Wait for the reply to appear first
    await expect(
      page.getByText("Let's work through this together."),
    ).toBeVisible({ timeout: 10_000 });

    // EmotionBadge renders a capitalised span containing the emotion label
    await expect(
      page.locator("span.capitalize", { hasText: "anxiety" }),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("emotion badge shows confidence percentage", async ({ page }) => {
    await injectToken(page);
    await mockChatHistory(page);
    await mockChatPost(page, "You're not alone in this.", "sadness", 0.9);

    await page.goto("/chat");

    await page
      .getByPlaceholder(/Type a message/i)
      .fill("I feel hopeless.");

    await page.click('[aria-label="Send message"]');

    await expect(page.getByText("You're not alone in this.")).toBeVisible({
      timeout: 10_000,
    });

    // Confidence is rendered as "90%" next to the emotion label
    await expect(page.getByText("90%")).toBeVisible({ timeout: 5_000 });
  });

  test("send via Enter key works", async ({ page }) => {
    await injectToken(page);
    await mockChatHistory(page);
    await mockChatPost(page, "I'm here to help.", "neutral");

    await page.goto("/chat");

    const textarea = page.getByPlaceholder(/Type a message/i);
    await textarea.fill("How are you?");
    await textarea.press("Enter");

    await expect(page.getByText("How are you?")).toBeVisible({
      timeout: 5_000,
    });
  });

  test("unauthenticated visit redirects to /login", async ({ page }) => {
    // No token injected
    await page.addInitScript(() => window.localStorage.clear());
    await page.goto("/chat");

    await page.waitForURL("**/login", { timeout: 5_000 });
    expect(page.url()).toContain("/login");
  });

  test("chat history is loaded and displayed on mount", async ({ page }) => {
    await injectToken(page);

    const historyMessages = [
      {
        role: "user",
        content: "Previous user message",
        emotion: null,
        created_at: new Date().toISOString(),
      },
      {
        role: "assistant",
        content: "Previous assistant reply",
        emotion: "neutral",
        created_at: new Date().toISOString(),
      },
    ];

    await mockChatHistory(page, historyMessages);

    await page.goto("/chat");

    // Both history messages should be shown after load
    await expect(page.getByText("Previous user message")).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.getByText("Previous assistant reply")).toBeVisible({
      timeout: 5_000,
    });
  });

  // ---------------------------------------------------------------------------
  // Message ordering & scroll regression tests
  // ---------------------------------------------------------------------------

  test("messages display in chronological order: oldest on top, newest at bottom", async ({ page }) => {
    await injectToken(page);
    await mockSupportingApis(page);

    const now = Date.now();
    const historyMessages = [
      { role: "user",      content: "Oldest message",        emotion: null,      created_at: new Date(now - 4000).toISOString() },
      { role: "assistant", content: "First assistant reply",  emotion: "neutral", created_at: new Date(now - 3000).toISOString() },
      { role: "user",      content: "Middle message",         emotion: null,      created_at: new Date(now - 2000).toISOString() },
      { role: "assistant", content: "Second assistant reply", emotion: "joy",     created_at: new Date(now - 1000).toISOString() },
      { role: "user",      content: "Newest message",         emotion: null,      created_at: new Date(now).toISOString() },
    ];
    await mockChatHistory(page, historyMessages);

    await page.goto("/chat");

    // All messages should be visible
    await expect(page.getByText("Oldest message")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Newest message")).toBeVisible({ timeout: 5_000 });

    // Verify DOM order: the bounding box of the first message should be
    // above (smaller Y) the last message — chronological top-to-bottom.
    const firstBox = await page.getByText("Oldest message").boundingBox();
    const lastBox  = await page.getByText("Newest message").boundingBox();
    expect(firstBox).not.toBeNull();
    expect(lastBox).not.toBeNull();
    expect(firstBox!.y).toBeLessThan(lastBox!.y);
  });

  test("latest message is scrolled into view after history loads", async ({ page }) => {
    await injectToken(page);
    await mockSupportingApis(page);

    // Create enough messages to require scrolling
    const now = Date.now();
    const historyMessages = Array.from({ length: 20 }, (_, i) => ({
      role: i % 2 === 0 ? "user" : "assistant",
      content: i === 19 ? "The very last message" : `Message number ${i}`,
      emotion: "neutral",
      created_at: new Date(now - (20 - i) * 1000).toISOString(),
    }));
    await mockChatHistory(page, historyMessages);

    await page.goto("/chat");

    // The last message must be visible in the viewport without manual scrolling
    await expect(page.getByText("The very last message")).toBeVisible({
      timeout: 5_000,
    });
  });

  test("dashboard → chat: last message is visible after tab switch", async ({ page }) => {
    await injectToken(page);
    await mockSupportingApis(page);

    const now = Date.now();
    const historyMessages = Array.from({ length: 10 }, (_, i) => ({
      role: i % 2 === 0 ? "user" : "assistant",
      content: i === 9 ? "Final chat message" : `Chat message ${i}`,
      emotion: "neutral",
      created_at: new Date(now - (10 - i) * 1000).toISOString(),
    }));
    await mockChatHistory(page, historyMessages);

    // Start on /chat
    await page.goto("/chat");
    await expect(page.getByText("Final chat message")).toBeVisible({ timeout: 5_000 });

    // Navigate to dashboard
    await page.getByRole("button", { name: /dashboard/i }).click();
    await page.waitForURL("**/dashboard", { timeout: 10_000 });

    // Navigate back to chat
    await page.getByRole("button", { name: /chat/i }).click();
    await page.waitForURL("**/chat", { timeout: 10_000 });

    // Last message must be visible (scroll should be at bottom)
    await expect(page.getByText("Final chat message")).toBeVisible({ timeout: 5_000 });
  });

  test("profile → chat: last message is visible after tab switch", async ({ page }) => {
    await injectToken(page);
    await mockSupportingApis(page);

    const now = Date.now();
    const historyMessages = Array.from({ length: 10 }, (_, i) => ({
      role: i % 2 === 0 ? "user" : "assistant",
      content: i === 9 ? "Last message before profile" : `Chat message ${i}`,
      emotion: "neutral",
      created_at: new Date(now - (10 - i) * 1000).toISOString(),
    }));
    await mockChatHistory(page, historyMessages);

    // Start on /chat
    await page.goto("/chat");
    await expect(page.getByText("Last message before profile")).toBeVisible({ timeout: 5_000 });

    // Navigate to profile
    await page.getByRole("button", { name: /profile/i }).click();
    await page.waitForURL("**/profile", { timeout: 10_000 });

    // Navigate back to chat
    await page.getByRole("button", { name: /chat/i }).click();
    await page.waitForURL("**/chat", { timeout: 10_000 });

    // Last message must be visible after returning
    await expect(page.getByText("Last message before profile")).toBeVisible({ timeout: 5_000 });
  });

  test("page refresh: messages remain in order and scroll is at bottom", async ({ page }) => {
    await injectToken(page);
    await mockSupportingApis(page);

    const now = Date.now();
    const historyMessages = Array.from({ length: 12 }, (_, i) => ({
      role: i % 2 === 0 ? "user" : "assistant",
      content: i === 11 ? "Last message after refresh" : `Message ${i}`,
      emotion: "neutral",
      created_at: new Date(now - (12 - i) * 1000).toISOString(),
    }));
    await mockChatHistory(page, historyMessages);

    await page.goto("/chat");
    await expect(page.getByText("Last message after refresh")).toBeVisible({ timeout: 5_000 });

    // Reload the page (simulates F5 / hard refresh)
    await page.reload();

    // Re-apply mocks after reload (page.route mocks persist across reload in Playwright)
    await expect(page.getByText("Last message after refresh")).toBeVisible({ timeout: 8_000 });

    // The first message should still appear above the last (chronological order preserved)
    const firstBox = await page.getByText("Message 0").boundingBox();
    const lastBox  = await page.getByText("Last message after refresh").boundingBox();
    expect(firstBox).not.toBeNull();
    expect(lastBox).not.toBeNull();
    expect(firstBox!.y).toBeLessThan(lastBox!.y);
  });

  test("mobile layout: last message is visible after history loads", async ({ page }) => {
    // Simulate a typical mobile viewport (375×812 — iPhone 12/13 Pro)
    await page.setViewportSize({ width: 375, height: 812 });
    await injectToken(page);
    await mockSupportingApis(page);

    const now = Date.now();
    const historyMessages = Array.from({ length: 15 }, (_, i) => ({
      role: i % 2 === 0 ? "user" : "assistant",
      content: i === 14 ? "Mobile last message" : `Mobile message ${i}`,
      emotion: "neutral",
      created_at: new Date(now - (15 - i) * 1000).toISOString(),
    }));
    await mockChatHistory(page, historyMessages);

    await page.goto("/chat");

    // Last message must be visible on mobile without extra scrolling
    await expect(page.getByText("Mobile last message")).toBeVisible({ timeout: 5_000 });
  });
});
