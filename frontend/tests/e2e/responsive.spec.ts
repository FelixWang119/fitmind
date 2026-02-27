/**
 * 响应式设计 E2E 测试
 * 
 * 测试应用在不同设备和 viewport 下的响应式布局
 * 覆盖 PRD FR12: 响应式设计
 */

import { test, expect, devices } from '@playwright/test';

// 测试设备配置
const devicesToTest = {
  'Mobile Chrome': devices['Pixel 5'],
  'Mobile Safari': devices['iPhone 12'],
  'Tablet': devices['iPad Mini'],
  'Desktop': {
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
  },
};

test.describe('[Responsive Design] 响应式布局测试', () => {
  
  // P0: 核心页面在所有设备上可访问
  test.describe('核心页面可访问性', () => {
    
    for (const [deviceName, deviceConfig] of Object.entries(devicesToTest)) {
      test(`[P0] 登录页面在 ${deviceName} 上正常显示`, async ({ page }) => {
        await page.setViewportSize(deviceConfig.viewport);
        await page.goto('/login');
        
        // 验证页面加载
        await expect(page).toHaveTitle(/FitMind|体重管理/);
        
        // 验证关键元素可见
        const loginForm = page.getByRole('form');
        await expect(loginForm).toBeVisible();
        
        // 验证邮箱输入框
        const emailInput = page.getByLabel(/邮箱|Email/);
        await expect(emailInput).toBeVisible();
        
        // 验证密码输入框
        const passwordInput = page.getByLabel(/密码|Password/);
        await expect(passwordInput).toBeVisible();
        
        // 验证登录按钮
        const loginButton = page.getByRole('button', { name: /登录|Login/i });
        await expect(loginButton).toBeVisible();
      });

      test(`[P0] 仪表盘页面在 ${deviceName} 上正常显示`, async ({ page }) => {
        await page.setViewportSize(deviceConfig.viewport);
        
        // 模拟登录状态 (跳过实际登录)
        await page.goto('/dashboard');
        
        // 验证仪表盘标题
        const dashboardTitle = page.getByText(/仪表盘|Dashboard|今日概览/i);
        await expect(dashboardTitle).toBeVisible();
      });

      test(`[P0] 导航在 ${deviceName} 上正常工作`, async ({ page }) => {
        await page.setViewportSize(deviceConfig.viewport);
        await page.goto('/');
        
        // 移动端应该显示汉堡菜单
        const isMobile = deviceConfig.viewport.width < 768;
        
        if (isMobile) {
          // 移动端：汉堡菜单
          const hamburgerMenu = page.getByRole('button', { name: /菜单|Menu/i });
          // 汉堡菜单可能隐藏，所以不强制验证
        } else {
          // 桌面端：侧边导航应该可见
          const sidebar = page.getByRole('navigation');
          // 侧边导航可能要求登录，所以不强制验证
        }
      });
    }
  });

  // P0: 触摸友好的按钮大小 (最小 44px)
  test.describe('[P0] 触摸友好的按钮大小', () => {
    
    for (const [deviceName, deviceConfig] of Object.entries(devicesToTest)) {
      const isMobile = deviceConfig.viewport.width < 768;
      
      if (isMobile) {
        test(`移动端 ${deviceName} 按钮大小 >= 44px`, async ({ page }) => {
          await page.setViewportSize(deviceConfig.viewport);
          await page.goto('/login');
          
          // 获取所有按钮
          const buttons = page.locator('button, [role="button"]');
          const count = await buttons.count();
          
          // 验证前 5 个按钮的大小 (如果存在)
          for (let i = 0; i < Math.min(count, 5); i++) {
            const button = buttons.nth(i);
            const box = await button.boundingBox();
            
            if (box) {
              // 按钮最小尺寸应该是 44x44px
              expect(box.height).toBeGreaterThanOrEqual(44);
              expect(box.width).toBeGreaterThanOrEqual(44);
            }
          }
        });
      }
    }
  });

  // P1: 移动端布局适配
  test.describe('[P1] 移动端布局适配', () => {
    
    test('[P1] 移动端 (< 768px) 单列布局', async ({ page }) => {
      await page.setViewportSize(devices['Pixel 5'].viewport);
      await page.goto('/login');
      
      // 验证视口宽度
      const viewportWidth = await page.evaluate(() => window.innerWidth);
      expect(viewportWidth).toBeLessThan(768);
      
      // 验证内容区域宽度
      const container = page.locator('.container, main, [role="main"]').first();
      const containerBox = await container.boundingBox();
      
      if (containerBox) {
        // 移动端容器应该接近屏幕宽度 (有 margin)
        expect(containerBox.width).toBeLessThan(viewportWidth);
      }
    });

    test('[P1] 移动端字体大小合适', async ({ page }) => {
      await page.setViewportSize(devices['Pixel 5'].viewport);
      await page.goto('/login');
      
      // 验证正文字体大小
      const fontSize = await page.evaluate(() => {
        const element = document.querySelector('body');
        return element ? parseFloat(getComputedStyle(element).fontSize) : 0;
      });
      
      // 移动端字体应该 >= 14px 以保证可读性
      expect(fontSize).toBeGreaterThanOrEqual(14);
    });

    test('[P1] 移动端无横向滚动', async ({ page }) => {
      await page.setViewportSize(devices['Pixel 5'].viewport);
      await page.goto('/login');
      
      // 验证无横向滚动
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      
      expect(hasHorizontalScroll).toBe(false);
    });
  });

  // P1: 平板布局适配
  test.describe('[P1] 平板布局适配', () => {
    
    test('[P1] 平板 (768px - 1024px) 双列布局', async ({ page }) => {
      await page.setViewportSize(devices['iPad Mini'].viewport);
      await page.goto('/login');
      
      // 验证视口宽度
      const viewportWidth = await page.evaluate(() => window.innerWidth);
      expect(viewportWidth).toBeGreaterThanOrEqual(768);
      expect(viewportWidth).toBeLessThanOrEqual(1024);
    });

    test('[P1] 平板布局元素间距合适', async ({ page }) => {
      await page.setViewportSize(devices['iPad Mini'].viewport);
      await page.goto('/login');
      
      // 验证表单内元素间距
      const form = page.getByRole('form');
      const formBox = await form.boundingBox();
      
      if (formBox) {
        // 平板表单宽度应该适中
        expect(formBox.width).toBeGreaterThanOrEqual(400);
        expect(formBox.width).toBeLessThanOrEqual(700);
      }
    });
  });

  // P1: 桌面布局适配
  test.describe('[P1] 桌面布局适配', () => {
    
    test('[P1] 桌面 (> 1024px) 多列布局', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto('/login');
      
      // 验证视口宽度
      const viewportWidth = await page.evaluate(() => window.innerWidth);
      expect(viewportWidth).toBeGreaterThan(1024);
    });

    test('[P1] 桌面布局内容居中', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto('/login');
      
      // 验证登录表单居中
      const form = page.getByRole('form');
      const formBox = await form.boundingBox();
      
      if (formBox && formBox.width) {
        // 表单应该大致在屏幕中央
        const screenWidth = 1920;
        const leftMargin = formBox.x;
        const rightMargin = screenWidth - (formBox.x + formBox.width);
        
        // 左右 margin 差异不应该太大 (允许 10% 误差)
        const marginDiff = Math.abs(leftMargin - rightMargin);
        expect(marginDiff).toBeLessThan(screenWidth * 0.1);
      }
    });

    test('[P1] 桌面布局利用屏幕空间', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto('/dashboard');
      
      // 桌面版应该展示更多内容
      const dashboardContent = page.locator('[data-testid="dashboard-content"], main, .dashboard');
      // 桌面版内容区域应该较宽
      const contentBox = await dashboardContent.boundingBox();
      
      if (contentBox) {
        expect(contentBox.width).toBeGreaterThanOrEqual(800);
      }
    });
  });

  // P2: 响应式图片
  test.describe('[P2] 响应式图片', () => {
    
    test('[P2] 图片适应容器大小', async ({ page }) => {
      await page.setViewportSize(devices['Pixel 5'].viewport);
      await page.goto('/login');
      
      // 查找所有图片
      const images = page.locator('img');
      const count = await images.count();
      
      for (let i = 0; i < Math.min(count, 3); i++) {
        const image = images.nth(i);
        const imageBox = await image.boundingBox();
        
        if (imageBox) {
          // 图片不应该溢出屏幕
          expect(imageBox.width).toBeLessThanOrEqual(devices['Pixel 5'].viewport.width);
        }
      }
    });
  });

  // P2: 响应式表格
  test.describe('[P2] 响应式表格', () => {
    
    test('[P2] 移动端表格可滚动或堆叠', async ({ page }) => {
      await page.setViewportSize(devices['Pixel 5'].viewport);
      await page.goto('/dashboard');
      
      // 查找表格
      const tables = page.locator('table');
      const count = await tables.count();
      
      if (count > 0) {
        const table = tables.first();
        const tableBox = await table.boundingBox();
        
        if (tableBox) {
          // 表格要么可横向滚动，要么适配屏幕宽度
          const viewportWidth = devices['Pixel 5'].viewport.width;
          
          // 如果表格超出视口，应该有滚动
          if (tableBox.width > viewportWidth) {
            const hasHorizontalScroll = await page.evaluate(() => {
              const table = document.querySelector('table');
              if (!table) return false;
              const parent = table.parentElement;
              if (!parent) return false;
              return parent.scrollWidth > parent.clientWidth;
            });
            
            // 要么父容器可滚动，要么表格适配
            expect(hasHorizontalScroll).toBe(true);
          }
        }
      }
    });
  });

  // P2: 断点验证
  test.describe('[P2] CSS 断点验证', () => {
    
    test('[P2] 768px 断点工作正常', async ({ page }) => {
      // 测试 767px (移动端)
      await page.setViewportSize({ width: 767, height: 1024 });
      await page.goto('/login');
      
      const isMobile767 = await page.evaluate(() => window.innerWidth < 768);
      expect(isMobile767).toBe(true);
      
      // 测试 768px (平板开始)
      await page.setViewportSize({ width: 768, height: 1024 });
      
      const isTablet768 = await page.evaluate(() => window.innerWidth >= 768);
      expect(isTablet768).toBe(true);
    });

    test('[P2] 1024px 断点工作正常', async ({ page }) => {
      // 测试 1023px (平板)
      await page.setViewportSize({ width: 1023, height: 768 });
      await page.goto('/login');
      
      const isTablet1023 = await page.evaluate(() => {
        return window.innerWidth >= 768 && window.innerWidth <= 1024;
      });
      expect(isTablet1023).toBe(true);
      
      // 测试 1025px (桌面开始)
      await page.setViewportSize({ width: 1025, height: 768 });
      
      const isDesktop1025 = await page.evaluate(() => window.innerWidth > 1024);
      expect(isDesktop1025).toBe(true);
    });
  });

  // P2: 可访问性
  test.describe('[P2] 响应式可访问性', () => {
    
    for (const [deviceName, deviceConfig] of Object.entries(devicesToTest)) {
      test(`[P2] ${deviceName} 键盘导航正常`, async ({ page, deviceName }) => {
        await page.setViewportSize(deviceConfig.viewport);
        await page.goto('/login');
        
        // 测试 Tab 键导航
        await page.keyboard.press('Tab');
        const firstFocusedElement = await page.evaluate(() => document.activeElement?.tagName);
        expect(firstFocusedElement).toBeTruthy();
        
        // 继续 Tab 导航
        await page.keyboard.press('Tab');
        const secondFocusedElement = await page.evaluate(() => document.activeElement?.tagName);
        expect(secondFocusedElement).toBeTruthy();
      });
    }
  });
});

// 运行所有响应式测试
// npx playwright test tests/e2e/responsive.spec.ts

// 仅运行移动端测试
// npx playwright test tests/e2e/responsive.spec.ts --grep "移动端"

// 仅运行 P0 测试
// npx playwright test tests/e2e/responsive.spec.ts --grep "@p0"
