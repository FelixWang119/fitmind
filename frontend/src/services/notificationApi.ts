/**
 * 通知系统 API 服务
 */

import api from '../api/client';

export interface Notification {
  id: string;
  notification_type: string;
  title: string;
  content: string;
  channel: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
  template_code: string | null;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  page_size: number;
  unread_count: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface NotificationSettings {
  id: string;  // UUID from backend serialized as string
  user_id: number;
  enabled: boolean;
  do_not_disturb_enabled: boolean;
  do_not_disturb_start: string;
  do_not_disturb_end: string;
  notify_habit_reminder: boolean;
  notify_milestone: boolean;
  notify_care: boolean;
  notify_system: boolean;
  in_app_enabled: boolean;
  email_enabled: boolean;
  max_notifications_per_day: number;
  min_notification_interval: number;
  created_at: string;
  updated_at: string | null;
}

export interface UpdateNotificationSettingsPayload {
  enabled?: boolean;
  do_not_disturb_enabled?: boolean;
  do_not_disturb_start?: string;
  do_not_disturb_end?: string;
  notify_habit_reminder?: boolean;
  notify_milestone?: boolean;
  notify_care?: boolean;
  notify_system?: boolean;
  in_app_enabled?: boolean;
  email_enabled?: boolean;
  max_notifications_per_day?: number;
  min_notification_interval?: number;
}

const notificationApi = {
  /**
   * 获取通知列表
   */
  getNotifications: async (
    page: number = 1,
    page_size: number = 20,
    unread_only: boolean = false,
    search?: string,
    notification_type?: string
  ): Promise<NotificationListResponse> => {
    const params: Record<string, any> = { page, page_size, unread_only };
    if (search) {
      params.search = search;
    }
    if (notification_type) {
      params.notification_type = notification_type;
    }
    const response = await api.get('/notifications', {
      params,
    });
    return response.data;
  },

  /**
   * 获取未读数量
   */
  getUnreadCount: async (): Promise<UnreadCountResponse> => {
    const response = await api.get('/notifications/unread-count');
    return response.data;
  },

  /**
   * 标记通知为已读
   */
  markAsRead: async (notificationId: string): Promise<void> => {
    await api.put(`/notifications/${notificationId}/read`);
  },

  /**
   * 标记所有通知为已读
   */
  markAllAsRead: async (): Promise<void> => {
    await api.put('/notifications/read-all');
  },

  /**
   * 删除通知
   */
  deleteNotification: async (notificationId: string): Promise<void> => {
    await api.delete(`/notifications/${notificationId}`);
  },

  /**
   * 获取通知设置
   */
  getSettings: async (): Promise<NotificationSettings> => {
    const response = await api.get('/notifications/settings');
    return response.data;
  },

  /**
   * 更新通知设置
   */
  updateSettings: async (
    payload: UpdateNotificationSettingsPayload
  ): Promise<NotificationSettings> => {
    const response = await api.put('/notifications/settings', payload);
    return response.data;
  },
};

export default notificationApi;
