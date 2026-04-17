# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat.spec.ts >> Chat Flow >> emotion badge is visible on assistant response
- Location: tests/e2e/chat.spec.ts:130:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('span.capitalize').filter({ hasText: 'anxiety' })
Expected: visible
Error: strict mode violation: locator('span.capitalize').filter({ hasText: 'anxiety' }) resolved to 2 elements:
    1) <span class="inline-flex items-center gap-1 rounded-full border font-medium capitalize px-3 py-1 text-sm bg-orange-400/20 text-orange-300 border-orange-400/30">…</span> aka getByText('😰anxiety75%')
    2) <span class="text-slate-200 capitalize">anxiety</span> aka getByText('anxiety').nth(3)

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('span.capitalize').filter({ hasText: 'anxiety' })

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - complementary [ref=e3]:
      - generic [ref=e4]:
        - generic [ref=e5]: 🌟
        - generic [ref=e6]:
          - paragraph [ref=e7]: AI Wellness
          - paragraph [ref=e8]: Buddy
      - navigation [ref=e9]:
        - button "Chat" [ref=e10] [cursor=pointer]:
          - img [ref=e11]
          - text: Chat
        - button "Dashboard" [ref=e13] [cursor=pointer]:
          - img [ref=e14]
          - text: Dashboard
        - button "Journey" [ref=e19] [cursor=pointer]:
          - img [ref=e20]
          - text: Journey
        - button "Weekly Report" [ref=e23] [cursor=pointer]:
          - img [ref=e24]
          - text: Weekly Report
        - button "Profile" [ref=e27] [cursor=pointer]:
          - img [ref=e28]
          - text: Profile
      - generic [ref=e31]:
        - generic [ref=e32] [cursor=pointer]:
          - generic [ref=e33]:
            - img [ref=e34]
            - text: Ambient Sound
          - switch "Ambient Sound" [ref=e38]
        - button "🫁 Start Breathing" [ref=e40] [cursor=pointer]
      - button "Sign Out" [ref=e42] [cursor=pointer]:
        - img [ref=e43]
        - text: Sign Out
    - main [ref=e47]:
      - generic [ref=e48]:
        - generic [ref=e49]:
          - generic [ref=e51]: Anxiety
          - 'button "Language: EN" [ref=e54] [cursor=pointer]':
            - img [ref=e55]
            - text: "Language:"
            - generic [ref=e58]: EN
        - generic [ref=e59]:
          - generic [ref=e60]: 🌬️
          - generic [ref=e61]: Breathe
          - button "Start Breathing" [ref=e62] [cursor=pointer]
          - button "✕" [ref=e63] [cursor=pointer]
        - generic [ref=e64]:
          - generic [ref=e65]:
            - main [ref=e66]:
              - generic [ref=e68]:
                - generic [ref=e69]: U
                - generic [ref=e71]: I'm feeling very anxious about everything.
              - generic [ref=e73]:
                - generic [ref=e74]: 🤖
                - generic [ref=e75]:
                  - generic [ref=e76]: Let's work through this together.
                  - button "Emotion insights" [ref=e78] [cursor=pointer]:
                    - img [ref=e79]
                    - text: Emotion insights
                    - img [ref=e81]
            - generic [ref=e83]:
              - generic [ref=e84]:
                - textbox "Message input" [ref=e85]:
                  - /placeholder: Type a message…
                - button "Send" [disabled] [ref=e86]:
                  - img [ref=e87]
              - paragraph [ref=e90]: AI Wellness Buddy is not a substitute for professional mental health care.
          - generic [ref=e93]:
            - generic [ref=e94]:
              - heading "🧠 AI Insights" [level=3] [ref=e95]
              - generic [ref=e96]: "Response Mode: generic"
              - generic [ref=e97]: "Dominant Emotion: anxiety"
              - generic [ref=e99]:
                - generic [ref=e100]: Personalization Score
                - generic [ref=e101]: 0%
              - generic [ref=e103]: "Trigger Signals: No trigger signals detected"
            - generic [ref=e104]:
              - heading "📊 Emotion Analysis" [level=3] [ref=e105]
              - generic [ref=e106]:
                - generic [ref=e107]: Dominant Emotion
                - generic [ref=e108]:
                  - generic [ref=e109]: 😰
                  - generic [ref=e110]: anxiety
                  - generic [ref=e111]: 75%
              - generic [ref=e112]:
                - generic [ref=e113]: Recent Pattern
                - generic [ref=e115]:
                  - generic [ref=e116]: anxiety
                  - generic [ref=e120]: 75%
            - generic [ref=e121]:
              - heading "🛡️ Risk Assessment" [level=3] [ref=e122]
              - generic [ref=e123]:
                - generic [ref=e124]:
                  - generic [ref=e125]: Risk Level
                  - generic [ref=e126]: Low
                - generic [ref=e128]: 0% risk detected
              - generic [ref=e130]:
                - generic [ref=e131]: Model Confidence
                - generic [ref=e132]: 75%
              - paragraph [ref=e136]: Risk analysis is not available yet. Continue chatting to generate risk signals.
              - paragraph [ref=e138]: ℹ️ If you're in crisis, please contact emergency services or a mental health professional immediately.
        - button "Start Voice" [ref=e141] [cursor=pointer]:
          - img [ref=e142]
  - button "Open Next.js Dev Tools" [ref=e150] [cursor=pointer]:
    - img [ref=e151]
  - alert [ref=e154]
