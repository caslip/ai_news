/**
 * SSE 实时推送 Hook
 * 使用 EventSource API 订阅后端 SSE 事件流
 */

import { useEffect, useRef, useCallback, useState } from 'react';

export type SSEEventType = 
  | 'connected'
  | 'ping'
  | 'new_article'
  | 'trending_update'
  | 'monitor_alert'
  | 'system_notification';

export interface SSEEvent {
  type: SSEEventType;
  data: any;
  timestamp?: string;
}

export interface UseSSEOptions {
  /** SSE 事件流 URL */
  url: string;
  /** 是否自动连接 */
  autoConnect?: boolean;
  /** 连接成功回调 */
  onConnected?: (clientId: string) => void;
  /** 断开连接回调 */
  onDisconnected?: () => void;
  /** 错误回调 */
  onError?: (error: Event) => void;
  /** 事件处理器映射 */
  handlers?: Partial<Record<SSEEventType, (data: any) => void>>;
}

export interface UseSSEReturn {
  /** 是否已连接 */
  isConnected: boolean;
  /** 最后收到的事件 */
  lastEvent: SSEEvent | null;
  /** 所有事件历史 */
  events: SSEEvent[];
  /** 手动连接 */
  connect: () => void;
  /** 手动断开 */
  disconnect: () => void;
  /** 清除事件历史 */
  clearEvents: () => void;
}

/**
 * SSE 全局单例管理器 - 确保整个应用只有一个 SSE 连接
 */
class SSEManager {
  private static instance: SSEManager | null = null;
  
  private eventSource: EventSource | null = null;
  private isConnected = false;
  private listeners: Set<(event: SSEEvent) => void> = new Set();
  private url: string = '';
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  private constructor() {}
  
  static getInstance(): SSEManager {
    if (!SSEManager.instance) {
      SSEManager.instance = new SSEManager();
    }
    return SSEManager.instance;
  }
  
  subscribe(listener: (event: SSEEvent) => void): () => void {
    this.listeners.add(listener);
    
    // 如果还没有连接，建立连接
    if (!this.eventSource && !this.url) {
      this.connect('/api/events');
    }
    
    // 返回取消订阅函数
    return () => {
      this.listeners.delete(listener);
      
      // 如果没有监听者了，关闭连接
      if (this.listeners.size === 0) {
        this.disconnect();
      }
    };
  }
  
  private connect(url: string) {
    if (this.eventSource) {
      this.eventSource.close();
    }
    
    this.url = url;
    const apiUrl = typeof window !== 'undefined' 
      ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
      : 'http://localhost:8000';
    const fullUrl = `${apiUrl}${url}`;
    
    console.log('[SSE Manager] 正在连接:', fullUrl);
    
    this.eventSource = new EventSource(fullUrl);
    
    this.eventSource.onopen = () => {
      this.isConnected = true;
      this.reconnectAttempts = 0;
      console.debug('[SSE Manager] 已连接');
    };
    
    this.eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        const event: SSEEvent = {
          type: 'connected',
          data,
          timestamp: data.timestamp,
        };
        this.emit(event);
      } catch (err) {
        // 静默处理解析错误，不打印到控制台
      }
    };
    
    // 自定义事件类型
    const eventTypes: SSEEventType[] = [
      'ping',
      'new_article',
      'trending_update',
      'monitor_alert',
      'system_notification',
    ];
    
    eventTypes.forEach(type => {
      this.eventSource!.addEventListener(type, (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          const event: SSEEvent = {
            type,
            data,
            timestamp: data.timestamp,
          };
          this.emit(event);
        } catch (err) {
        // 静默处理事件解析错误
      }
      });
    });
    
    this.eventSource.onerror = (error) => {
      // SSE 连接失败是正常现象（后端可能没启动），不要用 console.error
      console.warn('[SSE Manager] 连接失败，将在后台重试');
      this.isConnected = false;
      
      this.eventSource?.close();
      this.eventSource = null;
      
      // 只在有监听者时重连
      if (this.listeners.size > 0 && this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        this.reconnectAttempts++;
        
        console.debug(`[SSE Manager] ${delay}ms 后重试... (第 ${this.reconnectAttempts} 次/${this.maxReconnectAttempts})`);
        
        this.reconnectTimeout = setTimeout(() => {
          this.connect(url);
        }, delay);
      }
    };
  }
  
  private disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    
    this.isConnected = false;
    this.url = '';
    this.reconnectAttempts = 0;
    console.debug('[SSE Manager] 已断开连接');
  }
  
  private emit(event: SSEEvent) {
    this.listeners.forEach(listener => {
      try {
        listener(event);
      } catch (err) {
        // 静默处理监听器错误
      }
    });
  }
  
  getIsConnected(): boolean {
    return this.isConnected;
  }
}

/**
 * SSE Hook - 使用全局单例管理器
 */
export function useSSE(options: UseSSEOptions): UseSSEReturn {
  const {
    url,
    autoConnect = true,
    onConnected,
    onDisconnected,
    onError,
    handlers = {},
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const [events, setEvents] = useState<SSEEvent[]>([]);
  
  // 使用 ref 存储 handlers
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;
  
  const clearEvents = useCallback(() => {
    setEvents([]);
    setLastEvent(null);
  }, []);

  const disconnect = useCallback(() => {
    // 单例模式下，组件卸载不应该断开全局连接
    // 只有当没有组件使用时才会断开
    onDisconnected?.();
  }, [onDisconnected]);

  const connect = useCallback(() => {
    // 单例模式下，connect 不需要实际建立连接
    // 连接由全局管理器管理
  }, []);

  // 订阅全局 SSE 事件
  useEffect(() => {
    if (!autoConnect) return;
    
    const manager = SSEManager.getInstance();
    
    const handleEvent = (event: SSEEvent) => {
      setLastEvent(event);
      setEvents(prev => [...prev.slice(-99), event]);
      setIsConnected(manager.getIsConnected());
      
      // 调用对应的事件处理器
      handlersRef.current[event.type]?.(event.data);
    };
    
    const unsubscribe = manager.subscribe(handleEvent);
    
    // 初始化连接状态
    setIsConnected(manager.getIsConnected());
    
    return () => {
      unsubscribe();
    };
  }, [autoConnect]);

  return {
    isConnected,
    lastEvent,
    events,
    connect,
    disconnect,
    clearEvents,
  };
}

/**
 * 通用 SSE Hook - 订阅所有事件
 */
export function useSSEEvents(autoConnect = true) {
  return useSSE({
    url: '/api/events',
    autoConnect,
  });
}

/**
 * 爆文章 SSE Hook - 订阅爆文更新
 */
export function useTrendingSSE(autoConnect = true) {
  return useSSE({
    url: '/api/events/trending',
    autoConnect,
    handlers: {
      trending_update: (data) => {
        console.log('[SSE] Trending update:', data);
      },
    },
  });
}

/**
 * 监控告警 SSE Hook
 */
export function useMonitorSSE(autoConnect = true) {
  return useSSE({
    url: '/api/events/monitor',
    autoConnect,
    handlers: {
      monitor_alert: (data) => {
        console.log('[SSE] Monitor alert:', data);
      },
    },
  });
}
