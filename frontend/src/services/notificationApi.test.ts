/**
 * 通知 API 服务测试
 */

import notificationApi from './notificationApi';

describe('Notification API Service', () => {
  describe('API Methods', () => {
    it('should have all required methods', () => {
      expect(notificationApi.getNotifications).toBeDefined();
      expect(notificationApi.getUnreadCount).toBeDefined();
      expect(notificationApi.markAsRead).toBeDefined();
      expect(notificationApi.markAllAsRead).toBeDefined();
      expect(notificationApi.deleteNotification).toBeDefined();
      expect(notificationApi.getSettings).toBeDefined();
      expect(notificationApi.updateSettings).toBeDefined();
    });

    it('should have correct method types', () => {
      expect(typeof notificationApi.getNotifications).toBe('function');
      expect(typeof notificationApi.getUnreadCount).toBe('function');
      expect(typeof notificationApi.markAsRead).toBe('function');
      expect(typeof notificationApi.markAllAsRead).toBe('function');
      expect(typeof notificationApi.deleteNotification).toBe('function');
      expect(typeof notificationApi.getSettings).toBe('function');
      expect(typeof notificationApi.updateSettings).toBe('function');
    });
  });

  describe('API Endpoints', () => {
    it('should use correct base path', () => {
      // 验证 API 路径包含 notifications
      expect(notificationApi.getNotifications.toString()).toContain('notifications');
    });
  });
});
