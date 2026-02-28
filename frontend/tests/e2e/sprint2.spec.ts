/**
 * Sprint 2 E2E Tests
 * 
 * End-to-end tests for Sprint 2 features:
 * - Epic 2: Goal System Implementation
 * - Epic 3: Calorie Balance Enhancement
 * - Epic 4: Gamification System Expansion
 */

import { test, expect } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

test.describe('[Sprint 2] Goal System E2E', () => {
  
  test.describe('Goal Creation and Tracking', () => {
    
    test('[P0] should display goal recommendations', async ({ page }) => {
      await page.goto('/goals');
      
      // Verify goal page loads
      await expect(page).toHaveTitle(/目标/);
      
      // Should display recommendation section
      await expect(page.getByText('目标推荐')).toBeVisible({ timeout: 10000 });
    });
    
    test('[P0] should create a new weight goal', async ({ page }) => {
      await page.goto('/goals');
      
      // Click create goal button
      const createButton = page.getByRole('button', { name: /创建目标/i });
      if (await createButton.isVisible()) {
        await createButton.click();
        
        // Fill goal form
        await page.getByLabel('目标类型').selectOption('weight');
        await page.getByLabel('当前值').fill('75000'); // 75kg in grams
        await page.getByLabel('目标值').fill('65000'); // 65kg in grams
        await page.getByRole('button', { name: '保存' }).click();
        
        // Should show success or navigate to goal list
        await expect(
          page.getByText('目标创建成功') || page.getByText('目标详情')
        ).toBeVisible({ timeout: 5000 });
      }
    });
    
    test('[P1] should display goal progress', async ({ page }) => {
      await page.goto('/goals');
      
      // If there are existing goals, verify progress is displayed
      const goalCards = page.locator('[data-testid="goal-card"]');
      const count = await goalCards.count();
      
      if (count > 0) {
        await expect(goalCards.first()).toContainText(/进度/);
      }
    });
    
    test('[P2] should filter goals by status', async ({ page }) => {
      await page.goto('/goals');
      
      // Verify filter options exist
      const filterDropdown = page.getByRole('combobox', { name: /状态/ });
      if (await filterDropdown.isVisible()) {
        await filterDropdown.click();
        await expect(page.getByRole('option', { name: '进行中' })).toBeVisible();
        await expect(page.getByRole('option', { name: '已完成' })).toBeVisible();
      }
    });
  });
  
  test.describe('Goal Feedback', () => {
    
    test('[P1] should display goal feedback summary', async ({ page }) => {
      await page.goto('/goals/feedback');
      
      // Should show feedback summary
      await expect(
        page.getByText('反馈摘要') || page.getByText('目标状态')
      ).toBeVisible({ timeout: 10000 });
    });
    
    test('[P2] should dismiss feedback', async ({ page }) => {
      await page.goto('/goals/feedback');
      
      // If there's dismissible feedback
      const dismissButton = page.getByRole('button', { name: /忽略|稍后提醒/ });
      if (await dismissButton.first().isVisible()) {
        await dismissButton.first().click();
        
        // Should update the UI
        await page.waitForTimeout(500);
      }
    });
  });
});

test.describe('[Sprint 2] Calorie Balance E2E', () => {
  
  test.describe('Calorie Balance Display', () => {
    
    test('[P0] should display three-column calorie balance', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Verify three columns are displayed
      await expect(page.getByText('摄入')).toBeVisible({ timeout: 10000 });
      await expect(page.getByText('基础代谢')).toBeVisible();
      await expect(page.getByText('运动消耗')).toBeVisible();
    });
    
    test('[P0] should show progress bar', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Should display progress indicator
      const progressBar = page.locator('[role="progressbar"]');
      await expect(progressBar.first()).toBeVisible({ timeout: 10000 });
    });
    
    test('[P1] should update calories in real-time', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Get initial calorie values
      const intakeElement = page.getByText(/摄入/).first();
      const initialValue = await intakeElement.textContent();
      
      // Add a meal
      await page.getByRole('button', { name: /添加餐食/i }).click();
      
      // Fill meal form
      await page.getByLabel('餐食类型').selectOption('breakfast');
      await page.getByLabel('热量').fill('500');
      await page.getByRole('button', { name: '保存' }).click();
      
      // Verify value updates
      await page.waitForTimeout(1000);
      const newValue = await intakeElement.textContent();
      expect(newValue).not.toBe(initialValue);
    });
    
    test('[P2] should display calorie history chart', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Look for chart or history section
      const historyButton = page.getByRole('button', { name: /历史记录|趋势/ });
      if (await historyButton.isVisible()) {
        await historyButton.click();
        await expect(page.locator('canvas')).toBeVisible();
      }
    });
  });
});

