# 管理后台 API

> 系统管理和用户管理相关接口（需要管理员权限）

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/admin` |
| 认证方式 | Bearer Token（需要 admin 角色） |

## 权限说明

以下所有接口均需要管理员（admin）角色权限。普通用户调用将返回 403 Forbidden。

---

## 统计数据

### 获取管理统计面板

**请求方法** `GET /api/admin/stats`

**描述**: 获取系统整体统计数据

**认证**: 需要（Bearer Token + admin 角色）

**响应示例** (200 OK):

```json
{
  "total_users": 1250,
  "total_articles": 156789,
  "total_sources": 45,
  "active_sources": 38,
  "articles_today": 245,
  "articles_this_week": 1823,
  "articles_this_month": 7650,
  "low_fan_viral_count": 892,
  "bookmarks_count": 5670,
  "active_strategies": 3,
  "queue_pending_tasks": 0,
  "queue_running_tasks": 2,
  "last_crawl_at": "2024-01-15T10:30:00Z",
  "system_uptime": "N/A"
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `total_users` | integer | 总用户数 |
| `total_articles` | integer | 文章总数 |
| `total_sources` | integer | 信源总数 |
| `active_sources` | integer | 活跃信源数 |
| `articles_today` | integer | 今日文章数 |
| `articles_this_week` | integer | 本周文章数 |
| `articles_this_month` | integer | 本月文章数 |
| `low_fan_viral_count` | integer | 低粉爆文数量 |
| `bookmarks_count` | integer | 收藏总数 |
| `active_strategies` | integer | 活跃策略数 |
| `queue_pending_tasks` | integer | 待处理任务数 |
| `queue_running_tasks` | integer | 运行中任务数 |
| `last_crawl_at` | datetime \| null | 最后抓取时间 |
| `system_uptime` | string | 系统运行时间 |

---

## 用户管理

### 获取用户列表

**请求方法** `GET /api/admin/users`

**描述**: 获取所有用户列表

**认证**: 需要（Bearer Token + admin 角色）

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `skip` | integer | 否 | 0 | 跳过记录数 |
| `limit` | integer | 否 | 50 | 返回数量（最大 100） |

**响应示例** (200 OK):

```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "admin@example.com",
    "nickname": "管理员",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login_at": "2024-01-15T10:00:00Z",
    "articles_count": 50,
    "bookmarks_count": 120
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "email": "user@example.com",
    "nickname": "普通用户",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-05T00:00:00Z",
    "last_login_at": "2024-01-15T09:00:00Z",
    "articles_count": 25,
    "bookmarks_count": 45
  }
]
```

---

### 更新用户

**请求方法** `PATCH /api/admin/users/{user_id}`

**描述**: 更新用户角色或状态

**认证**: 需要（Bearer Token + admin 角色）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `user_id` | string (UUID) | 是 | 用户 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `role` | string | 是 | 用户角色：user / admin |
| `is_active` | boolean | 否 | 是否激活 |

**请求示例**:

```json
{
  "role": "admin",
  "is_active": true
}
```

**响应示例** (200 OK):

```json
{
  "message": "更新成功",
  "user_id": "660e8400-e29b-41d4-a716-446655440002"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 400 | 不能修改自己的权限 |
| 400 | 无效的角色 |
| 404 | 用户不存在 |

**说明**: 管理员不能修改自己的权限。

---

### 删除用户

**请求方法** `DELETE /api/admin/users/{user_id}`

**描述**: 删除指定用户（同时删除用户的收藏记录）

**认证**: 需要（Bearer Token + admin 角色）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `user_id` | string (UUID) | 是 | 用户 ID |

**响应示例** (200 OK):

```json
{
  "message": "删除成功"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 400 | 不能删除自己 |
| 404 | 用户不存在 |

**说明**:

- 删除用户会同时删除该用户的所有收藏记录
- 管理员不能删除自己

---

## 信源管理

### 获取信源健康状态

**请求方法** `GET /api/admin/sources/health`

**描述**: 获取所有信源的健康状态和抓取统计

**认证**: 需要（Bearer Token + admin 角色）

**响应示例** (200 OK):

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Hacker News",
    "type": "rss",
    "url": "https://hnrss.org/frontpage",
    "is_active": true,
    "last_fetched_at": "2024-01-15T10:30:00Z",
    "last_error": null,
    "success_count": 1500,
    "error_count": 0,
    "success_rate": 100.0,
    "avg_response_time_ms": 250,
    "articles_count": 1500
  },
  {
    "id": "551e8400-e29b-41d4-a716-446655440001",
    "name": "AI Twitter",
    "type": "twitter",
    "url": "",
    "is_active": true,
    "last_fetched_at": "2024-01-15T10:00:00Z",
    "last_error": "Rate limit exceeded",
    "success_count": 890,
    "error_count": 12,
    "success_rate": 98.7,
    "avg_response_time_ms": 450,
    "articles_count": 890
  }
]
```

**SourceHealthResponse 字段说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | string | 信源 ID |
| `name` | string | 信源名称 |
| `type` | string | 信源类型 |
| `url` | string | 信源 URL |
| `is_active` | boolean | 是否激活 |
| `last_fetched_at` | datetime \| null | 最后抓取时间 |
| `last_error` | string \| null | 最后错误信息 |
| `success_count` | integer | 成功抓取次数 |
| `error_count` | integer | 失败次数 |
| `success_rate` | float | 成功率（百分比） |
| `avg_response_time_ms` | integer | 平均响应时间（毫秒） |
| `articles_count` | integer | 文章数量 |

---

### 手动刷新信源

**请求方法** `POST /api/admin/sources/{source_id}/refresh`

**描述**: 手动触发指定信源的刷新任务

**认证**: 需要（Bearer Token + admin 角色）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `source_id` | string (UUID) | 是 | 信源 ID |

**响应示例** (200 OK):

```json
{
  "message": "刷新任务已提交",
  "source_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 信源不存在 |

---

## 队列管理

### 获取队列状态

**请求方法** `GET /api/admin/queue/status`

**描述**: 获取 Celery 任务队列的当前状态

**认证**: 需要（Bearer Token + admin 角色）

**响应示例** (200 OK):

```json
{
  "worker_status": [
    {
      "name": "celery@worker1",
      "status": "up",
      "active_tasks": 2
    }
  ],
  "pending_tasks": 0,
  "running_tasks": 2,
  "scheduled_tasks": 5,
  "failed_tasks_recent": 0,
  "tasks_by_type": {
    "crawl_rss": 10,
    "crawl_twitter": 5,
    "analyze_article": 20
  },
  "memory_usage_mb": null,
  "cpu_usage_percent": null
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `worker_status` | array | Worker 状态列表 |
| `pending_tasks` | integer | 待处理任务数 |
| `running_tasks` | integer | 运行中任务数 |
| `scheduled_tasks` | integer | 定时任务数 |
| `failed_tasks_recent` | integer | 最近失败任务数 |
| `tasks_by_type` | object | 各类型任务数量统计 |

### Worker 状态

| 字段 | 类型 | 描述 |
|------|------|------|
| `name` | string | Worker 名称 |
| `status` | string | 状态：up / down |
| `active_tasks` | integer | 活跃任务数 |

---

## 系统健康

### 获取系统健康状态

**请求方法** `GET /api/admin/health`

**描述**: 获取系统各组件的健康状态

**认证**: 需要（Bearer Token + admin 角色）

**响应示例** (200 OK):

```json
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "up",
      "latency_ms": 0
    },
    "redis": {
      "status": "unknown"
    },
    "celery": {
      "status": "unknown"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 86400
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | string | 整体状态：healthy / degraded / unhealthy |
| `components` | object | 各组件状态 |
| `timestamp` | datetime | 检查时间 |
| `version` | string | 系统版本 |
| `uptime_seconds` | integer | 运行时间（秒） |

### 组件状态

| 状态 | 描述 |
|------|------|
| `healthy` | 所有组件正常 |
| `degraded` | 部分组件有问题但可服务 |
| `unhealthy` | 关键组件不可用 |

---

## 日志管理

### 获取最近日志

**请求方法** `GET /api/admin/logs`

**描述**: 获取系统最近的日志记录

**认证**: 需要（Bearer Token + admin 角色）

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `lines` | integer | 否 | 100 | 返回行数 |
| `service` | string | 否 | - | 服务过滤 |

**响应示例** (200 OK):

```json
{
  "logs": [],
  "message": "日志功能待实现"
}
```

**说明**: 此接口目前为占位实现。

---

## 数据模型

### AdminStatsResponse

```typescript
interface AdminStatsResponse {
  total_users: number;
  total_articles: number;
  total_sources: number;
  active_sources: number;
  articles_today: number;
  articles_this_week: number;
  articles_this_month: number;
  low_fan_viral_count: number;
  bookmarks_count: number;
  active_strategies: number;
  queue_pending_tasks: number;
  queue_running_tasks: number;
  last_crawl_at: string | null;
  system_uptime: string;
}
```

### UserManagementResponse

```typescript
interface UserManagementResponse {
  id: string;
  email: string;
  nickname: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
  articles_count: number;
  bookmarks_count: number;
}
```

### UserRoleUpdate

```typescript
interface UserRoleUpdate {
  role: string;        // user / admin
  is_active?: boolean;
}
```

### QueueStatusResponse

```typescript
interface QueueStatusResponse {
  worker_status: WorkerStatus[];
  pending_tasks: number;
  running_tasks: number;
  scheduled_tasks: number;
  failed_tasks_recent: number;
  tasks_by_type: Record<string, number>;
  memory_usage_mb: number | null;
  cpu_usage_percent: number | null;
}

interface WorkerStatus {
  name: string;
  status: string;
  active_tasks: number;
}
```

### SystemHealthResponse

```typescript
interface SystemHealthResponse {
  status: string;  // healthy / degraded / unhealthy
  components: Record<string, ComponentStatus>;
  timestamp: string;
  version: string;
  uptime_seconds: number;
}

interface ComponentStatus {
  status: string;
  latency_ms?: number;
  error?: string;
}
```
