import { Page } from '@playwright/test';

/**
 * Logs into the app via the Keycloak login form.
 * Call this before any test that navigates to a protected page.
 */
export async function loginAsUser(page: Page, username: string, password: string): Promise<void> {
  // Navigate to root — AuthProvider will redirect to Keycloak
  // baseURL is set in playwright.config.ts
  await page.goto('/');

  // Wait for Keycloak login form to appear
  await page.waitForSelector('#username', { timeout: 30_000 });

  // Fill credentials and submit
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('#kc-login');

  // Wait for redirect back to the app (URL changes back to localhost:3000)
  // Wait for redirect back to the app
  await page.waitForURL(/localhost:300[0-9]\//, { timeout: 30_000 });

  // Wait for the app to finish loading (AuthProvider sets authenticated=true)
  await page.waitForFunction(
    () => !document.body.innerText.includes('Authenticating') &&
          !document.body.innerText.includes('Login required'),
    { timeout: 15_000 }
  );
}

export async function loginAsUser1(page: Page): Promise<void> {
  return loginAsUser(page, 'user1', 'password');
}
