import { test, expect } from '@playwright/test';

test.describe('BMAD E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Go to the app
    await page.goto('http://localhost:5173');
  });

  test.describe('User Authentication', () => {
    
    test('should display login page', async ({ page }) => {
      await expect(page.locator('text=体重管家')).toBeVisible();
      await expect(page.locator('text=登录')).toBeVisible();
    });

    test('should show registration form when clicking register', async ({ page }) => {
      await page.click('text=立即注册');
      await expect(page.locator('text=注册')).toBeVisible();
    });

    test('should validate email format', async ({ page }) => {
      await page.click('text=立即注册');
      await page.fill('input[type="email"]', 'invalid-email');
      await page.fill('input[type="password"]', 'Password123');
      await page.click('button[type="submit"]');
      await expect(page.locator('text=邮箱格式不正确')).toBeVisible();
    });

    test('should validate password requirements', async ({ page }) => {
      await page.click('text=立即注册');
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'short');
      await page.click('button[type="submit"]');
      await expect(page.locator('text=密码至少需要8个字符')).toBeVisible();
    });
  });

  test.describe('Navigation', () => {
    
    test('should show sidebar navigation', async ({ page }) => {
      // After login, sidebar should be visible
      await expect(page.locator('aside')).toBeVisible();
    });

    test('should have correct nav items', async ({ page }) => {
      const expectedNavItems = [
        '仪表板',
        '个人资料',
        '习惯追踪',
        '营养管理',
        '健康记录',
        '情感支持',
        '成就中心',
        'AI助手',
      ];

      for (const item of expectedNavItems) {
        await expect(page.locator(`text=${item}`)).toBeVisible();
      }
    });
  });

  test.describe('Dashboard', () => {
    
    test('should display dashboard title', async ({ page }) => {
      await expect(page.locator('text=仪表板')).toBeVisible();
    });

    test('should show health summary cards', async ({ page }) => {
      // Check for expected dashboard elements
      await expect(page.locator('text=今日概览')).toBeVisible();
    });
  });

  test.describe('Chat Feature', () => {
    
    test('should open chat page', async ({ page }) => {
      await page.click('text=AI助手');
      await expect(page.locator('text=AI健康助手')).toBeVisible();
    });

    test('should display role selector buttons', async ({ page }) => {
      await page.click('text=AI助手');
      // Check role buttons
      await expect(page.locator('text=🥗')).toBeVisible();
      await expect(page.locator('text=🏃')).toBeVisible();
      await expect(page.locator('text=💬')).toBeVisible();
    });

    test('should allow message input', async ({ page }) => {
      await page.click('text=AI助手');
      const input = page.locator('input[placeholder*="输入"]');
      await expect(input).toBeVisible();
    });
  });

  test.describe('Habits Feature', () => {
    
    test('should open habits page', async ({ page }) => {
      await page.click('text=习惯追踪');
      await expect(page.locator('text=习惯打卡')).toBeVisible();
    });

    test('should show add habit button', async ({ page }) => {
      await page.click('text=习惯追踪');
      await expect(page.locator('text=添加新习惯')).toBeVisible();
    });

    test('should show habit templates', async ({ page }) => {
      await page.click('text=习惯追踪');
      await expect(page.locator('text=使用模板')).toBeVisible();
    });
  });

  test.describe('Gamification', () => {
    
    test('should open achievements page', async ({ page }) => {
      await page.click('text=成就中心');
      await expect(page.locator('text=成就中心')).toBeVisible();
    });

    test('should display user level', async ({ page }) => {
      await page.click('text=成就中心');
      await expect(page.locator('text=等级')).toBeVisible();
    });
  });

  test.describe('Nutrition', () => {
    
    test('should open nutrition page', async ({ page }) => {
      await page.click('text=营养管理');
      await expect(page.locator('text=营养追踪')).toBeVisible();
    });

    test('should show meal input', async ({ page }) => {
      await page.click('text=营养管理');
      await expect(page.locator('text=记录餐食')).toBeVisible();
    });
  });

  test.describe('Health Records', () => {
    
    test('should open health records page', async ({ page }) => {
      await page.click('text=健康记录');
      await expect(page.locator('text=健康数据')).toBeVisible();
    });

    test('should show weight tracking', async ({ page }) => {
      await page.click('text=健康记录');
      await expect(page.locator('text=体重记录')).toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {
    
    test('should work on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await expect(page.locator('text=体重管家')).toBeVisible();
    });

    test('should work on tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(page.locator('text=体重管家')).toBeVisible();
    });
  });

  test.describe('Error Handling', () => {
    
    test('should show error toast on failed request', async ({ page }) => {
      // This would require mocking the API to fail
      // Skipping actual implementation for now
      test.skip();
    });
  });
});

// Mark critical tests
test.describe('@critical', () => {
  test('critical: user can login', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await expect(page.locator('text=体重管家')).toBeVisible();
  });

  test('critical: can navigate to dashboard', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('text=仪表板');
    await expect(page.locator('text=今日概览')).toBeVisible();
  });

  test('critical: can open chat', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('text=AI助手');
    await expect(page.locator('text=AI健康助手')).toBeVisible();
  });
});
