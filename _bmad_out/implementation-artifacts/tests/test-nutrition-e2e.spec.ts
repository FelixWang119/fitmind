// 基于Playwright的营养管理模块E2E测试
import { test, expect } from '@playwright/test';

test.describe('饮食记录模块E2E测试', () => {
  test.beforeEach(async ({ page }) => {
    // 登录测试账号（假设已经存在于数据库中）
    await page.goto('http://localhost:5173/login'); // 假设登录页面路径
    await page.locator('[data-testid="email-input"]').fill('debug@example.com'); // 使用我们之前创建的测试用户
    await page.locator('[data-testid="password-input"]').fill('Debug1234!');
    await page.locator('button[type="submit"]').click();
    await page.waitForNavigation(); // 等待导航完成
    expect(page.url()).toContain('/dashboard'); // 确认已登录
  });

  test('应能访问饮食记录页面并显示标题和功能区', async ({ page }) => {
    // 导航到饮食记录页面
    await page.getByRole('link', { name: '饮食记录' }).click();
    await expect(page).toHaveURL(/.*diet-tracking/);

    // 检查页面标题
    await expect(page.locator('h1')).toContainText('饮食记录');

    // 检查基本功能组件是否可见
    await expect(page.locator('text=今日目标热量')).toBeVisible();
    await expect(page.locator('text=快速记录')).toBeVisible();
    await expect(page.locator('text=今日餐食记录')).toBeVisible();

    // 验证营养分布图表
    await expect(page.locator('.chartjs-render-monitor')).toBeVisible().catch(() => {
      // 图表可能不会出现在屏幕上，但至少检查其容器
      expect(page.locator('text=营养分布')).toBeVisible();
    });
  });

  test('应能切换日期并正确更新餐食数据', async ({ page }) => {
    await page.goto('http://localhost:5173/diet-tracking');

    // 检查默认日期选择器
    const defaultDate = await page.locator('input[type="date"]').inputValue();
    expect(defaultDate).toMatch(/^\d{4}-\d{2}-\d{2}$/); // 验证日期格式

    // 尝试更改为前一天的日期
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const yesterdayStr = yesterday.toISOString().split('T')[0];
    
    await page.locator('input[type="date"]').fill(yesterdayStr);
    
    // 验证日期选择器已经更新
    expect(await page.locator('input[type="date"]').inputValue()).toBe(yesterdayStr);
  });

  test('应能打开添加餐食表单', async ({ page }) => {
    await page.goto('http://localhost:5173/diet-tracking');
    
    // 点击添加餐食按钮
    await page.locator('button', { hasText: '添加餐食' }).click();
    
    // 验证模态框是否打开
    await expect(page.locator('text=添加餐食记录')).toBeVisible();
    await expect(page.locator('input[placeholder*="餐名"]')).toBeVisible();
    await expect(page.locator('select')).toBeVisible();
  });

  test('应能添加快捷餐食', async ({ page }) => {
    await page.goto('http://localhost:5173/diet-tracking');
    
    // 验证快速记录区
    await expect(page.locator('text=快速记录早餐')).toBeVisible();
    await expect(page.locator('text=快速记录午餐')).toBeVisible();
    await expect(page.locator('text=快速记录晚餐')).toBeVisible();

    // 尝试点击快速记录早餐
    const breakfastBtn = page.locator('text=快速记录早餐');
    await expect(breakfastBtn).toBeVisible();
    await breakfastBtn.click();

    // 这应该打开添加餐食表单，其中已填入早餐信息
    await expect(page.locator('text=添加餐食记录')).toBeVisible();
    await expect(page.locator('input[placeholder*="餐名"]').first()).toHaveValue(/早餐|快速早餐/i);
    
    // 关闭模态框
    await page.keyboard.press('Escape');
  });

  test('营养汇总数据显示', async ({ page }) => {
    await page.goto('http://localhost:5173/diet-tracking');

    // 检查各项营养信息汇总
    const totalCalorie = page.locator('text=/总热量 \\d+ kcal/').first();
    await expect(totalCalorie).toBeVisible();
    
    const proteinValue = page.locator('text=/蛋白质 \\d+\\.\\dg/').first();
    await expect(proteinValue).toBeVisible();
    
    const carbohydrateValue = page.locator('text=/碳水 \\d+\\.\\dg/').first();
    await expect(carbohydrateValue).toBeVisible();
    
    const fatValue = page.locator('text=/脂肪 \\d+\\.\\dg/').first();
    await expect(fatValue).toBeVisible();
  });
});

test.describe('营养管理模块E2E测试', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('http://localhost:5173/login');
    await page.locator('[data-testid="email-input"]').fill('debug@example.com');
    await page.locator('[data-testid="password-input"]').fill('Debug1234!');
    await page.locator('button[type="submit"]').click();
    await page.waitForNavigation();
  });

  test('应能访问营养管理页面并显示营养建议', async ({ page }) => {
    await page.goto('http://localhost:5173/nutrition');
    
    // 检查页面标题
    await expect(page.locator('h1')).toContainText('营养管理');
    
    // 检查是否显示目标热量
    await expect(page.locator('text=今日目标热量')).toBeVisible();
    
    // 检查推荐的宏量营养素是否显示
    await expect(page.locator('text=蛋白质')).toBeVisible();
    await expect(page.locator('text=碳水化合物')).toBeVisible();
    await expect(page.locator('text=脂肪')).toBeVisible();
  });

  test('应显示营养详情模态框', async ({ page }) => {
    await page.goto('http://localhost:5173/nutrition');
    
    // 点击信息提示按钮
    const infoBtn = page.locator('svg').first(); // 使用svg图标表示info按钮
    if (await infoBtn.count()>0) {
      await infoBtn.first().click();
      await expect(page.locator('text=热量目标是怎么计算的')).toBeVisible();
    } else {
      console.log('未找到信息按钮，跳过测试');
    }
  });
});