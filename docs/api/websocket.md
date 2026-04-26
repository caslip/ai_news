# WebSocket / SSE 实时推送 API

> 基于 Server-Sent Events (SSE) 的实时推送接口

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/events` |
| 协议 | Server-Sent Events (SSE) |
| 认证方式 | 可选（部分事件需要） |

## 技术说明

本 API 使用 **Server-Sent Events (SSE)** 协议实现服务端向客户端的实时推送。与 WebSocket 不同，SSE 是单向通道，只能从服务器向客户端推送数据。

**SSE 优势**：
- 基于 HTTP 协议，无需特殊协议支持
- 自动重连机制
- 支持自定义事件类型
- 更简单的服务端实现

---

## 事件流端点

### 通用事件流

**请求方法** `GET /api/events`

**描述**: 接收所有类型的实时事件

**认证**: 不需要

**查询参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `channels` | string | 否 | 订阅的频道（逗号分隔） |

**事件类型**:

| 事件类型 | 描述 |
|----------|------|
| `connected` | 连接成功 |
| `ping` | 心跳（每 30 秒） |
| `new_article` | 新文章 |
| `trending_update` | 爆文更新 |
| `monitor_alert` | 监控告警 |
| `system_notification` | 系统通知 |

**SSE 响应格式**:

```
event: connected
data: {"client_id": "abc123", "timestamp": "2024-01-15T10:30:00Z"}

event: new_article
data: {"type": "new_article", "article": {...}, "timestamp": "2024-01-15T10:31:00Z"}

