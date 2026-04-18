# AI Wellness Buddy — Demo & Viva Script

**Project:** AI Wellness Buddy — Intelligent Emotional Support and Mental Wellness Monitoring System
**Stack:** FastAPI · Next.js · SQLite/PostgreSQL · HuggingFace Transformers · JWT HttpOnly Cookies

---

## 1. One-Sentence Summary (say this first)

> "AI Wellness Buddy is a privacy-first, full-stack mental wellness application that uses transformer-based emotion detection, empathetic AI chatting, and real-time risk escalation to support users' emotional wellbeing — all secured with HttpOnly cookie authentication and deployable on Render + Vercel."

---

## 2. Architecture Walkthrough (2–3 minutes)

```
Browser (Next.js / Vercel)
    │  HTTPS same-origin requests to /api/*
    ▼
Next.js Edge Proxy  ←── next.config.js rewrites /api/:path* → BACKEND_URL
    │  Forwards cookies transparently (no CORS issues)
    ▼
FastAPI Backend (Render)
    ├── POST /api/v1/auth/login  → sets HttpOnly wb_access_token cookie
    ├── GET  /api/v1/auth/me     → validates cookie, returns user
    ├── POST /api/v1/chat        → emotion analysis + empathetic reply
    ├── GET  /api/v1/chat/history → messages in chronological (ASC) order
    ├── GET  /api/v1/dashboard   → emotion trend + risk alerts
    ├── GET  /api/v1/weekly-report
    ├── GET  /api/v1/insights
    ├── POST /api/v1/voice/transcribe  (STT — SpeechRecognition + ffmpeg)
    └── POST /api/v1/voice/tts         (TTS — gTTS)
    │
    ▼
SQLite (dev) / PostgreSQL (prod via Render)
    └── Tables: users · chat_history · emotion_logs · user_profiles · guardian_alerts
```

**Key design decisions to mention:**
- **Same-origin proxy** eliminates CORS and cookie cross-site issues.
- **HttpOnly cookie** (`wb_access_token`) prevents XSS token theft; no token ever touches `localStorage`.
- **SameSite=Lax** cookie allows the cookie to travel on same-site navigation.
- **Secure flag** auto-detected from request scheme (HTTP in dev, HTTPS in prod).

---

## 3. Feature Walkthrough — Live Demo Steps

### Step 1: Signup / Login
1. Open `http://localhost:3000` (or the Vercel URL).
2. Click **Sign Up** → fill email, username, password.
3. On success you are redirected through Onboarding → `/chat`.
4. Open **DevTools → Application → Cookies**: confirm `wb_access_token` is present, marked **HttpOnly** and **SameSite=Lax**.
5. Refresh the page — still logged in (cookie persists).

### Step 2: Chat (Emotion-Aware)
1. Type: *"I've been feeling really anxious about my exams lately."*
2. Show the reply — the system detects `anxiety` with a confidence score.
3. Type: *"I don't see any point in continuing."*
4. Demonstrate the **high-risk flag** and the escalation message with crisis hotline numbers.

### Step 3: Dashboard
1. Navigate to **/dashboard**.
2. Show the **emotion trend line chart** and **emotion distribution pie/bar chart**.
3. Point out **risk_alerts** if any.

### Step 4: Weekly Report
1. Navigate to **/weekly-report**.
2. Show the 7-day breakdown: daily counts, dominant emotion, mood direction.

### Step 5: Insights
1. Navigate to **/insights**.
2. Show personalization score, trigger signals, risk level, and recent emotion pattern.

### Step 6: Voice Input (if ffmpeg installed)
1. On the chat page, click the **microphone** icon.
2. Speak a message — it is transcribed server-side via SpeechRecognition + ffmpeg.
3. The transcribed text populates the chat input automatically.

### Step 7: Guardian Alert (optional)
1. In the profile/onboarding form, fill **Guardian Email**.
2. Trigger a test alert: the backend sends an email notification when risk exceeds threshold.
3. Show the alert log at `/api/v1/guardian-alert`.

---

## 4. Authentication Security Explanation (for viva questions)

| Question | Answer |
|---|---|
| Why HttpOnly cookie instead of localStorage? | HttpOnly cookies are inaccessible to JavaScript — mitigates XSS attacks that steal tokens. |
| Why same-origin proxy? | Avoids CORS preflight issues and ensures the browser always sends the cookie (SameSite policy). |
| Why `SameSite=Lax`? | Lax allows cookie on top-level navigations and same-site requests without restricting normal use. |
| How does the cookie work on refresh? | The `max_age` is set to `ACCESS_TOKEN_EXPIRE_MINUTES * 60` seconds, so the cookie persists until it expires. |
| How is CSRF prevented? | The `SameSite=Lax` attribute prevents the cookie from being sent on cross-site form submissions. For production, SameSite=None + Secure + custom CSRF token is recommended. |

---

## 5. AI/ML Pipeline Explanation