```

# Test source

```ts
  51  |   emotion = "sadness",
  52  |   confidence = 0.82,
  53  | ) {
  54  |   // Use a URL predicate to match /api/v1/chat (POST) but never /api/v1/chat/history
  55  |   await page.route(
  56  |     (url) =>
  57  |       url.href.startsWith(`${API}/api/v1/chat`) &&
  58  |       !url.pathname.includes("/history"),
  59  |     (route) => {
  60  |       if (route.request().method() === "POST") {
  61  |         route.fulfill({
  62  |           status: 200,
  63  |           contentType: "application/json",
  64  |           body: JSON.stringify({
  65  |             session_id: "test-session-123",
  66  |             reply,
  67  |             primary_emotion: emotion,
  68  |             confidence,
  69  |             is_high_risk: false,
  70  |             escalation_message: null,
  71  |             scores: [{ emotion, score: confidence }],
  72  |           }),
  73  |         });
  74  |       } else {
  75  |         route.continue();
  76  |       }
  77  |     },
  78  |   );
  79  | }
  80  | 
  81  | // ---------------------------------------------------------------------------
  82  | // Tests
  83  | // ---------------------------------------------------------------------------
  84  | 
  85  | test.describe("Chat Flow", () => {
  86  |   test("send a message → user bubble appears in conversation", async ({
  87  |     page,
  88  |   }) => {
  89  |     await injectToken(page);
  90  |     await mockChatHistory(page);
  91  |     await mockChatPost(page);
  92  | 
  93  |     await page.goto("/chat");
  94  | 
  95  |     const textarea = page.getByPlaceholder(/Type a message/i);
  96  |     await textarea.fill("Hello, I need some support today.");
  97  | 
  98  |     // Send via button click
  99  |     await page.click('[data-testid="send-message"]');
  100 | 
  101 |     // User message bubble should be visible
  102 |     await expect(
  103 |       page.getByText("Hello, I need some support today."),
  104 |     ).toBeVisible({ timeout: 5_000 });
  105 |   });
  106 | 
  107 |   test("receive assistant response after sending message", async ({ page }) => {
  108 |     await injectToken(page);
  109 |     await mockChatHistory(page);
  110 |     await mockChatPost(
  111 |       page,
  112 |       "I hear you. That sounds really difficult.",
  113 |       "sadness",
  114 |     );
  115 | 
  116 |     await page.goto("/chat");
  117 | 
  118 |     await page
  119 |       .getByPlaceholder(/Type a message/i)
  120 |       .fill("I've been feeling very sad lately.");
  121 | 
  122 |     await page.click('[data-testid="send-message"]');
  123 | 
  124 |     // Assistant reply should appear
  125 |     await expect(
  126 |       page.getByText("I hear you. That sounds really difficult."),
  127 |     ).toBeVisible({ timeout: 10_000 });
  128 |   });
  129 | 
  130 |   test("emotion badge is visible on assistant response", async ({ page }) => {
  131 |     await injectToken(page);
  132 |     await mockChatHistory(page);
  133 |     await mockChatPost(page, "Let's work through this together.", "anxiety", 0.75);
  134 | 
  135 |     await page.goto("/chat");
  136 | 
  137 |     await page
  138 |       .getByPlaceholder(/Type a message/i)
  139 |       .fill("I'm feeling very anxious about everything.");
  140 | 
  141 |     await page.click('[data-testid="send-message"]');
  142 | 
  143 |     // Wait for the reply to appear first
  144 |     await expect(
  145 |       page.getByText("Let's work through this together."),
  146 |     ).toBeVisible({ timeout: 10_000 });
  147 | 
  148 |     // EmotionBadge renders a capitalised span containing the emotion label
  149 |     await expect(
  150 |       page.locator("span.capitalize", { hasText: "anxiety" }),
> 151 |     ).toBeVisible({ timeout: 5_000 });
      |       ^ Error: expect(locator).toBeVisible() failed
  152 |   });
  153 | 
  154 |   test("emotion badge shows confidence percentage", async ({ page }) => {
  155 |     await injectToken(page);
  156 |     await mockChatHistory(page);
  157 |     await mockChatPost(page, "You're not alone in this.", "sadness", 0.9);
  158 | 
  159 |     await page.goto("/chat");
  160 | 
  161 |     await page
  162 |       .getByPlaceholder(/Type a message/i)
  163 |       .fill("I feel hopeless.");
  164 | 
  165 |     await page.click('[data-testid="send-message"]');
  166 | 
  167 |     await expect(page.getByText("You're not alone in this.")).toBeVisible({
  168 |       timeout: 10_000,
  169 |     });
  170 | 
  171 |     // Confidence is rendered as "90%" next to the emotion label
  172 |     await expect(page.getByText("90%")).toBeVisible({ timeout: 5_000 });
  173 |   });
  174 | 
  175 |   test("send via Enter key works", async ({ page }) => {
  176 |     await injectToken(page);
  177 |     await mockChatHistory(page);
  178 |     await mockChatPost(page, "I'm here to help.", "neutral");
  179 | 
  180 |     await page.goto("/chat");
  181 | 
  182 |     const textarea = page.getByPlaceholder(/Type a message/i);
  183 |     await textarea.fill("How are you?");
  184 |     await textarea.press("Enter");
  185 | 
  186 |     await expect(page.getByText("How are you?")).toBeVisible({
  187 |       timeout: 5_000,
  188 |     });
  189 |   });
  190 | 
  191 |   test("unauthenticated visit redirects to /login", async ({ page }) => {
  192 |     // No token injected
  193 |     await page.addInitScript(() => window.localStorage.clear());
  194 |     await page.goto("/chat");
  195 | 
  196 |     await page.waitForURL("**/login", { timeout: 5_000 });
  197 |     expect(page.url()).toContain("/login");
  198 |   });
  199 | 
  200 |   test("chat history is loaded and displayed on mount", async ({ page }) => {
  201 |     await injectToken(page);
  202 | 
  203 |     const historyMessages = [
  204 |       {
  205 |         role: "user",
  206 |         content: "Previous user message",
  207 |         emotion: null,
  208 |         created_at: new Date().toISOString(),
  209 |       },
  210 |       {
  211 |         role: "assistant",
  212 |         content: "Previous assistant reply",
  213 |         emotion: "neutral",
  214 |         created_at: new Date().toISOString(),
  215 |       },
  216 |     ];
  217 | 
  218 |     await mockChatHistory(page, historyMessages);
  219 | 
  220 |     await page.goto("/chat");
  221 | 
  222 |     // Both history messages should be shown after load
  223 |     await expect(page.getByText("Previous user message")).toBeVisible({
  224 |       timeout: 5_000,
  225 |     });
  226 |     await expect(page.getByText("Previous assistant reply")).toBeVisible({
  227 |       timeout: 5_000,
  228 |     });
  229 |   });
  230 | });
  231 | 
```