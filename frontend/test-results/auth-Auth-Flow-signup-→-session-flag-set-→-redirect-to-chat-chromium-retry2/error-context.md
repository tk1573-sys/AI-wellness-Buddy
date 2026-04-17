# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Auth Flow >> signup → session flag set → redirect to /chat
- Location: tests/e2e/auth.spec.ts:73:7

# Error details

```
TimeoutError: page.waitForURL: Timeout 10000ms exceeded.
=========================== logs ===========================
waiting for navigation to "**/chat" until "load"
  navigated to "http://localhost:3000/onboarding"
============================================================
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e3]:
    - generic [ref=e4]:
      - text: 🌟
      - heading "Set Up Your Profile" [level=1] [ref=e5]
      - paragraph [ref=e6]: Help us personalize your wellness experience
    - generic [ref=e7]:
      - generic [ref=e10]: Basic Info
      - generic [ref=e13]: Emotional History
      - generic [ref=e16]: Trigger Identification
      - generic [ref=e19]: Lifestyle Habits
      - generic [ref=e22]: Personal Background
      - generic [ref=e25]: Guardian Alerts
    - generic [ref=e26]:
      - generic [ref=e27]:
        - heading "Basic Info" [level=2] [ref=e28]
        - paragraph [ref=e29]: Tell us a bit about yourself
      - generic [ref=e30]:
        - generic [ref=e31]:
          - generic [ref=e32]:
            - generic [ref=e33]: Age
            - spinbutton [ref=e34]
          - generic [ref=e35]:
            - generic [ref=e36]: Gender
            - combobox [ref=e37]:
              - option "Select" [selected]
              - option "Male"
              - option "Female"
              - option "Non-binary"
              - option "Prefer not to say"
        - generic [ref=e38]:
          - generic [ref=e39]: Occupation
          - textbox "e.g. Software Engineer, Student…" [ref=e40]
      - generic [ref=e41]:
        - button "Skip for now" [ref=e43] [cursor=pointer]
        - button "Next →" [ref=e44] [cursor=pointer]
    - paragraph [ref=e45]: Step 1 of 6
  - button "Open Next.js Dev Tools" [ref=e51] [cursor=pointer]:
    - img [ref=e52]
  - alert [ref=e55]
```

# Test source

