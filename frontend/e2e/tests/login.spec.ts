import { expect, test } from "@playwright/test";

// Backend base URL (FastAPI). The Playwright runner talks to it directly to
// seed data; the browser talks to it via NEXT_PUBLIC_API_URL.
const API_URL = process.env.E2E_API_URL ?? "http://localhost:8000";
const E2E_SECRET = process.env.E2E_SECRET ?? "dev-e2e-secret";

interface SeedResponse {
  guardian_token: string;
  dependants: { id: string; first_name: string; balance: string }[];
}

test("login with a seeded token shows the dashboard with a dependant", async ({
  page,
  request,
}) => {
  // 1. Seed the backend (creates guardian Alex + dependants Mia & Leo).
  const seedResponse = await request.post(`${API_URL}/api/v1/e2e/seed`, {
    headers: { "X-E2E-Secret": E2E_SECRET },
  });
  expect(seedResponse.ok()).toBeTruthy();
  const seed = (await seedResponse.json()) as SeedResponse;
  expect(seed.guardian_token).toBeTruthy();

  // 2. Log in via the dev seam: paste the guardian token on /login.
  await page.goto("/login");
  await page.getByLabel(/guardian token or id/i).fill(seed.guardian_token);
  await page.getByRole("button", { name: /continue/i }).click();

  // 3. Dashboard renders the seeded dependants.
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByText("Mia")).toBeVisible();
  await expect(page.getByText("Leo")).toBeVisible();
  await expect(page.getByTestId("dependant-card").first()).toBeVisible();
});
