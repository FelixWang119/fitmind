import { test, expect } from '@playwright/test';

test.describe('FitMind E2E Tests', () => {
  
  test('should load login page directly', async ({ page }) => {
    // Go directly to login page
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/login-page.png' });
    
    // Log console errors
    page.on('console', msg => {
      console.log(`[${msg.type()}] ${msg.text()}`);
    });
  });

  test('should load root page', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
    
    await page.screenshot({ path: 'test-results/root-page.png' });
  });
});