```ts
  1   | /**
  2   |  * Auth Flow — end-to-end tests
  3   |  *
  4   |  * Covers:
  5   |  *   1. Signup  → token stored → redirect to /chat
  6   |  *   2. Login   → token stored → redirect to /chat
  7   |  *   3. Invalid login → error toast shown, user stays on /login
  8   |  *
  9   |  * All backend API calls are intercepted with page.route() so the tests
  10  |  * run fully in CI without a live backend.
  11  |  */
  12  | 
  13  | import { test, expect, type Page } from "@playwright/test";
  14  | 
  15  | // Backend origin as seen by the browser (matches NEXT_PUBLIC_API_URL default)
  16  | const API = "http://localhost:8000";
  17  | 
  18  | // Fake JWT returned by the mocked auth endpoints
  19  | const FAKE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.token";
  20  | 
  21  | /** Clear localStorage before each test so tokens never leak between tests. */
  22  | test.beforeEach(async ({ page }) => {
  23  |   await page.addInitScript(() => window.localStorage.clear());
  24  | });
  25  | 
  26  | // ---------------------------------------------------------------------------
  27  | // Helpers
  28  | // ---------------------------------------------------------------------------
  29  | 
  30  | /** Set up the mock auth endpoints and a stub history endpoint. */
  31  | async function mockAuthSuccess(
  32  |   page: Page,
  33  |   endpoint: "signup" | "login",
  34  |   status = 200,
  35  | ) {
  36  |   await page.route(`${API}/api/v1/auth/${endpoint}`, (route) =>
  37  |     route.fulfill({
  38  |       status,
  39  |       contentType: "application/json",
  40  |       body: JSON.stringify({
  41  |         access_token: FAKE_TOKEN,
  42  |         token_type: "bearer",
  43  |         expires_in: 3600,
  44  |       }),
  45  |     }),
  46  |   );
  47  | 
  48  |   // Stub chat history so the /chat page loads cleanly after redirect
  49  |   await page.route(`${API}/api/v1/chat/history*`, (route) =>
  50  |     route.fulfill({
  51  |       status: 200,
  52  |       contentType: "application/json",
  53  |       body: JSON.stringify([]),
  54  |     }),
  55  |   );
  56  | }
  57  | 
  58  | async function mockAuthFailure(page: Page, endpoint: "signup" | "login") {
  59  |   await page.route(`${API}/api/v1/auth/${endpoint}`, (route) =>
  60  |     route.fulfill({
  61  |       status: 401,
  62  |       contentType: "application/json",
  63  |       body: JSON.stringify({ detail: "Incorrect email or password." }),
  64  |     }),
  65  |   );
  66  | }
  67  | 
  68  | // ---------------------------------------------------------------------------
  69  | // Tests
  70  | // ---------------------------------------------------------------------------
  71  | 
  72  | test.describe("Auth Flow", () => {
  73  |   test("signup → session flag set → redirect to /chat", async ({ page }) => {
  74  |     await mockAuthSuccess(page, "signup", 201);
  75  |     await page.goto("/signup");
  76  | 
  77  |     // Fill the registration form
  78  |     await page.fill("#email", "e2etest@example.com");
  79  |     await page.fill("#username", "e2euser");
  80  |     await page.fill("#password", "Passw0rd!");
  81  | 
  82  |     await page.click('button[type="submit"]');
  83  | 
  84  |     // Should land on the chat page
> 85  |     await page.waitForURL("**/chat", { timeout: 10_000 });
      |                ^ TimeoutError: page.waitForURL: Timeout 10000ms exceeded.
  86  |     expect(page.url()).toContain("/chat");
  87  | 
  88  |     // Session presence flag must be set in the wb_logged_in cookie.
  89  |     // The JWT itself lives in an HttpOnly cookie set by the backend; only
  90  |     // the non-HttpOnly flag is readable from JavaScript.
  91  |     const cookies = await page.context().cookies();
  92  |     const flag = cookies.find((c) => c.name === "wb_logged_in");
  93  |     expect(flag?.value).toBe("1");
  94  |   });
  95  | 
  96  |   test("login → session flag set → redirect to /chat", async ({ page }) => {
  97  |     await mockAuthSuccess(page, "login");
  98  |     await page.goto("/login");
  99  | 
  100 |     await page.fill("#email", "e2etest@example.com");
  101 |     await page.fill("#password", "Passw0rd!");
  102 | 
  103 |     await page.click('button[type="submit"]');
  104 | 
  105 |     await page.waitForURL("**/chat", { timeout: 10_000 });
  106 |     expect(page.url()).toContain("/chat");
  107 | 
  108 |     // The wb_logged_in flag cookie must be present after a successful login.
  109 |     const cookies = await page.context().cookies();
  110 |     const flag = cookies.find((c) => c.name === "wb_logged_in");
  111 |     expect(flag?.value).toBe("1");
  112 |   });
  113 | 
  114 |   test("invalid login → error toast shown, stays on /login", async ({
  115 |     page,
  116 |   }) => {
  117 |     await mockAuthFailure(page, "login");
  118 |     await page.goto("/login");
  119 | 
  120 |     await page.fill("#email", "wrong@example.com");
  121 |     await page.fill("#password", "BadPass99!");
  122 | 
  123 |     await page.click('button[type="submit"]');
  124 | 
  125 |     // react-hot-toast renders a live-region with role="status"
  126 |     await expect(page.locator('[role="status"]').first()).toBeVisible({
  127 |       timeout: 5_000,
  128 |     });
  129 | 
  130 |     // Must NOT have navigated away from the login page
  131 |     expect(page.url()).toContain("/login");
  132 |   });
  133 | 
  134 |   test("signup form client-side validation — invalid email", async ({
  135 |     page,
  136 |   }) => {
  137 |     await page.goto("/signup");
  138 | 
  139 |     await page.fill("#email", "not-an-email");
  140 |     await page.fill("#username", "user");
  141 |     await page.fill("#password", "Passw0rd!");
  142 | 
  143 |     await page.click('button[type="submit"]');
  144 | 
  145 |     // The form shows an inline validation error (no API call made)
  146 |     await expect(page.getByText("Enter a valid email.")).toBeVisible({
  147 |       timeout: 3_000,
  148 |     });
  149 |   });
  150 | 
  151 |   test("login form client-side validation — empty password", async ({
  152 |     page,
  153 |   }) => {
  154 |     await page.goto("/login");
  155 | 
  156 |     await page.fill("#email", "test@example.com");
  157 |     // Leave password blank
  158 | 
  159 |     await page.click('button[type="submit"]');
  160 | 
  161 |     await expect(page.getByText("Password is required.")).toBeVisible({
  162 |       timeout: 3_000,
  163 |     });
  164 |   });
  165 | });
  166 | 
```