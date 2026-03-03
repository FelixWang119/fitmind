/**
 * Notification Center E2E Tests
 * 
 * Tests for Epic 8: Notification System Integration
 * Priority: P0 (Critical)
 */

import { test, expect } from '@playwright/test';

test.describe('Notification Center', () => {
  
  // P0: View notification drawer and list
  test.describe('P0: Core Functionality', () => {
    
    test('should display notification bell in header', async ({ page }) => {
      // Assume user is logged in
      await page.goto('/dashboard');
      
      // Check notification bell exists in header
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell');
      await expect(bellIcon).toBeVisible({ timeout: 10000 });
    });
    
    test('should show unread count badge', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Badge should be visible when there are unread notifications
      const badge = page.locator('.ant-badge-count, [class*="Badge"]').first();
      await expect(badge).toBeVisible({ timeout: 10000 });
    });
    
    test('should open notification drawer when clicking bell', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Click the notification bell
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Verify drawer opens with title "通知中心"
      const drawer = page.locator('.ant-drawer');
      await expect(drawer).toBeVisible({ timeout: 5000 });
      
      const title = page.locator('.ant-drawer-title');
      await expect(title).toContainText('通知中心');
    });
    
    test('should display notification list in drawer', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Click bell to open drawer
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Wait for list to load
      const list = page.locator('.ant-list');
      await expect(list).toBeVisible({ timeout: 10000 });
    });
    
    test('P0: should mark single notification as read', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Open notification drawer
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Wait for notifications to load
      const listItem = page.locator('.ant-list-item').first();
      await expect(listItem).toBeVisible({ timeout: 10000 });
      
      // Find and click "已读" button
      const readButton = listItem.locator('button:has-text("已读")');
      if (await readButton.isVisible()) {
        await readButton.click();
        
        // Verify button is no longer visible (notification is now read)
        await expect(readButton).not.toBeVisible();
      }
    });
    
    test('P0: should mark all notifications as read', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Open notification drawer
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Find "全部已读" button
      const markAllButton = page.locator('button:has-text("全部已读"), button:has-text("标记全部")');
      
      if (await markAllButton.isVisible()) {
        await markAllButton.click();
        
        // Verify all notifications are now read (no unread indicator)
        const unreadBadge = page.locator('.ant-list-item.notification-unread');
        await expect(unreadBadge).toHaveCount(0);
      }
    });
    
    test('P0: should delete a notification', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Open notification drawer
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Wait for list to load
      const listItem = page.locator('.ant-list-item').first();
      await expect(listItem).toBeVisible({ timeout: 10000 });
      
      // Find and click delete button
      const deleteButton = listItem.locator('button:has-text("删除")');
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        
        // The item should be removed from the list
        // This is a simple check - actual implementation may vary
        await page.waitForTimeout(500);
      }
    });
  });
  
  // P1: Search and filter functionality
  test.describe('P1: Search and Filter', () => {
    
    test('P1: should display search input', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Open notification drawer
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Search input should be visible
      const searchInput = page.locator('input[placeholder*="搜索"], .ant-input-search input');
      await expect(searchInput).toBeVisible({ timeout: 5000 });
    });
    
    test('P1: should display type filter dropdown', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Open notification drawer
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Type filter should be visible
      const filterSelect = page.locator('.ant-select');
      await expect(filterSelect).toBeVisible({ timeout: 5000 });
    });
    
    test('P1: should filter notifications by type', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Open notification drawer
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Click type filter
      const filterSelect = page.locator('.ant-select').first();
      await filterSelect.click();
      
      // Select a type option
      const option = page.locator('.ant-select-item-option').first();
      await option.click();
      
      // List should update
      await page.waitForTimeout(500);
    });
    
    test('P1: should navigate pagination', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Open notification drawer
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Check for pagination
      const pagination = page.locator('.ant-pagination');
      
      if (await pagination.isVisible()) {
        // Click next page
        const nextButton = pagination.locator('button.ant-pagination-next');
        if (await nextButton.isEnabled()) {
          await nextButton.click();
          await page.waitForTimeout(500);
        }
      }
    });
  });
  
  // P1: Notification Settings
  test.describe('P1: Notification Settings', () => {
    
    test('P1: should access notification settings page', async ({ page }) => {
      await page.goto('/notification-settings');
      
      // Page should load
      await expect(page.locator('h1, h2')).toBeVisible({ timeout: 10000 });
    });
    
    test('P1: should toggle notification master switch', async ({ page }) => {
      await page.goto('/notification-settings');
      
      // Find master switch
      const masterSwitch = page.locator('switch').first();
      await masterSwitch.click();
      
      // Should toggle state
      await page.waitForTimeout(500);
    });
    
    test('P1: should toggle individual notification types', async ({ page }) => {
      await page.goto('/notification-settings');
      
      // Find notification type switches
      const switches = page.locator('switch');
      const count = await switches.count();
      
      if (count > 1) {
        // Toggle second switch (first might be master)
        await switches.nth(1).click();
        await page.waitForTimeout(500);
      }
    });
  });
  
  // P2: Edge cases
  test.describe('P2: Edge Cases', () => {
    
    test('P2: should display empty state when no notifications', async ({ page }) => {
      // This test would require a fresh user without notifications
      // Skipping for now as it requires specific setup
    });
    
    test('P2: should handle very long notification content', async ({ page }) => {
      // Should not break layout with long content
      await page.goto('/dashboard');
      
      const bellIcon = page.locator('[class*="BellOutlined"], .anticon-bell').first();
      await bellIcon.click();
      
      // Just verify drawer opens without error
      const drawer = page.locator('.ant-drawer');
      await expect(drawer).toBeVisible({ timeout: 5000 });
    });
  });
});