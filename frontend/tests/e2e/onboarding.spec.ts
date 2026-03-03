import { test, expect } from '@playwright/test';

test.describe('Onboarding', () => {
  test('can access onboarding page', async ({ page }) => {
    await page.goto('/onboarding');
    await expect(page).toHaveURL(/.*onboarding/, { timeout: 10000 });
  });
});
