/**
 * Chat Flow — end-to-end tests
 *
 * Covers:
 *   1. Send a message → user bubble appears
 *   2. Receive an assistant response → reply visible
 *   3. Emotion badge is rendered on the assistant bubble
 *   4. Unauthenticated visit → redirected to /login
 *
 * All backend calls are mocked with page.route() for CI stability.
 */

import { test, expect, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const FAKE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.token";

// ---------------------------------------------------------------------------
// Fixture: set the wb_logged_in cookie so the auth gate treats the session as
// authenticated (auth.ts uses Cookies.get("wb_logged_in") === "1").
// ---------------------------------------------------------------------------

async function injectToken(page: Page) {
  await page.context().addCookies([
    {
      name: "wb_logged_in",
      value: "1",
      domain: "localhost",
      path: "/",
    },
  ]);
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
    await page.click('[data-testid="send-message"]');

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

    await page.click('[data-testid="send-message"]');

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

    await page.click('[data-testid="send-message"]');

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

    await page.click('[data-testid="send-message"]');

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
});
