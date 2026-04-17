# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Auth Flow >> signup form client-side validation — invalid email
- Location: tests/e2e/auth.spec.ts:134:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('Enter a valid email.')
Expected: visible
Timeout: 3000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 3000ms
  - waiting for getByText('Enter a valid email.')

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - main [ref=e2]:
    - generic [ref=e3]:
      - generic [ref=e4]:
        - heading "Create Account" [level=1] [ref=e5]
        - paragraph [ref=e6]: Start your wellness journey today
      - generic [ref=e7]:
        - generic [ref=e8]:
          - generic [ref=e9]: Email
          - textbox "Email" [active] [ref=e10]:
            - /placeholder: you@example.com
            - text: not-an-email
        - generic [ref=e11]:
          - generic [ref=e12]: Username
          - textbox "Username" [ref=e13]:
            - /placeholder: yourname
            - text: user
        - generic [ref=e14]:
          - generic [ref=e15]: Password
          - textbox "Password" [ref=e16]:
            - /placeholder: Min. 8 chars, 1 uppercase, 1 digit
            - text: Passw0rd!
        - button "Create Account" [ref=e17] [cursor=pointer]
      - paragraph [ref=e18]:
        - text: Already have an account?
        - link "Sign in" [ref=e19] [cursor=pointer]:
          - /url: /login
  - button "Open Next.js Dev Tools" [ref=e25] [cursor=pointer]:
    - img [ref=e26]
  - alert [ref=e29]
```

# Test source

```ts
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
  85  |     await page.waitForURL("**/chat", { timeout: 10_000 });
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
> 146 |     await expect(page.getByText("Enter a valid email.")).toBeVisible({
      |                                                          ^ Error: expect(locator).toBeVisible() failed
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