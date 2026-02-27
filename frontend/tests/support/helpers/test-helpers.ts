/**
 * Helper Utilities for Health Assessment Tests
 * 
 * Common test utilities for assertions, waits, and data validation.
 */

import { Page, expect } from '@playwright/test';

/**
 * Wait for API response matching URL pattern
 */
export async function waitForApiResponse(page: Page, urlPattern: string, timeout = 5000) {
  return page.waitForResponse(
    (response) => response.url().includes(urlPattern) && response.ok(),
    { timeout }
  );
}

/**
 * Wait for element to be visible with custom timeout
 */
export async function waitForElement(page: Page, selector: string, timeout = 5000) {
  await page.waitForSelector(selector, { state: 'visible', timeout });
}

/**
 * Wait for page navigation with custom timeout
 */
export async function waitForNavigation(page: Page, timeout = 10000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Assert health score is within valid range
 */
export function assertValidScore(score: number) {
  expect(score).toBeGreaterThanOrEqual(0);
  expect(score).toBeLessThanOrEqual(100);
}

/**
 * Assert grade label is valid
 */
export function assertValidGrade(grade: string) {
  const validGrades = ['优秀', '良好', '一般', '需改善'];
  expect(validGrades).toContain(grade);
}

/**
 * Assert score-grade consistency
 */
export function assertScoreGradeConsistency(score: number, grade: string) {
  if (score >= 80) {
    expect(grade).toBe('优秀');
  } else if (score >= 60) {
    expect(grade).toBe('良好');
  } else if (score >= 40) {
    expect(grade).toBe('一般');
  } else {
    expect(grade).toBe('需改善');
  }
}

/**
 * Calculate completeness percentage
 */
export function calculateCompleteness(actualDays: number, requiredDays: number): number {
  if (requiredDays === 0) return 100;
  return Math.min(100, Math.round((actualDays / requiredDays) * 100));
}

/**
 * Assert data completeness thresholds
 */
export function assertDataCompleteness(
  foodDays: number,
  habitDays: number,
  sleepDays: number
) {
  const foodComplete = foodDays >= 7;
  const habitComplete = habitDays >= 14;
  const sleepComplete = sleepDays >= 7;

  return {
    foodComplete,
    habitComplete,
    sleepComplete,
    overallComplete: foodComplete && habitComplete && sleepComplete,
  };
}

/**
 * Retry helper for flaky operations
 */
export async function retry<T>(
  operation: () => Promise<T>,
  maxAttempts = 3,
  delayMs = 1000
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }

  throw lastError || new Error('Operation failed after retries');
}

/**
 * Generate timestamp for test data
 */
export function generateTimestamp(): string {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

/**
 * Sleep for specified milliseconds (use sparingly, prefer explicit waits)
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
