/**
 * Authentication Fixtures for Health Assessment Tests
 * 
 * Provides authenticated user state and auth tokens for API and E2E tests.
 * Uses Playwright's test.extend() pattern with auto-cleanup.
 */

import { test as base, expect } from '@playwright/test';

// Test user credentials
const testUserCredentials = {
  email: `test-${Date.now()}@example.com`,
  password: 'TestPassword123!',
  name: '测试用户',
};

// Extend base test with authentication fixtures
export const test = base.extend<{
  authToken: string;
  authenticatedPage: any;
}>({
  // Auth token fixture for API tests
  authToken: async ({ request }, use) => {
    // Get auth token via API
    const response = await request.post('/api/v1/auth/login', {
      data: {
        email: testUserCredentials.email,
        password: testUserCredentials.password,
      },
    });

    // Handle both success and failure cases
    let token = '';
    if (response.ok()) {
      const data = await response.json();
      token = data.token || data.access_token || '';
    }

    // Provide token to tests
    await use(token);

    // Cleanup: Token is stateless, no cleanup needed
  },

  // Authenticated page fixture for E2E tests
  authenticatedPage: async ({ page, request }, use) => {
    // Navigate to login page
    await page.goto('/login');

    // Fill login form
    await page.getByLabel('Email').fill(testUserCredentials.email);
    await page.getByLabel('Password').fill(testUserCredentials.password);

    // Submit and wait for navigation
    await page.getByRole('button', { name: 'Login' }).click();
    await page.waitForURL('**/dashboard');

    // Verify successful login
    const dashboardVisible = await page.getByText('Dashboard').isVisible().catch(() => false);
    expect(dashboardVisible).toBe(true);

    // Provide authenticated page to tests
    await use(page);

    // Cleanup: Logout after test
    try {
      await page.goto('/logout');
      await page.waitForURL('**/login');
    } catch (e) {
      // Logout may fail if session expired, which is fine
    }
  },
});

// Export helpers for test data setup
export async function setupAuthenticatedUser(request: any) {
  const response = await request.post('/api/v1/auth/register', {
    data: testUserCredentials,
  });

  if (!response.ok()) {
    throw new Error('Failed to create test user');
  }

  return await response.json();
}

export async function teardownUser(request: any, userId: number) {
  try {
    await request.delete(`/api/v1/users/${userId}`);
  } catch (e) {
    // User deletion may fail if user doesn't exist, which is fine
  }
}

export { testUserCredentials };
