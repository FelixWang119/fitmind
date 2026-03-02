/**
 * 通知中心组件 - Story 8.5
 * 支持搜索、类型筛选、浏览器桌面通知和优化空状态
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Badge,
  Button,
  Drawer,
  List,
  Empty,
  message,
  Spin,
  Dropdown,
  Menu,
  Pagination,
  Input,
  Select,
} from 'antd';
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  ReadOutlined,
  SearchOutlined,
  InboxOutlined,
} from '@ant-design/icons';
import notificationApi, { Notification } from '../../services/notificationApi';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

// 只在非测试环境中初始化 dayjs 插件
if (typeof window !== 'undefined' && process.env.NODE_ENV !== 'test') {
  dayjs.extend(relativeTime);
  dayjs.locale('zh-cn');
}

interface NotificationCenterProps {
  onNotificationClick?: (notification: Notification) => void;
}

// 通知类型选项
const NOTIFICATION_TYPES = [
  { value: '', label: '全部类型' },
  { value: 'habit_reminder', label: '习惯提醒' },
  { value: 'milestone', label: '里程碑' },
  { value: 'care', label: '关怀通知' },
  { value: 'system', label: '系统通知' },
];

// 浏览器通知辅助类
class BrowserNotificationHelper {
  private static permission: NotificationPermission = 'default';

  static async requestPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      console.log('此浏览器不支持桌面通知');
      return 'denied';
    }

    try {
      this.permission = Notification.permission;
      
      if (this.permission === 'granted') {
        return 'granted';
      }
      
      if (this.permission !== 'denied') {
        this.permission = await Notification.requestPermission();
      }
      
      return this.permission;
    } catch (error) {
      console.error('请求通知权限失败:', error);
      return 'denied';
    }
  }

  static async showNotification(title: string, options?: NotificationOptions): Promise<Notification | null> {
    if (!('Notification' in window)) {
      return null;
    }

    const permission = await this.requestPermission();
    
    if (permission !== 'granted') {
      console.log('通知权限未授权');
      return null;
    }

    try {
      const notification = new Notification(title, {
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        ...options,
      });

      // 3 秒后自动关闭
      setTimeout(() => {
        notification.close();
      }, 5000);

      return notification;
    } catch (error) {
      console.error('显示通知失败:', error);
      return null;
    }
  }

  static get isSupported(): boolean {
    return 'Notification' in window;
  }

  static get currentPermission(): NotificationPermission {
    if (!('Notification' in window)) {
      return 'denied';
    }
    return Notification.permission;
  }
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  onNotificationClick,
}) => {
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [notificationType, setNotificationType] = useState<string>('');
  const [searchInput, setSearchInput] = useState('');
  const pageSize = 20;
  
  // 用于检测新通知的 ref
  const prevUnreadCountRef = useRef(0);
  // 用于追踪已显示桌面通知的通知 ID，避免重复显示
  const notifiedIdsRef = useRef<Set<string>>(new Set());

  // 获取未读数量
  const fetchUnreadCount = useCallback(async () => {
    try {
      const data = await notificationApi.getUnreadCount();
      const newUnreadCount = data.unread_count;
      
      // 检测新通知并发送浏览器通知
      if (prevUnreadCountRef.current > 0 && newUnreadCount > prevUnreadCountRef.current) {
        // 有新通知 - 获取最新通知并发送桌面通知
        try {
          const notificationsData = await notificationApi.getNotifications(1, 1, true);
          if (notificationsData.items.length > 0) {
            const latestNotification = notificationsData.items[0];
            // 检查是否已显示过此通知，避免重复显示
            if (!notifiedIdsRef.current.has(latestNotification.id)) {
              await BrowserNotificationHelper.showNotification(
                latestNotification.title,
                {
                  body: latestNotification.content,
                  tag: latestNotification.id,
                }
              );
              // 记录已显示的通知 ID
              notifiedIdsRef.current.add(latestNotification.id);
            }
          }
        } catch (e) {
          console.error('获取最新通知失败:', e);
        }
      }
      
      setUnreadCount(newUnreadCount);
      prevUnreadCountRef.current = newUnreadCount;
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }, []);

  // 获取通知列表（支持搜索和筛选）
  // 注意：不依赖 searchKeyword/notificationType 状态，避免 handleSearch/handleTypeChange 中调用时重复触发
  const fetchNotifications = useCallback(async (
    page: number = 1,
    keyword?: string,
    type?: string
  ) => {
    setLoading(true);
    try {
      const data = await notificationApi.getNotifications(
        page, 
        pageSize, 
        false,
        keyword || searchKeyword || undefined,
        type || notificationType || undefined
      );
      setNotifications(data.items);
      setTotalCount(data.total);
      setUnreadCount(data.unread_count);
      setCurrentPage(data.page);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      message.error('加载通知失败');
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  // 请求浏览器通知权限
  useEffect(() => {
    if (BrowserNotificationHelper.isSupported) {
      BrowserNotificationHelper.requestPermission();
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

  // 搜索处理
  const handleSearch = useCallback(() => {
    const keyword = searchInput;
    setSearchKeyword(keyword);
    setCurrentPage(1);
    // 直接传递 keyword 参数，避免依赖状态更新后的闭包值
    fetchNotifications(1, keyword);
  }, [searchInput, fetchNotifications]);

  // 类型筛选处理
  const handleTypeChange = useCallback((value: string) => {
    setNotificationType(value);
    setCurrentPage(1);
    // 直接传递 value 参数，避免依赖状态更新后的闭包值
    fetchNotifications(1, undefined, value);
  }, [fetchNotifications]);

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
      setTotalCount(prev => Math.max(0, prev - 1));
      
      message.success('已删除');
    } catch (error) {
      console.error('Failed to delete:', error);
      message.error('删除失败');
    }
  };

  // 分页变化
  const handlePageChange = (page: number) => {
    fetchNotifications(page);
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
              <ReadOutlined style={{ marginRight: 8 }} />
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
        {/* 搜索和筛选区域 - Story 8.5 */}
        <div style={{ marginBottom: 16 }}>
          {/* 搜索框 */}
          <Input.Search
            data-testid="search-input"
            placeholder="搜索通知..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onSearch={handleSearch}
            style={{ marginBottom: 12 }}
            allowClear
            enterButton={<SearchOutlined />}
          />
          
          {/* 类型筛选 */}
          <Select
            data-testid="type-filter"
            value={notificationType}
            onChange={handleTypeChange}
            style={{ width: '100%' }}
            options={NOTIFICATION_TYPES}
            placeholder="按类型筛选"
          />
        </div>

        <Spin spinning={loading}>
          {notifications.length > 0 ? (
            <>
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
              {totalCount > pageSize && (
                <div style={{ textAlign: 'center', marginTop: 16 }}>
                  <Pagination
                    current={currentPage}
                    total={totalCount}
                    pageSize={pageSize}
                    onChange={handlePageChange}
                    size="small"
                    showSizeChanger={false}
                  />
                </div>
              )}
            </>
          ) : (
            /* 优化空状态 - Story 8.5 */
            <Empty
              data-testid="empty"
              image={<InboxOutlined style={{ fontSize: 64, color: '#ccc' }} />}
              description={
                <div style={{ textAlign: 'center' }}>
                  <p style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>
                    {searchKeyword || notificationType ? '没有找到匹配的通知' : '暂无通知'}
                  </p>
                  <p style={{ fontSize: 12, color: '#999' }}>
                    {searchKeyword || notificationType 
                      ? '试试调整搜索条件或清除筛选' 
                      : '有新通知时会在这里显示'}
                  </p>
                </div>
              }
            />
          )}
        </Spin>
      </Drawer>
    </>
  );
};

export default NotificationCenter;