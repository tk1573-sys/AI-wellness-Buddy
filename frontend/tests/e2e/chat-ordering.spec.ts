/**
 * Chat Ordering & Scroll Regression Tests
 *
 * Covers:
 *  1. User message always appears above (before) the corresponding assistant reply.
 *  2. Conversation order is preserved after simulating a page-back / navigation.
 *  3. Multi-turn conversation maintains strict chronological order.
 *  4. History restored from the backend is rendered in ascending order.
 *  5. After sending a new message the bottom of the conversation is visible
 *     (scroll restoration).
 */

import { test, expect, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const FAKE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.token";

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function injectToken(page: Page) {
  await page.addInitScript((token) => {
    window.localStorage.setItem("wb_access_token", token);
  }, FAKE_TOKEN);
}

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
            session_id: "test-session-ordering",
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
// Section 1 — Ordering tests
// ---------------------------------------------------------------------------

test.describe("Chat Ordering", () => {
  test("user message appears above assistant reply in DOM", async ({ page }) => {
    await injectToken(page);
    await mockChatHistory(page);
    await mockChatPost(page, "I understand — you are not alone.", "sadness");

    await page.goto("/chat");

    await page
      .getByPlaceholder(/Type a message/i)
      .fill("I feel very sad today.");
    await page.click('[aria-label="Send message"]');

    // Wait for the assistant reply to appear.
    await expect(
      page.getByText("I understand — you are not alone."),
    ).toBeVisible({ timeout: 10_000 });

    // Verify DOM ordering: user bubble must come before the assistant bubble.
    const userBubble = page.getByText("I feel very sad today.");
    const assistantBubble = page.getByText("I understand — you are not alone.");

    const userBox = await userBubble.boundingBox();
    const assistantBox = await assistantBubble.boundingBox();

    expect(userBox).not.toBeNull();
    expect(assistantBox).not.toBeNull();
    // User bubble top edge must be strictly above (less Y) than assistant bubble.
    expect(userBox!.y).toBeLessThan(assistantBox!.y);
  });

  test("multi-turn conversation maintains chronological order", async ({
    page,
  }) => {
    await injectToken(page);
    await mockChatHistory(page);

    // Two sequential replies — each POST returns a different message.
    let callCount = 0;
    const replies = ["First reply.", "Second reply."];
    await page.route(
      (url) =>
        url.href.startsWith(`${API}/api/v1/chat`) &&
        !url.pathname.includes("/history"),
      (route) => {
        if (route.request().method() === "POST") {
          const reply = replies[callCount % replies.length];
          callCount++;
          route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              session_id: "test-session-multi",
              reply,
              primary_emotion: "neutral",
              confidence: 0.5,
              is_high_risk: false,
              escalation_message: null,
              scores: [],
            }),
          });
        } else {
          route.continue();
        }
      },
    );

    await page.goto("/chat");

    // First turn
    await page.getByPlaceholder(/Type a message/i).fill("Message one.");
    await page.click('[aria-label="Send message"]');
    await expect(page.getByText("First reply.")).toBeVisible({
      timeout: 10_000,
    });

    // Second turn
    await page.getByPlaceholder(/Type a message/i).fill("Message two.");
    await page.click('[aria-label="Send message"]');
    await expect(page.getByText("Second reply.")).toBeVisible({
      timeout: 10_000,
    });

    // Collect the top-Y positions of all four bubbles.
    const msg1 = await page.getByText("Message one.").boundingBox();
    const rep1 = await page.getByText("First reply.").boundingBox();
    const msg2 = await page.getByText("Message two.").boundingBox();
    const rep2 = await page.getByText("Second reply.").boundingBox();

    expect(msg1).not.toBeNull();
    expect(rep1).not.toBeNull();
    expect(msg2).not.toBeNull();
    expect(rep2).not.toBeNull();

    // Strict ordering: msg1 → rep1 → msg2 → rep2 (ascending Y).
    expect(msg1!.y).toBeLessThan(rep1!.y);
    expect(rep1!.y).toBeLessThan(msg2!.y);
    expect(msg2!.y).toBeLessThan(rep2!.y);
  });

  test("history from backend is rendered in ascending order", async ({
    page,
  }) => {
    await injectToken(page);

    // Provide history with explicit timestamps in ascending order.
    const base = new Date("2024-01-01T10:00:00Z").getTime();
    const historyMessages = [
      {
        role: "user",
        content: "Old user message",
        emotion: null,
        created_at: new Date(base).toISOString(),
      },
      {
        role: "assistant",
        content: "Old assistant reply",
        emotion: "neutral",
        created_at: new Date(base + 1000).toISOString(),
      },
    ];

    await mockChatHistory(page, historyMessages);
    await page.goto("/chat");

    await expect(page.getByText("Old user message")).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.getByText("Old assistant reply")).toBeVisible({
      timeout: 5_000,
    });

    // Verify DOM order — user must come first.
    const userBox = await page.getByText("Old user message").boundingBox();
    const assistantBox = await page
      .getByText("Old assistant reply")
      .boundingBox();

    expect(userBox).not.toBeNull();
    expect(assistantBox).not.toBeNull();
    expect(userBox!.y).toBeLessThan(assistantBox!.y);
  });

  test("ordering is preserved after page navigation and back", async ({
    page,
  }) => {
    await injectToken(page);

    const historyMessages = [
      {
        role: "user",
        content: "Before nav user message",
        emotion: null,
        created_at: new Date("2024-01-01T10:00:00Z").toISOString(),
      },
      {
        role: "assistant",
        content: "Before nav assistant reply",
        emotion: "neutral",
        created_at: new Date("2024-01-01T10:00:01Z").toISOString(),
      },
    ];
    await mockChatHistory(page, historyMessages);

    await page.goto("/chat");
    await expect(page.getByText("Before nav user message")).toBeVisible({
      timeout: 5_000,
    });

    // Navigate away and back.
    await page.goto("/dashboard");
    await page.goto("/chat");

    await expect(page.getByText("Before nav user message")).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.getByText("Before nav assistant reply")).toBeVisible({
      timeout: 5_000,
    });

    const userBox = await page
      .getByText("Before nav user message")
      .boundingBox();
    const assistantBox = await page
      .getByText("Before nav assistant reply")
      .boundingBox();

    expect(userBox!.y).toBeLessThan(assistantBox!.y);
  });
});

// ---------------------------------------------------------------------------
// Section 2 — Scroll restoration tests
// ---------------------------------------------------------------------------

test.describe("Scroll Restoration", () => {
  test("latest message is visible after sending", async ({ page }) => {
    await injectToken(page);
    await mockChatHistory(page);
    await mockChatPost(page, "Latest assistant reply.", "neutral");

    await page.goto("/chat");

    await page
      .getByPlaceholder(/Type a message/i)
      .fill("Show me the latest message.");
    await page.click('[aria-label="Send message"]');

    const latestReply = page.getByText("Latest assistant reply.");
    await expect(latestReply).toBeVisible({ timeout: 10_000 });

    // The latest reply must be within the visible viewport.
    const box = await latestReply.boundingBox();
    expect(box).not.toBeNull();
    const viewport = page.viewportSize();
    expect(viewport).not.toBeNull();
    expect(box!.y + box!.height).toBeLessThanOrEqual(viewport!.height + 10); // ±10 px tolerance
  });
});
