/**
 * 通知 Toast 组件
 * 用于显示 SSE 实时推送的通知
 */

'use client';

import { useEffect, useState } from 'react';
import { useSSEEvents, SSEEvent } from '@/hooks/useSSE';
import { X, Bell, TrendingUp, Radio, AlertCircle, CheckCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { cn } from '@/lib/utils';

interface ToastNotification {
  id: string;
  type: 'new_article' | 'trending' | 'monitor' | 'system' | 'success' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  link?: string;
  read: boolean;
}

interface ToastProps {
  notification: ToastNotification;
  onClose: () => void;
  onClick?: () => void;
}

function Toast({ notification, onClose, onClick }: ToastProps) {
  const icons = {
    new_article: Bell,
    trending: TrendingUp,
    monitor: Radio,
    system: AlertCircle,
    success: CheckCircle,
    error: AlertCircle,
  };
  
  const colors = {
    new_article: 'bg-blue-500',
    trending: 'bg-orange-500',
    monitor: 'bg-purple-500',
    system: 'bg-gray-500',
    success: 'bg-green-500',
    error: 'bg-red-500',
  };

  const Icon = icons[notification.type];
  const color = colors[notification.type];

  return (
    <div
      className={cn(
        'relative flex items-start gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700',
        'animate-in slide-in-from-right-full duration-300',
        !notification.read && 'border-l-4 border-l-blue-500'
      )}
    >
      <div className={cn('p-2 rounded-full text-white', color)}>
        <Icon className="w-4 h-4" />
      </div>
      
      <div className="flex-1 min-w-0" onClick={onClick}>
        <p className="font-medium text-sm text-gray-900 dark:text-gray-100">
          {notification.title}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">
          {notification.message}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          {formatDistanceToNow(notification.timestamp, { addSuffix: true, locale: zhCN })}
        </p>
      </div>
      
      <button
        onClick={(e) => {
          e.stopPropagation();
          onClose();
        }}
        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
      >
        <X className="w-4 h-4 text-gray-400" />
      </button>
    </div>
  );
}

interface NotificationToastContainerProps {
  maxVisible?: number;
  className?: string;
}

export function NotificationToastContainer({ 
  maxVisible = 5,
  className 
}: NotificationToastContainerProps) {
  const [notifications, setNotifications] = useState<ToastNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  
  const { lastEvent, isConnected } = useSSEEvents();

  // 处理收到的 SSE 事件
  useEffect(() => {
    if (!lastEvent) return;

    const newNotification = createNotificationFromEvent(lastEvent);
    if (newNotification) {
      setNotifications(prev => {
        // 使用随机 ID 避免 hydration mismatch
        const updated = [{ ...newNotification, id: `${newNotification.id}-${Math.random().toString(36).slice(2, 8)}` }, ...prev].slice(0, 20);
        return updated;
      });
      setUnreadCount(prev => prev + 1);
    }
  }, [lastEvent]);

  const createNotificationFromEvent = (event: SSEEvent): ToastNotification | null => {
    const timestamp = event.timestamp ? new Date(event.timestamp) : new Date();

    switch (event.type) {
      case 'new_article':
        return {
          id: `article-${Math.random().toString(36).slice(2, 9)}`,
          type: 'new_article',
          title: '新文章',
          message: event.data.article?.title || '发现新文章',
          timestamp,
          link: event.data.article?.url,
          read: false,
        };

      case 'trending_update':
        return {
          id: `trending-${Math.random().toString(36).slice(2, 9)}`,
          type: 'trending',
          title: '爆文更新',
          message: `发现 ${event.data.articles?.length || 0} 篇新的低粉爆文`,
          timestamp,
          read: false,
        };

      case 'monitor_alert':
        return {
          id: `monitor-${Math.random().toString(36).slice(2, 9)}`,
          type: 'monitor',
          title: '监控告警',
          message: event.data.tweet?.content?.slice(0, 100) || '收到监控告警',
          timestamp,
          link: event.data.tweet?.url,
          read: false,
        };

      case 'system_notification':
        return {
          id: `system-${Math.random().toString(36).slice(2, 9)}`,
          type: event.data.level === 'error' ? 'error' : 'system',
          title: '系统通知',
          message: event.data.message || '系统消息',
          timestamp,
          read: false,
        };

      default:
        return null;
    }
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  const clearAll = () => {
    setNotifications([]);
    setUnreadCount(0);
  };

  const visibleNotifications = notifications.slice(0, maxVisible);

  return (
    <div className={cn('fixed top-4 right-4 z-50 flex flex-col gap-2 w-80', className)}>
      {/* 未读计数徽章 */}
      {unreadCount > 0 && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
            {unreadCount} 条未读通知
          </span>
          <div className="flex gap-2">
            <button
              onClick={markAllAsRead}
              className="text-xs text-blue-600 hover:text-blue-700"
            >
              全部已读
            </button>
            <button
              onClick={clearAll}
              className="text-xs text-gray-500 hover:text-gray-600"
            >
              清空
            </button>
          </div>
        </div>
      )}

      {/* 连接状态指示器 */}
      {!isConnected && (
        <div className="text-xs text-center text-gray-500 py-1">
          实时连接已断开，正在重连...
        </div>
      )}

      {/* 通知列表 */}
      {visibleNotifications.map(notification => (
        <Toast
          key={notification.id}
          notification={notification}
          onClose={() => removeNotification(notification.id)}
          onClick={() => markAsRead(notification.id)}
        />
      ))}
    </div>
  );
}

/**
 * 通知 Badge - 显示在导航栏
 */
export function NotificationBadge() {
  const { lastEvent, isConnected } = useSSEEvents();
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (lastEvent) {
      setCount(prev => prev + 1);
      const timer = setTimeout(() => {
        setCount(c => Math.max(0, c - 1));
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [lastEvent]);

  if (count === 0) return null;

  return (
    <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center animate-pulse">
      {count > 9 ? '9+' : count}
    </span>
  );
}
