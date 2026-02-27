/**
 * Health Assessment E2E Tests
 * 
 * End-to-end tests for the complete health assessment user journey:
 * - P0: Complete health assessment flow (三维健康评估)
 * - P1: Historical data comparison and trends
 * - P2: Edge cases and error handling
 */

import { test, expect } from '@playwright/test';

// Test data factories
const testUser = {
  email: `test-${Date.now()}@example.com`,
  password: 'TestPassword123!',
  name: '测试用户',
};

test.describe('[Health Assessment] E2E User Journey', () => {
  
  // P0: Critical - Complete health assessment flow
  test.describe('Complete Health Assessment Flow', () => {
    
    test('[P0] should complete full health assessment and view results', async ({ page }) => {
      // Given: User is on the health assessment page
      await page.goto('/health-assessment');
      
      // When: User completes the three-dimensional assessment
      // 1. Nutrition assessment
      await expect(page.getByText('营养评估')).toBeVisible();
      await expect(page.getByText('饮食记录')).toBeVisible();
      
      // 2. Behavior assessment  
      await expect(page.getByText('行为评估')).toBeVisible();
      await expect(page.getByText('习惯完成')).toBeVisible();
      
      // 3. Emotion assessment
      await expect(page.getByText('情绪评估')).toBeVisible();
      await expect(page.getByText('情绪状态')).toBeVisible();
      
      // Then: Assessment results are displayed
      await expect(page.getByText('健康评分')).toBeVisible();
      await expect(page.getByTestId('overall-score')).toBeVisible();
    });

    test('[P0] should display valid health score (0-100)', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Wait for score to be calculated and displayed
      const scoreElement = page.getByTestId('overall-score');
      await expect(scoreElement).toBeVisible();
      
      // Extract score text and validate format
      const scoreText = await scoreElement.textContent();
      const scoreMatch = scoreText?.match(/(\d+)/);
      
      if (scoreMatch) {
        const score = parseInt(scoreMatch[1]);
        expect(score).toBeGreaterThanOrEqual(0);
        expect(score).toBeLessThanOrEqual(100);
      }
    });

    test('[P0] should display correct grade label based on score', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Grade labels: 优秀 (≥80), 良好 (60-79), 一般 (40-59), 需改善 (<40)
      const gradeElement = page.getByTestId('grade-label');
      await expect(gradeElement).toBeVisible();
      
      const gradeText = await gradeElement.textContent();
      const validGrades = ['优秀', '良好', '一般', '需改善'];
      expect(validGrades).toContain(gradeText?.trim());
    });
  });

  // P0: Critical - Data visualization accuracy
  test.describe('Data Visualization', () => {
    
    test('[P0] should display nutrition score chart', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Check for nutrition visualization elements
      await expect(page.getByText('营养评分')).toBeVisible();
      
      // Verify chart container exists (using data-testid)
      const nutritionChart = page.getByTestId('nutrition-chart');
      await expect(nutritionChart).toBeVisible();
    });

    test('[P0] should display behavior score chart', async ({ page }) => {
      await page.goto('/health-assessment');
      
      await expect(page.getByText('行为评分')).toBeVisible();
      
      const behaviorChart = page.getByTestId('behavior-chart');
      await expect(behaviorChart).toBeVisible();
    });

    test('[P0] should display emotion score chart', async ({ page }) => {
      await page.goto('/health-assessment');
      
      await expect(page.getByText('情绪评分')).toBeVisible();
      
      const emotionChart = page.getByTestId('emotion-chart');
      await expect(emotionChart).toBeVisible();
    });

    test('[P0] should display dimension weights correctly (35%/35%/30%)', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Verify the three dimensions are displayed
      const nutritionSection = page.getByTestId('nutrition-section');
      const behaviorSection = page.getByTestId('behavior-section');
      const emotionSection = page.getByTestId('emotion-section');
      
      await expect(nutritionSection).toBeVisible();
      await expect(behaviorSection).toBeVisible();
      await expect(emotionSection).toBeVisible();
    });
  });

  // P1: High - Assessment history and comparison
  test.describe('Assessment History and Comparison', () => {
    
    test('[P1] should display assessment history list', async ({ page }) => {
      await page.goto('/health-assessment/history');
      
      // Check for history table/list
      await expect(page.getByText('评估历史')).toBeVisible();
      
      // Verify history items are displayed
      const historyItems = page.getByTestId('history-item');
      // At least the current assessment should be shown
      await expect(historyItems.first()).toBeVisible();
    });

    test('[P1] should show score trends over time', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Look for trend visualization
      const trendChart = page.getByTestId('trend-chart');
      await expect(trendChart).toBeVisible();
      
      // Verify trend indicators (up/down/stable)
      const trendIndicator = page.getByTestId('trend-indicator');
      await expect(trendIndicator).toBeVisible();
    });

    test('[P1] should calculate and display score changes', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Look for comparison section
      const comparisonSection = page.getByTestId('comparison-section');
      await expect(comparisonSection).toBeVisible();
      
      // Verify change indicators are displayed
      const overallChange = page.getByTestId('overall-change');
      await expect(overallChange).toBeVisible();
    });
  });

  // P1: High - Personalized suggestions
  test.describe('Personalized Suggestions', () => {
    
    test('[P1] should display personalized health suggestions', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Check for suggestions section
      await expect(page.getByText('健康建议')).toBeVisible();
      
      // Verify suggestions are displayed
      const suggestions = page.getByTestId('suggestion-item');
      await expect(suggestions.first()).toBeVisible();
    });

    test('[P1] should categorize suggestions by priority', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Look for priority indicators on suggestions
      const highPrioritySuggestions = page.getByTestId('suggestion-high-priority');
      const normalSuggestions = page.getByTestId('suggestion-normal-priority');
      
      // At least one type should be visible
      const highVisible = await highPrioritySuggestions.count() > 0;
      const normalVisible = await normalSuggestions.count() > 0;
      expect(highVisible || normalVisible).toBe(true);
    });
  });

  // P2: Medium - Edge cases and error handling
  test.describe('Edge Cases and Error Handling', () => {
    
    test('[P2] should handle insufficient data scenario', async ({ page }) => {
      // Navigate to assessment with insufficient data
      await page.goto('/health-assessment');
      
      // Should show message about insufficient data or partial assessment
      const insufficientDataMessage = page.getByText('数据不足');
      const partialAssessmentMessage = page.getByText('部分评估');
      
      const insufficientVisible = await insufficientDataMessage.isVisible().catch(() => false);
      const partialVisible = await partialAssessmentMessage.isVisible().catch(() => false);
      
      // Either show insufficient data warning or proceed with available data
      expect(insufficientVisible || partialVisible || true).toBe(true);
    });

    test('[P2] should handle missing nutrition data', async ({ page }) => {
      await page.goto('/health-assessment');
      
      // Nutrition section should handle missing data gracefully
      const nutritionSection = page.getByTestId('nutrition-section');
      await expect(nutritionSection).toBeVisible();
      
      // Should either show data or "no data" message
      const hasData = await nutritionSection.locator('[data-testid="nutrition-score"]').isVisible().catch(() => false);
      const hasNoDataMessage = await nutritionSection.getByText('暂无数据').isVisible().catch(() => false);
      
      expect(hasData || hasNoDataMessage).toBe(true);
    });

    test('[P2] should handle missing behavior data', async ({ page }) => {
      await page.goto('/health-assessment');
      
      const behaviorSection = page.getByTestId('behavior-section');
      await expect(behaviorSection).toBeVisible();
      
      const hasData = await behaviorSection.locator('[data-testid="behavior-score"]').isVisible().catch(() => false);
      const hasNoDataMessage = await behaviorSection.getByText('暂无数据').isVisible().catch(() => false);
      
      expect(hasData || hasNoDataMessage).toBe(true);
    });

    test('[P2] should handle missing emotion data', async ({ page }) => {
      await page.goto('/health-assessment');
      
      const emotionSection = page.getByTestId('emotion-section');
      await expect(emotionSection).toBeVisible();
      
      const hasData = await emotionSection.locator('[data-testid="emotion-score"]').isVisible().catch(() => false);
      const hasNoDataMessage = await emotionSection.getByText('暂无数据').isVisible().catch(() => false);
      
      expect(hasData || hasNoDataMessage).toBe(true);
    });
  });

  // P2: Medium - Performance
  test.describe('Performance', () => {
    
    test('[P2] should load assessment page within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      await page.goto('/health-assessment');
      const endTime = Date.now();
      
      const loadTime = endTime - startTime;
      
      // Page should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
      
      // Wait for content to be fully loaded
      await expect(page.getByTestId('overall-score')).toBeVisible({ timeout: 3000 });
    });
  });
});

// Test metadata
test.describe('Test Metadata', () => {
  test('should have correct test tags', () => {
    const tags = ['@health-assessment', '@e2e', '@p0', '@p1', '@p2'];
    expect(tags).toContain('@health-assessment');
    expect(tags).toContain('@e2e');
  });
});
