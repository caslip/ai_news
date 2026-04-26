# 信源管理 API

> RSS、Twitter、GitHub 等内容信源的管理接口

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/sources` |
| 认证方式 | Bearer Token（必需） |

---

## 获取信源列表

### 列表查询

**请求方法** `GET /api/sources`

**描述**: 获取用户可访问的信源列表

**认证**: 需要（Bearer Token）

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `type` | string | 否 | - | 信源类型过滤：rss / twitter / github / netter |
| `is_active` | boolean | 否 | - | 是否激活状态过滤 |
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量（最大 100） |

**请求示例**:

```bash
# 获取所有 RSS 信源
GET /api/sources?type=rss

# 获取已激活的信源
GET /api/sources?is_active=true

# 分页查询
GET /api/sources?page=2&page_size=10
```

**响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Hacker News",
      "type": "rss",
      "config": {
        "feed_url": "https://hnrss.org/frontpage"
      },
      "is_active": true,
      "last_fetched_at": "2024-01-15T10:30:00Z",
      "created_by": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "551e8400-e29b-41d4-a716-446655440001",
      "name": "AI Twitter",
      "type": "twitter",
      "config": {
        "account": "@AINews"
      },
      "is_active": true,
      "last_fetched_at": "2024-01-15T10:00:00Z",
      "created_by": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2024-01-05T00:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `items` | array | 信源列表 |
| `total` | integer | 总数量 |
| `page` | integer | 当前页码 |
| `page_size` | integer | 每页数量 |

---

## 创建信源

### 新建信源

**请求方法** `POST /api/sources`

**描述**: 创建一个新的内容信源

**认证**: 需要（Bearer Token）

**请求头**:

```
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | string | 是 | 信源名称（1-255 字符） |
| `type` | string | 是 | 信源类型：rss / twitter / github / netter |
| `config` | object | 是 | 信源配置 |

**Config 参数说明**:

| 信源类型 | 配置字段 | 描述 |
|----------|----------|------|
| `rss` | `feed_url` | RSS 订阅地址 |
| `twitter` | `account` | Twitter 账号 (@username) |
| `github` | `org` / `repo` | GitHub 组织/仓库 |
| `netter` | `account` | 微信公众号账号 |

**请求示例**:

```json
{
  "name": "AI Daily News",
  "type": "rss",
  "config": {
    "feed_url": "https://aidaily.example.com/rss"
  }
}
```

```json
{
  "name": "OpenAI Twitter",
  "type": "twitter",
  "config": {
    "account": "@OpenAI"
  }
}
```

```json
{
  "name": "LangChain Repository",
  "type": "github",
  "config": {
    "org": "langchain-ai",
    "repo": "langchain"
  }
}
```

**响应示例** (201 Created):

```json
{
  "id": "552e8400-e29b-41d4-a716-446655440002",
  "name": "AI Daily News",
  "type": "rss",
  "config": {
    "feed_url": "https://aidaily.example.com/rss"
  },
  "is_active": true,
  "last_fetched_at": null,
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": null
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 422 | 参数验证失败 |

---

## 获取信源详情

### 信源详情

**请求方法** `GET /api/sources/{source_id}`

**描述**: 获取单个信源的详细信息

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `source_id` | string (UUID) | 是 | 信源 ID |

**响应示例** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Hacker News",
  "type": "rss",
  "config": {
    "feed_url": "https://hnrss.org/frontpage"
  },
  "is_active": true,
  "last_fetched_at": "2024-01-15T10:30:00Z",
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 信源不存在 |

---

## 更新信源

### 修改信源

**请求方法** `PUT /api/sources/{source_id}`

**描述**: 更新信源信息

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `source_id` | string (UUID) | 是 | 信源 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | string | 否 | 信源名称（1-255 字符） |
| `is_active` | boolean | 否 | 是否激活 |
| `config` | object | 否 | 信源配置 |

**请求示例**:

```json
{
  "name": "Hacker News Updated",
  "is_active": true,
  "config": {
    "feed_url": "https://hnrss.org/frontpage"
  }
}
```

**响应示例** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Hacker News Updated",
  "type": "rss",
  "config": {
    "feed_url": "https://hnrss.org/frontpage"
  },
  "is_active": true,
  "last_fetched_at": "2024-01-15T10:30:00Z",
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T12:30:00Z"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 信源不存在 |

---

## 切换信源状态

### 启用/禁用信源

**请求方法** `PATCH /api/sources/{source_id}/toggle`

**描述**: 切换信源的激活状态

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `source_id` | string (UUID) | 是 | 信源 ID |

**响应示例** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Hacker News",
  "type": "rss",
  "config": {
    "feed_url": "https://hnrss.org/frontpage"
  },
  "is_active": false,
  "last_fetched_at": "2024-01-15T10:30:00Z",
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T12:35:00Z"
}
```