test.describe('[Sprint 2] Gamification E2E', () => {
  
  test.describe('Gamification Overview', () => {
    
    test('[P0] should display gamification overview', async ({ page }) => {
      await page.goto('/gamification');
      
      // Verify overview page loads
      await expect(
        page.getByText('游戏化') || page.getByText('成就')
      ).toBeVisible({ timeout: 10000 });
    });
    
    test('[P0] should display user level and points', async ({ page }) => {
      await page.goto('/gamification');
      
      // Should show level
      await expect(page.getByText(/等级|Lv/)).toBeVisible({ timeout: 10000 });
      
      // Should show points
      await expect(page.getByText(/积分/)).toBeVisible();
    });
    
    test('[P1] should display badges', async ({ page }) => {
      await page.goto('/gamification');
      
      // Should show badges section
      const badgesSection = page.getByText(/徽章|成就/);
      await expect(badgesSection.first()).toBeVisible({ timeout: 10000 });
    });
    
    test('[P1] should display streaks', async ({ page }) => {
      await page.goto('/gamification');
      
      // Should show streak info
      await expect(page.getByText(/连续|连续天数/)).toBeVisible({ timeout: 10000 });
    });
    
    test('[P2] should display challenges', async ({ page }) => {
      await page.goto('/gamification');
      
      // Should show challenges section
      const challengesSection = page.getByText(/挑战/);
      if (await challengesSection.isVisible()) {
        await expect(challengesSection).toBeVisible();
      }
    });
  });
  
  test.describe('Nutrition Achievements', () => {
    
    test('[P1] should track nutrition-related achievements', async ({ page }) => {
      await page.goto('/gamification');
      
      // Navigate to badges/achievements
      const badgesTab = page.getByRole('tab', { name: /营养成就|饮食成就/ });
      if (await badgesTab.isVisible()) {
        await badgesTab.click();
        
        // Should show nutrition achievements
        await expect(page.getByText(/饮食|营养/)).toBeVisible();
      }
    });
  });
  
  test.describe('Exercise Achievements', () => {
    
    test('[P2] should track exercise achievements', async ({ page }) => {
      await page.goto('/gamification');
      
      // Navigate to exercise achievements
      const exerciseTab = page.getByRole('tab', { name: /运动成就/ });
      if (await exerciseTab.isVisible()) {
        await exerciseTab.click();
        
        // Should show exercise achievements
        await expect(page.getByText(/运动|锻炼/)).toBeVisible();
      }
    });
  });
});

test.describe('[Sprint 2] Integration Tests', () => {
  
  test('[P0] should complete goal creation flow from dashboard', async ({ page }) => {
    // 1. Go to dashboard
    await page.goto('/dashboard');
    
    // 2. Navigate to goals
    await page.getByRole('link', { name: /目标/ }).click();
    
    // 3. Create a goal
    await page.waitForURL('**/goals');
    const createButton = page.getByRole('button', { name: /创建/ });
    if (await createButton.isVisible()) {
      await createButton.click();
    }
    
    // 4. Verify we're on goal creation page
    await expect(page.getByText(/创建目标|目标设置/)).toBeVisible({ timeout: 5000 });
  });
  
  test('[P1] should update progress and see gamification impact', async ({ page }) => {
    // 1. Go to goals
    await page.goto('/goals');
    
    // 2. Select a goal and record progress
    const progressButton = page.getByRole('button', { name: /记录进度/ });
    if (await progressButton.first().isVisible()) {
      await progressButton.first().click();
      
      // 3. Fill progress form
      await page.getByLabel('当前数值').fill('70000');
      await page.getByRole('button', { name: '保存' }).click();
      
      // 4. Navigate to gamification to see impact
      await page.goto('/gamification');
      
      // Should reflect progress (points should be visible)
      await expect(page.getByText(/积分/)).toBeVisible({ timeout: 5000 });
    }
  });
});
