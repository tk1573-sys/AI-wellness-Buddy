/**
 * API Contract Tests — validate /predict and /chat response schemas.
 *
 * These tests call the backend API directly using Playwright's request
 * context.  They are skipped automatically when the backend is not
 * reachable (CI without a live server), so they never block the pipeline.
 *
 * Run them locally with a running backend:
 *   cd backend && uvicorn app.main:app --reload
 *   cd frontend && npx playwright test tests/e2e/api.spec.ts
 */

import { test, expect, APIRequestContext } from "@playwright/test";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Returns true when the backend health endpoint is reachable. */
async function isApiReachable(request: APIRequestContext): Promise<boolean> {
  try {
    const res = await request.get(`${API_BASE}/health`, { timeout: 3_000 });
    return res.ok();
  } catch {
    return false;
  }
}

/** Register + login and return a valid JWT. */
async function obtainToken(request: APIRequestContext): Promise<string> {
  const email = `e2e_api_${Date.now()}@example.com`;
  const username = `e2e_api_${Date.now()}`;

  await request.post(`${API_BASE}/api/v1/auth/signup`, {
    data: { email, username, password: "E2ePassw0rd!" },
  });

  const loginRes = await request.post(`${API_BASE}/api/v1/auth/login`, {
    data: { email, password: "E2ePassw0rd!" },
  });
  const body = await loginRes.json();
  return body.access_token as string;
}

// ---------------------------------------------------------------------------
// /health
// ---------------------------------------------------------------------------

test.describe("API — /health", () => {
  test("GET /health returns status ok", async ({ request }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    const res = await request.get(`${API_BASE}/health`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toMatchObject({ status: "ok" });
    expect(typeof body.version).toBe("string");
  });
});

// ---------------------------------------------------------------------------
// /api/v1/predict
// ---------------------------------------------------------------------------

test.describe("API — /predict", () => {
  test("POST /predict returns expected schema", async ({ request }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    const res = await request.post(`${API_BASE}/api/v1/predict`, {
      data: { text: "I feel really happy and excited today!" },
    });

    expect(res.status()).toBe(200);
    const body = await res.json();

    // Required top-level fields
    expect(typeof body.primary_emotion).toBe("string");
    expect(body.primary_emotion.length).toBeGreaterThan(0);

    expect(typeof body.confidence).toBe("number");
    expect(body.confidence).toBeGreaterThanOrEqual(0);
    expect(body.confidence).toBeLessThanOrEqual(1);

    expect(typeof body.uncertainty).toBe("number");
    expect(body.uncertainty).toBeGreaterThanOrEqual(0);
    expect(body.uncertainty).toBeLessThanOrEqual(1);

    expect(typeof body.is_uncertain).toBe("boolean");
    expect(typeof body.is_high_risk).toBe("boolean");

    // scores must be a non-empty array of {emotion, score} objects
    expect(Array.isArray(body.scores)).toBe(true);
    expect(body.scores.length).toBeGreaterThan(0);
    for (const s of body.scores) {
      expect(typeof s.emotion).toBe("string");
      expect(typeof s.score).toBe("number");
      expect(s.score).toBeGreaterThanOrEqual(0);
      expect(s.score).toBeLessThanOrEqual(1);
    }
  });

  test("POST /predict with empty text returns 422", async ({ request }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    const res = await request.post(`${API_BASE}/api/v1/predict`, {
      data: { text: "" },
    });
    expect(res.status()).toBe(422);
  });

  test("POST /predict high-risk input sets is_high_risk flag", async ({
    request,
  }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    const res = await request.post(`${API_BASE}/api/v1/predict`, {
      data: { text: "I want to end my life" },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.is_high_risk).toBe(true);
    expect(typeof body.escalation_message).toBe("string");
  });
});

// ---------------------------------------------------------------------------
// /api/v1/chat
// ---------------------------------------------------------------------------

test.describe("API — /chat", () => {
  test("POST /chat returns expected schema", async ({ request }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    const token = await obtainToken(request);

    const res = await request.post(`${API_BASE}/api/v1/chat`, {
      // The backend authenticates via a `token` query parameter by design
      // (see app/routers/chat.py — `token: str` is a required query param).
      params: { token },
      data: { message: "I have been feeling a bit anxious lately." },
    });

    expect(res.status()).toBe(200);
    const body = await res.json();

    expect(typeof body.session_id).toBe("string");
    expect(body.session_id.length).toBeGreaterThan(0);

    expect(typeof body.reply).toBe("string");
    expect(body.reply.length).toBeGreaterThan(0);

    expect(typeof body.primary_emotion).toBe("string");
    expect(body.primary_emotion.length).toBeGreaterThan(0);

    expect(typeof body.confidence).toBe("number");
    expect(body.confidence).toBeGreaterThanOrEqual(0);
    expect(body.confidence).toBeLessThanOrEqual(1);

    expect(typeof body.is_high_risk).toBe("boolean");

    // escalation_message is nullable
    expect(
      body.escalation_message === null ||
        typeof body.escalation_message === "string",
    ).toBe(true);
  });

  test("POST /chat without token returns 422", async ({ request }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    // Omit the required `token` query param → FastAPI returns 422
    const res = await request.post(`${API_BASE}/api/v1/chat`, {
      data: { message: "Hello" },
    });
    expect(res.status()).toBe(422);
  });

  test("POST /chat with invalid token returns 401", async ({ request }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    const res = await request.post(`${API_BASE}/api/v1/chat`, {
      params: { token: "not-a-real-token" },
      data: { message: "Hello" },
    });
    expect(res.status()).toBe(401);
  });

  test("GET /chat/history returns an array", async ({ request }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    const token = await obtainToken(request);

    const res = await request.get(`${API_BASE}/api/v1/chat/history`, {
      params: { token },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
  });

  test("POST /chat continues existing session when session_id provided", async ({
    request,
  }) => {
    test.skip(!(await isApiReachable(request)), "Backend not reachable — skipping");

    const token = await obtainToken(request);

    // First message — creates session
    const first = await request.post(`${API_BASE}/api/v1/chat`, {
      params: { token },
      data: { message: "Hello there" },
    });
    const { session_id } = await first.json();
    expect(typeof session_id).toBe("string");

    // Second message — reuses session
    const second = await request.post(`${API_BASE}/api/v1/chat`, {
      params: { token },
      data: { message: "Can you help me?", session_id },
    });
    expect(second.status()).toBe(200);
    const secondBody = await second.json();
    expect(secondBody.session_id).toBe(session_id);
  });
});