**说明**: 调用此接口会将 `is_active` 状态取反。

---

## 删除信源

### 删除信源

**请求方法** `DELETE /api/sources/{source_id}`

**描述**: 删除指定的信源

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `source_id` | string (UUID) | 是 | 信源 ID |

**响应**: 204 No Content

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 信源不存在 |

---

## 批量删除信源

### 批量删除

**请求方法** `POST /api/sources/batch-delete`

**描述**: 批量删除多个信源

**认证**: 需要（Bearer Token）

**请求头**:

```
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `source_ids` | array[string] | 是 | 要删除的信源 ID 列表（至少 1 个） |

**请求示例**:

```json
{
  "source_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "551e8400-e29b-41d4-a716-446655440001"
  ]
}
```

**响应示例** (200 OK):

```json
{
  "deleted_count": 2,
  "not_found_ids": [],
  "total_requested": 2
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `deleted_count` | integer | 成功删除的数量 |
| `not_found_ids` | array | 不存在的 ID 列表 |
| `total_requested` | integer | 请求删除的总数 |

---

## 测试信源

### 测试信源连接

**请求方法** `POST /api/sources/{source_id}/test`

**描述**: 手动测试信源连接并抓取内容

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `source_id` | string (UUID) | 是 | 信源 ID |

**响应示例** (200 OK):

```json
{
  "success": true,
  "message": "成功抓取 15 篇文章",
  "article_count": 15
}
```

```json
{
  "success": false,
  "message": "抓取失败: Connection timeout",
  "article_count": 0
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `success` | boolean | 是否成功 |
| `message` | string | 结果描述 |
| `article_count` | integer | 抓取到的文章数量 |

---

## 数据模型

### SourceType (枚举)

| 值 | 描述 |
|----|------|
| `rss` | RSS 订阅源 |
| `twitter` | Twitter/X 账号 |
| `github` | GitHub 仓库 |
| `netter` | 微信公众号 |

### SourceResponse

```typescript
interface SourceResponse {
  id: string;                      // UUID
  name: string;                    // 信源名称
  type: SourceType;                // 信源类型
  config: SourceConfig;            // 配置信息
  is_active: boolean;              // 是否激活
  last_fetched_at: string | null; // 最后抓取时间
  created_by: string | null;      // 创建者 ID
  created_at: string;             // 创建时间
  updated_at: string | null;      // 更新时间
}
```

### SourceConfig

```typescript
// RSS 类型
interface RSSConfig {
  feed_url: string;  // RSS 订阅地址
}

// Twitter 类型
interface TwitterConfig {
  account: string;    // Twitter 账号 (@username)
}

// GitHub 类型
interface GitHubConfig {
  org: string;        // 组织名称
  repo: string;       // 仓库名称
}

// Netter 类型
interface NetterConfig {
  account: string;    // 微信公众号账号
}
```

### SourceListResponse

```typescript
interface SourceListResponse {
  items: SourceResponse[];
  total: number;
  page: number;
  page_size: number;
}
```

### SourceTestResponse

```typescript
interface SourceTestResponse {
  success: boolean;
  message: string;
  article_count: number;
}
```
