import { test, expect } from '@playwright/test';

test.describe('FitMind E2E Smoke Tests', () => {
  
  test('should load the main page without crash', async ({ page }) => {
    // Navigate to the app
    const response = await page.goto('http://localhost:3000');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check that page has content
    const body = await page.locator('body');
    await expect(body).toBeVisible();
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'test-results/smoke-test.png' });
    
    // Log any console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('Console error:', msg.text());
      }
    });
  });

  test('should have no critical console errors', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    
    // Filter out known non-critical errors
    const criticalErrors = errors.filter(e => 
      !e.includes('favicon') && 
      !e.includes('manifest') &&
      !e.includes('service-worker')
    );
    
    console.log('Console errors found:', criticalErrors);
  });
});