event: ping
data: {"timestamp": "2024-01-15T10:31:30Z"}
```

---

### 监控事件流

**请求方法** `GET /api/events/monitor`

**描述**: 接收 X (Twitter) 监控相关事件

**认证**: 不需要

**推送事件**:

| 事件类型 | 描述 |
|----------|------|
| `monitor_alert` | 关键词或账号匹配事件 |
| `new_article` | 新抓取的文章 |

**事件示例**:

```json
{
  "event": "monitor_alert",
  "data": {
    "type": "monitor_alert",
    "keyword": "AI",
    "matched_type": "keyword",
    "tweet": {
      "id": "123456789",
      "author": "@user",
      "content": "关于 AI 的讨论...",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "timestamp": "2024-01-15T10:31:00Z"
  }
}
```

---

### 爆文事件流

**请求方法** `GET /api/events/trending`

**描述**: 接收低粉爆文通知

**认证**: 不需要

**推送事件**:

| 事件类型 | 描述 |
|----------|------|
| `trending_update` | 新的低粉爆文 |
| `new_article` | 新文章（符合爆文条件） |

**事件示例**:

```json
{
  "event": "trending_update",
  "data": {
    "type": "trending_update",
    "articles": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "发现一个有趣的 AI 项目",
        "url": "https://twitter.com/xxx/status/123456",
        "author": "@ai_maker",
        "fan_count": 1200,
        "engagement": {
          "likes": 3500,
          "retweets": 1200
        },
        "hot_score": 8520.3
      }
    ],
    "timestamp": "2024-01-15T10:32:00Z"
  }
}
```

---

## 事件类型详解

### connected - 连接成功

**描述**: 客户端连接成功后发送的第一个事件

**事件数据**:

```json
{
  "client_id": "abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### ping - 心跳

**描述**: 服务端定期发送的心跳事件，用于保持连接活跃

**事件数据**:

```json
{
  "timestamp": "2024-01-15T10:30:30Z"
}
```

**说明**: 心跳每 30 秒发送一次

---

### new_article - 新文章

**描述**: 有新文章被抓取时推送

**事件数据**:

```json
{
  "type": "new_article",
  "article": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "ChatGPT 发布重大更新",
    "url": "https://twitter.com/xxx/status/123456",
    "summary": "OpenAI 宣布...",
    "author": "@openai",
    "source_type": "twitter",
    "hot_score": 9520.5,
    "tags": ["AI", "ChatGPT"],
    "is_low_fan_viral": false
  },
  "timestamp": "2024-01-15T10:31:00Z"
}
```

---

### trending_update - 爆文更新

**描述**: 有新的低粉爆文时推送

**事件数据**:

```json
{
  "type": "trending_update",
  "articles": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "发现一个有趣的 AI 项目",
      "url": "https://twitter.com/xxx/status/123456",
      "author": "@ai_maker",
      "fan_count": 1200,
      "hot_score": 8520.3,
      "engagement": {
        "likes": 3500,
        "retweets": 1200,
        "replies": 456
      },
      "tags": ["AI", "开源"]
    }
  ],
  "timestamp": "2024-01-15T10:32:00Z"
}
```

---

### monitor_alert - 监控告警

**描述**: 监控关键词或账号匹配到新内容时推送

**事件数据**:

```json
{
  "type": "monitor_alert",
  "keyword": "AI",
  "matched_type": "keyword",
  "tweet": {
    "id": "123456789",
    "author": "@tech_news",
    "content": "关于 AI 的最新消息...",
    "url": "https://twitter.com/xxx/status/123456789",
    "likes": 500,
    "retweets": 100,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:31:00Z"
}
```

**matched_type 值**:

| 值 | 描述 |
|----|------|
| `keyword` | 关键词匹配 |
| `account` | 账号匹配 |

---

### system_notification - 系统通知

**描述**: 系统级通知和告警

**事件数据**:

```json
{
  "type": "system",
  "level": "info",
  "message": "系统维护通知：将于 2024-01-20 02:00 进行升级",
  "timestamp": "2024-01-15T10:33:00Z"
}
```

**level 值**:

| 值 | 描述 |
|----|------|
| `info` | 信息 |
| `warning` | 警告 |
| `error` | 错误 |
| `critical` | 严重 |

---

## 客户端实现

### JavaScript 客户端示例

```javascript
class SSEClient {
  constructor(url) {
    this.url = url;
    this.eventSource = null;
    this.handlers = {};
  }

  connect() {
    this.eventSource = new EventSource(this.url);

    this.eventSource.onopen = () => {
      console.log('SSE 连接已建立');
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE 连接错误:', error);
      // EventSource 会自动重连
    };

    // 监听所有事件
    this.eventSource.onmessage = (event) => {
      console.log('收到消息:', event.data);
    };

    // 监听自定义事件
    const events = ['new_article', 'trending_update', 'monitor_alert', 'system_notification'];
    events.forEach(eventType => {
      this.eventSource.addEventListener(eventType, (event) => {
        const data = JSON.parse(event.data);
        if (this.handlers[eventType]) {
          this.handlers[eventType](data);
        }
      });
    });
  }

  on(eventType, handler) {
    this.handlers[eventType] = handler;
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

// 使用示例
const client = new SSEClient('http://localhost:8000/api/events/monitor');

client.on('monitor_alert', (data) => {
  console.log('收到监控告警:', data.keyword);
  showNotification(data.tweet);
});

client.on('new_article', (data) => {
  console.log('收到新文章:', data.article.title);
  updateArticleList(data.article);
});

client.connect();
```

### Python 客户端示例

```python
import sseclient
import requests

def listen_events():
    headers = {'Accept': 'text/event-stream'}
    response = requests.get(
        'http://localhost:8000/api/events/trending',
        headers=headers,
        stream=True
    )

    client = sseclient.SSEClient(response)

    for event in client.events():
        print(f"事件类型: {event.event}")
        print(f"数据: {event.data}")

        if event.event == 'monitor_alert':
            data = json.loads(event.data)
            handle_monitor_alert(data)

        elif event.event == 'new_article':
            data = json.loads(event.data)
            handle_new_article(data)

if __name__ == '__main__':
    listen_events()
```

---

## 前端集成示例

### React 组件示例

```tsx
import { useEffect, useState } from 'react';

interface Article {
  id: string;
  title: string;
  url: string;
  author: string;
  hot_score: number;
}

export function RealTimeFeed() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource('/api/events');

    eventSource.onopen = () => setConnected(true);

    eventSource.addEventListener('new_article', (event) => {
      const data = JSON.parse(event.data);
      setArticles(prev => [data.article, ...prev].slice(0, 50));
    });

    eventSource.addEventListener('trending_update', (event) => {
      const data = JSON.parse(event.data);
      setArticles(prev => [...data.articles, ...prev].slice(0, 50));
    });

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div>
      <h2>实时资讯</h2>
      <p>连接状态: {connected ? '已连接' : '未连接'}</p>
      <ul>
        {articles.map(article => (
          <li key={article.id}>
            <a href={article.url}>{article.title}</a>
            <span>by {article.author}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 最佳实践

### 1. 连接管理

- 页面可见性变化时断开/重连 SSE
- 使用唯一标识追踪连接状态
- 处理网络断开情况

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    eventSource.close();
  } else {
    eventSource = new EventSource('/api/events');
  }
});
```

### 2. 心跳处理

- 监听 `ping` 事件确认连接活跃
- 如果长时间没有收到任何事件，可能连接已断开

```javascript
let lastPong = Date.now();
const PONG_TIMEOUT = 60000; // 60 秒超时

eventSource.addEventListener('ping', () => {
  lastPong = Date.now();
});

// 定期检查
setInterval(() => {
  if (Date.now() - lastPong > PONG_TIMEOUT) {
    console.log('连接超时，重新连接...');
    eventSource.close();
    eventSource = new EventSource('/api/events');
  }
}, 30000);
```

### 3. 错误重试

- EventSource 有内置重连机制（默认 5 秒）
- 可以通过 `retry` 字段自定义重连时间

### 4. 性能考虑

- 不要在事件处理中进行大量计算
- 使用防抖/节流处理高频事件
- 限制本地缓存的文章数量

---

## 数据模型

### SSEEvent

```typescript
interface SSEEvent {
  event: EventType;
  data: EventData;
  id?: string;
  retry?: number;
}

type EventType =
  | 'connected'
  | 'ping'
  | 'new_article'
  | 'trending_update'
  | 'monitor_alert'
  | 'system_notification';
```

### ArticleEvent

```typescript
interface ArticleEvent {
  type: 'new_article';
  article: ArticleResponse;
  timestamp: string;
}
```

### TrendingEvent

```typescript
interface TrendingEvent {
  type: 'trending_update';
  articles: ArticleResponse[];
  timestamp: string;
}
```

### MonitorAlertEvent

```typescript
interface MonitorAlertEvent {
  type: 'monitor_alert';
  keyword: string;
  matched_type: 'keyword' | 'account';
  tweet: TweetData;
  timestamp: string;
}
```
