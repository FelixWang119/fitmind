/**
 * 通知中心组件测试
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import NotificationCenter from './index';
import notificationApi from '../../services/notificationApi';

// Mock notificationApi
jest.mock('../../services/notificationApi', () => ({
  __esModule: true,
  default: {
    getNotifications: jest.fn(),
    getUnreadCount: jest.fn(),
    markAsRead: jest.fn(),
    markAllAsRead: jest.fn(),
    deleteNotification: jest.fn(),
    getSettings: jest.fn(),
    updateSettings: jest.fn(),
  },
}));

// Mock Ant Design components
jest.mock('antd', () => ({
  Badge: ({ count, children, offset, size }: any) => (
    <div data-testid="badge" data-count={count}>{children}</div>
  ),
  Drawer: ({ visible, children, title, onClose, placement, width, extra }: any) => 
    visible ? <div data-testid="drawer">{title}{extra}{children}</div> : null,
  Button: ({ children, onClick, type, size, icon, block, danger }: any) => (
    <button onClick={onClick} data-type={type}>{children}</button>
  ),
  List: ({ dataSource, renderItem, actions }: any) => (
    <div data-testid="list">
      {dataSource?.map((item: any, index: number) => (
        <div key={index} data-testid="list-item">
          {renderItem(item)}
        </div>
      ))}
    </div>
  ),
  Typography: { Text: ({ children }: any) => <span>{children}</span> },
  Empty: ({ description }: any) => (
    <div data-testid="empty">{description}</div>
  ),
  message: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
    warning: jest.fn(),
  },
  Spin: ({ spinning, children }: any) => (
    <div data-testid="spin" data-spinning={spinning}>{children}</div>
  ),
  Dropdown: ({ overlay, children, trigger }: any) => (
    <div data-testid="dropdown">{children}{overlay}</div>
  ),
  Menu: ({ children }: any) => <div data-testid="menu">{children}</div>,
  Menu_Item: ({ children, onClick, icon, disabled }: any) => (
    <button onClick={onClick} data-testid="menu-item" disabled={disabled}>{icon}{children}</button>
  ),
}));

describe('NotificationCenter', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<NotificationCenter />);
    
    expect(screen.getByTestId('badge')).toBeInTheDocument();
  });

  it('shows unread count badge', async () => {
    (notificationApi.getUnreadCount as jest.Mock).mockResolvedValue({ unread_count: 5 });
    
    render(<NotificationCenter />);
    
    await waitFor(() => {
      const badge = screen.getByTestId('badge');
      expect(badge.getAttribute('data-count')).toBe('5');
    });
  });

  it('opens drawer when clicking bell icon', async () => {
    (notificationApi.getUnreadCount as jest.Mock).mockResolvedValue({ unread_count: 0 });
    (notificationApi.getNotifications as jest.Mock).mockResolvedValue({
      items: [],
      total: 0,
      unread_count: 0,
    });
    
    render(<NotificationCenter />);
    
    const bellIcon = screen.getByTestId('badge');
    fireEvent.click(bellIcon);
    
    await waitFor(() => {
      expect(screen.getByTestId('drawer')).toBeInTheDocument();
    });
  });

  it('loads notifications when drawer opens', async () => {
    const mockNotifications = [
      {
        id: '1',
        title: '测试通知 1',
        content: '内容 1',
        is_read: false,
        created_at: '2026-02-25T10:00:00Z',
      },
      {
        id: '2',
        title: '测试通知 2',
        content: '内容 2',
        is_read: true,
        created_at: '2026-02-25T09:00:00Z',
      },
    ];
    
    (notificationApi.getUnreadCount as jest.Mock).mockResolvedValue({ unread_count: 1 });
    (notificationApi.getNotifications as jest.Mock).mockResolvedValue({
      items: mockNotifications,
      total: 2,
      unread_count: 1,
    });
    
    render(<NotificationCenter />);
    
    const bellIcon = screen.getByTestId('badge');
    fireEvent.click(bellIcon);
    
    await waitFor(() => {
      expect(notificationApi.getNotifications).toHaveBeenCalledWith(1, 20, false);
      expect(screen.getByTestId('list')).toBeInTheDocument();
    });
  });

  it('marks notification as read when clicking read button', async () => {
    const mockNotifications = [
      {
        id: '1',
        title: '未读通知',
        content: '内容',
        is_read: false,
        created_at: '2026-02-25T10:00:00Z',
      },
    ];
    
    (notificationApi.getUnreadCount as jest.Mock).mockResolvedValue({ unread_count: 1 });
    (notificationApi.getNotifications as jest.Mock).mockResolvedValue({
      items: mockNotifications,
      total: 1,
      unread_count: 1,
    });
    (notificationApi.markAsRead as jest.Mock).mockResolvedValue(undefined);
    
    render(<NotificationCenter />);
    
    const bellIcon = screen.getByTestId('badge');
    fireEvent.click(bellIcon);
    
    await waitFor(() => {
      const readButton = screen.getByText('已读');
      fireEvent.click(readButton);
    });
    
    await waitFor(() => {
      expect(notificationApi.markAsRead).toHaveBeenCalledWith('1');
    });
  });

  it('marks all as read when clicking mark all button', async () => {
    const mockNotifications = [
      {
        id: '1',
        title: '通知 1',
        content: '内容 1',
        is_read: false,
        created_at: '2026-02-25T10:00:00Z',
      },
    ];
    
    (notificationApi.getUnreadCount as jest.Mock).mockResolvedValue({ unread_count: 1 });
    (notificationApi.getNotifications as jest.Mock).mockResolvedValue({
      items: mockNotifications,
      total: 1,
      unread_count: 1,
    });
    (notificationApi.markAllAsRead as jest.Mock).mockResolvedValue(undefined);
    
    render(<NotificationCenter />);
    
    const bellIcon = screen.getByTestId('badge');
    fireEvent.click(bellIcon);
    
    await waitFor(() => {
      const markAllButton = screen.getByText('全部已读');
      fireEvent.click(markAllButton);
    });
    
    await waitFor(() => {
      expect(notificationApi.markAllAsRead).toHaveBeenCalled();
    });
  });

  it('shows empty state when no notifications', async () => {
    (notificationApi.getUnreadCount as jest.Mock).mockResolvedValue({ unread_count: 0 });
    (notificationApi.getNotifications as jest.Mock).mockResolvedValue({
      items: [],
      total: 0,
      unread_count: 0,
    });
    
    render(<NotificationCenter />);
    
    const bellIcon = screen.getByTestId('badge');
    fireEvent.click(bellIcon);
    
    await waitFor(() => {
      expect(screen.getByTestId('empty')).toBeInTheDocument();
    });
  });

  it('polls unread count every 60 seconds', async () => {
    jest.useFakeTimers();
    
    (notificationApi.getUnreadCount as jest.Mock).mockResolvedValue({ unread_count: 0 });
    
    render(<NotificationCenter />);
    
    // 初始调用
    expect(notificationApi.getUnreadCount).toHaveBeenCalledTimes(1);
    
    // 快进 60 秒
    jest.advanceTimersByTime(60000);
    
    await waitFor(() => {
      expect(notificationApi.getUnreadCount).toHaveBeenCalledTimes(2);
    });
    
    // 再快进 60 秒
    jest.advanceTimersByTime(60000);
    
    await waitFor(() => {
      expect(notificationApi.getUnreadCount).toHaveBeenCalledTimes(3);
    });
    
    jest.useRealTimers();
  });
});