```
User text input
    │
    ▼
EmotionAnalyzer (HuggingFace j-hartmann/emotion-english-distilroberta-base)
    │  → primary_emotion, confidence, uncertainty, all_scores
    ▼
Risk Classifier (rule-based + crisis emotion flag)
    │  → is_high_risk, risk_score, escalation_message
    ▼
WellnessAgentPipeline
    │  → context-aware empathetic reply (template + pattern-based)
    │  → personalization from user profile (triggers, tone, language)
    ▼
Response stored in DB (chat_history table, created_at ASC)
```

**Key stats to quote:**
- Model: `distilroberta-base` fine-tuned on GoEmotions — 7-class emotion detection.
- Crisis detection threshold: `confidence ≥ 0.6` for high-risk label.
- Personalization score: 0–1 scale, stored per session in `emotion_logs`.

---

## 6. Deployment Explanation

### Backend (Render)
```
render.yaml → Docker build (Dockerfile.backend)
Environment:
  SECRET_KEY=<generated>
  DATABASE_URL=postgresql+asyncpg://...  (from Render PostgreSQL add-on)
  ALLOWED_ORIGINS=["https://your-app.vercel.app"]
  FRONTEND_URL=https://your-app.vercel.app
  ENV=production
```

### Frontend (Vercel)
```
vercel.json → Next.js build
Environment:
  BACKEND_URL=https://ai-wellness-backend-ox4q.onrender.com
next.config.js rewrites /api/:path* → BACKEND_URL/api/:path*
```

---

## 7. Testing Evidence

### Backend (pytest)
```bash
cd backend && pytest tests/ -q
# 117 passed
# Covers: auth signup/login/logout, cookie presence, /auth/me, chat, history ordering,
#         analytics, crisis auto-dispatch, guardian alerts, DB outage handling
```

### E2E (Playwright)
```bash
cd frontend && npx playwright test
# Covers: login flow, redirect, cookie flag, invalid login toast,
#         chat message ordering, history from backend, scroll restoration
```

---

## 8. Potential Viva Questions & Answers

**Q: How do you handle concurrency in the backend?**
A: FastAPI uses asyncio; all DB calls use SQLAlchemy async engine with aiosqlite (dev) or asyncpg (prod). Rate limiting via slowapi prevents abuse.

**Q: What happens if the ML model is unavailable?**
A: Models are pre-warmed at startup. If pre-warm fails, a warning is logged; the first request incurs a cold-start delay (~16s) but the service continues. Errors surface as 500 with structured JSON.

**Q: How do you prevent duplicate guardian alerts?**
A: A cooldown of 30 minutes (`GUARDIAN_ALERT_COOLDOWN_MINUTES`) is enforced per user. The last alert timestamp is stored in `guardian_alerts` and checked before dispatching.

**Q: How is the chat history ordered?**
A: `SELECT ... ORDER BY created_at ASC` — strictly chronological, newest-last. Backend test `test_chat_history_ascending_order` verifies this by inserting rows in reverse order and asserting the API returns them sorted correctly.

**Q: What is the personalization score?**
A: A 0–1 float stored on each `EmotionLog` row. It reflects how well the AI response used the user's profile triggers and preferred communication style. Averaged over all sessions in the analytics endpoint.

**Q: Why did you use a proxy instead of calling the backend directly from the browser?**
A: Direct browser calls to `http://localhost:8000` (or the Render URL) are cross-origin — a different host or port. Browsers block or restrict cross-origin requests under CORS policy, and `SameSite=Lax` cookies will not be sent on cross-origin requests. The Next.js server-side proxy (`next.config.js` rewrites) forwards `/api/*` to the backend transparently, keeping the browser on a single origin throughout. This eliminates all CORS preflight issues and ensures cookies work correctly.

**Q: How is user data secured?**
A: Multiple layers: (1) The JWT token lives in an HttpOnly cookie — inaccessible to JavaScript, preventing XSS theft. (2) The same-origin proxy prevents CORS leakage. (3) Passwords are hashed with bcrypt via passlib. (4) The `SameSite=Lax` cookie attribute blocks cross-site request forgery. (5) The `Secure` flag is auto-set on HTTPS. (6) Rate limiting (5 requests/min on auth endpoints) prevents brute-force. (7) Security headers (CSP, X-Frame-Options, X-Content-Type-Options) are added by `SecurityHeadersMiddleware`. (8) In production, PostgreSQL on a Render private network is used — not a public-facing SQLite file.

---

## 9. Quick-Start Commands (for live demo setup)

```bash
# Backend
cd backend
cp .env.example .env          # fill in SECRET_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
cp .env.example .env.local    # BACKEND_URL=http://localhost:8000
npm install
npm run dev

# Open http://localhost:3000
```

---

## 10. Key Differentiators (closing statement)

1. **Privacy by design** — no token in browser storage; HttpOnly cookie + same-origin proxy.
2. **Crisis safety layer** — real-time escalation with guardian alerts via email/WhatsApp.
3. **Research-grade analytics** — IEEE-ready metrics endpoint with emotion distribution, risk trend, personalization score.
4. **Production-ready** — Docker, Render + Vercel deployment, PostgreSQL, Prometheus metrics, rate limiting, structured logging.
5. **Comprehensive test coverage** — 117 backend tests + Playwright E2E tests covering every critical flow.
