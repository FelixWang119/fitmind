/**
 * 通知中心组件
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Badge,
  Button,
  Drawer,
  List,
  Typography,
  Empty,
  message,
  Spin,
  Dropdown,
  Menu,
} from 'antd';
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  ReadingOutlined,
} from '@ant-design/icons';
import notificationApi, { Notification } from '../../services/notificationApi';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

interface NotificationCenterProps {
  onNotificationClick?: (notification: Notification) => void;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  onNotificationClick,
}) => {
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);

  // 获取未读数量
  const fetchUnreadCount = useCallback(async () => {
    try {
      const data = await notificationApi.getUnreadCount();
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }, []);

  // 获取通知列表
  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const data = await notificationApi.getNotifications(1, 20, false);
      setNotifications(data.items);
      setTotalCount(data.total);
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      message.error('加载通知失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // 轮询未读数量（60 秒）
  useEffect(() => {
    // 立即获取一次
    fetchUnreadCount();

    // 设置轮询
    const pollInterval = setInterval(() => {
      fetchUnreadCount();
    }, 60000); // 60 秒

    return () => clearInterval(pollInterval);
  }, [fetchUnreadCount]);

  // 打开抽屉时加载通知
  useEffect(() => {
    if (visible) {
      fetchNotifications();
    }
  }, [visible, fetchNotifications]);

  // 标记为已读
  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await notificationApi.markAsRead(notificationId);
      
      // 更新本地状态
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, is_read: true } : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
      
      message.success('已标记为已读');
    } catch (error) {
      console.error('Failed to mark as read:', error);
      message.error('操作失败');
    }
  };

  // 全部标记为已读
  const handleMarkAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead();
      
      // 更新本地状态
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
      
      message.success('全部标记为已读');
    } catch (error) {
      console.error('Failed to mark all as read:', error);
      message.error('操作失败');
    }
  };

  // 删除通知
  const handleDelete = async (notificationId: string) => {
    try {
      await notificationApi.deleteNotification(notificationId);
      
      // 更新本地状态
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      
      message.success('已删除');
    } catch (error) {
      console.error('Failed to delete:', error);
      message.error('删除失败');
    }
  };

  // 下拉菜单
  const menu = (
    <Menu>
      <Menu.Item
        key="mark-all-read"
        icon={<CheckOutlined />}
        onClick={handleMarkAllAsRead}
        disabled={unreadCount === 0}
      >
        全部标记已读
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      {/* 通知图标 */}
      <Badge count={unreadCount} offset={[-5, 5]} size="small">
        <Dropdown overlay={menu} trigger={['click']} visible={visible}>
          <BellOutlined
            onClick={() => setVisible(true)}
            style={{
              fontSize: 20,
              cursor: 'pointer',
              color: unreadCount > 0 ? '#1890ff' : 'inherit',
            }}
          />
        </Dropdown>
      </Badge>

      {/* 通知抽屉 */}
      <Drawer
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>
              <ReadingOutlined style={{ marginRight: 8 }} />
              通知中心
            </span>
            {unreadCount > 0 && (
              <span style={{ fontSize: 12, color: '#999' }}>
                {unreadCount} 条未读
              </span>
            )}
          </div>
        }
        placement="right"
        visible={visible}
        onClose={() => setVisible(false)}
        width={400}
        extra={
          unreadCount > 0 && (
            <Button
              type="link"
              size="small"
              onClick={handleMarkAllAsRead}
              icon={<CheckOutlined />}
            >
              全部已读
            </Button>
          )
        }
      >
        <Spin spinning={loading}>
          {notifications.length > 0 ? (
            <List
              dataSource={notifications}
              renderItem={(notification) => (
                <List.Item
                  className={`notification-item ${
                    !notification.is_read ? 'notification-unread' : ''
                  }`}
                  onClick={() => onNotificationClick?.(notification)}
                  actions={[
                    !notification.is_read && (
                      <Button
                        type="text"
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMarkAsRead(notification.id);
                        }}
                        icon={<CheckOutlined />}
                      >
                        已读
                      </Button>
                    ),
                    <Button
                      type="text"
                      size="small"
                      danger
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(notification.id);
                      }}
                      icon={<DeleteOutlined />}
                    >
                      删除
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{notification.title}</span>
                        {!notification.is_read && (
                          <Badge dot color="red" />
                        )}
                      </div>
                    }
                    description={
                      <div>
                        <div style={{ marginBottom: 4 }}>
                          {notification.content}
                        </div>
                        <div style={{ fontSize: 12, color: '#999' }}>
                          {dayjs(notification.created_at).fromNow()}
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          ) : (
            <Empty description="暂无通知" />
          )}
        </Spin>
      </Drawer>
    </>
  );
};

export default NotificationCenter;
