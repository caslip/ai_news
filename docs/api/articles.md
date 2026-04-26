# 文章 API

> 文章获取、筛选、收藏相关接口

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/articles` |
| 认证方式 | Bearer Token（部分接口需要） |

---

## 获取文章列表

### 列表查询

**请求方法** `GET /api/articles`

**描述**: 获取文章列表，支持多种筛选和排序方式

**认证**: 不需要（登录用户可获取收藏状态）

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `source` | string | 否 | - | 信源 ID 过滤 |
| `source_type` | string | 否 | - | 信源类型过滤 |
| `time_range` | string | 否 | today | 时间范围：today / week / month |
| `sort` | string | 否 | hot | 排序方式：hot（热度）/ time（时间） |
| `q` | string | 否 | - | 搜索关键词（匹配标题和摘要） |
| `is_low_fan_viral` | boolean | 否 | - | 低粉爆文过滤 |
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量（最大 100） |

**请求示例**:

```bash
# 获取今日热门文章
GET /api/articles?sort=hot&time_range=today&page=1&page_size=20

# 获取 Twitter 源文章
GET /api/articles?source_type=twitter&page=1&page_size=10

# 搜索关键词
GET /api/articles?q=AI&sort=time&time_range=week

# 获取低粉爆文
GET /api/articles?is_low_fan_viral=true&sort=hot
```

**响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "source_id": "660e8400-e29b-41d4-a716-446655440001",
      "source_name": "AI Daily",
      "source_type": "twitter",
      "title": "ChatGPT 发布重大更新",
      "url": "https://twitter.com/xxx/status/123456",
      "summary": "OpenAI 宣布 ChatGPT 迎来重大更新...",
      "author": "@openai",
      "hot_score": 9520.5,
      "fan_count": 500000,
      "engagement": {
        "likes": 12500,
        "retweets": 3200,
        "replies": 890
      },
      "is_low_fan_viral": false,
      "tags": ["AI", "ChatGPT", "OpenAI"],
      "raw_metadata": {
        "tweet_id": "123456",
        "repo": null
      },
      "fetched_at": "2024-01-15T10:30:00Z",
      "published_at": "2024-01-15T10:25:00Z",
      "created_at": "2024-01-15T10:30:00Z",
      "is_bookmarked": false
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `items` | array | 文章列表 |
| `total` | integer | 总数量 |
| `page` | integer | 当前页码 |
| `page_size` | integer | 每页数量 |
| `total_pages` | integer | 总页数 |

### ArticleResponse 字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | string (UUID) | 文章唯一标识 |
| `source_id` | string \| null | 信源 ID |
| `source_name` | string \| null | 信源名称 |
| `source_type` | string \| null | 信源类型：rss / twitter / github / netter |
| `title` | string | 文章标题 |
| `url` | string | 原文链接 |
| `summary` | string \| null | 文章摘要 |
| `author` | string \| null | 作者 |
| `hot_score` | float | 热度分数 |
| `fan_count` | integer | 作者粉丝数 |
| `engagement` | object | 互动数据 |
| `is_low_fan_viral` | boolean | 是否为低粉爆文 |
| `tags` | array | 标签列表 |
| `raw_metadata` | object \| null | 原始元数据 |
| `fetched_at` | datetime | 抓取时间 |
| `published_at` | datetime \| null | 发布时间 |
| `created_at` | datetime | 创建时间 |
| `is_bookmarked` | boolean | 是否已收藏（仅登录用户有效） |

---

## 获取文章统计

### 统计数据

**请求方法** `GET /api/articles/stats`

**描述**: 获取文章统计数据

**认证**: 不需要

**请求参数**: 无

**响应示例** (200 OK):

```json
{
  "today_count": 245,
  "week_count": 1823,
  "month_count": 7650,
  "total_count": 156789
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `today_count` | integer | 今日文章数量 |
| `week_count` | integer | 本周文章数量 |
| `month_count` | integer | 本月文章数量 |
| `total_count` | integer | 文章总数 |

---

## 获取文章详情

### 文章详情

**请求方法** `GET /api/articles/{article_id}`

**描述**: 获取单篇文章的详细信息

**认证**: 不需要（登录用户可获取收藏状态）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `article_id` | string (UUID) | 是 | 文章 ID |

**响应示例** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source_id": "660e8400-e29b-41d4-a716-446655440001",
  "source_name": "AI Daily",
  "source_type": "twitter",
  "title": "ChatGPT 发布重大更新",
  "url": "https://twitter.com/xxx/status/123456",
  "summary": "OpenAI 宣布 ChatGPT 迎来重大更新...",
  "author": "@openai",
  "hot_score": 9520.5,
  "fan_count": 500000,
  "engagement": {
    "likes": 12500,
    "retweets": 3200,
    "replies": 890
  },
  "is_low_fan_viral": false,
  "tags": ["AI", "ChatGPT", "OpenAI"],
  "raw_metadata": {
    "tweet_id": "123456"
  },
  "fetched_at": "2024-01-15T10:30:00Z",
  "published_at": "2024-01-15T10:25:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "is_bookmarked": true
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 文章不存在 |

---

## 获取热门文章

### 低粉爆文列表

**请求方法** `GET /api/articles/trending`

**描述**: 获取低粉爆文列表（粉丝少但互动高的文章）

**认证**: 不需要（登录用户可获取收藏状态）

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量（最大 100） |

**请求示例**:

```bash
GET /api/articles/trending?page=1&page_size=20
```

**响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "source_id": "660e8400-e29b-41d4-a716-446655440001",
      "source_name": "AI Insights",
      "source_type": "twitter",
      "title": "发现一个有趣的 AI 项目",
      "url": "https://twitter.com/xxx/status/789012",
      "summary": "一个小团队开发的 AI 工具...",
      "author": "@ai_maker",
      "hot_score": 8520.3,
      "fan_count": 1200,
      "engagement": {
        "likes": 3500,
        "retweets": 1200,
        "replies": 456
      },
      "is_low_fan_viral": true,
      "tags": ["AI", "开源项目"],
      "raw_metadata": null,
      "fetched_at": "2024-01-15T11:00:00Z",
      "published_at": "2024-01-15T10:55:00Z",
      "created_at": "2024-01-15T11:00:00Z",
      "is_bookmarked": false
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

## 收藏文章

### 收藏文章

**请求方法** `POST /api/articles/{article_id}/bookmark`

**描述**: 将文章添加到收藏夹

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `article_id` | string (UUID) | 是 | 文章 ID |

**响应示例** (201 Created):

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "message": "Article bookmarked"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 400 | 文章已在收藏夹中 |
| 404 | 文章不存在 |
| 401 | 未认证 |

---

## 取消收藏

### 取消文章收藏

**请求方法** `DELETE /api/articles/{article_id}/bookmark`

**描述**: 从收藏夹移除文章

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `article_id` | string (UUID) | 是 | 文章 ID |

**响应示例** (200 OK):

```json
{
  "message": "Bookmark removed"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 收藏记录不存在 |
| 401 | 未认证 |

---

## 数据模型

### ArticleResponse

```typescript
interface ArticleResponse {
  id: string;                    // UUID
  source_id: string | null;      // 信源 ID
  source_name: string | null;    // 信源名称
  source_type: string | null;    // 信源类型
  title: string;                 // 标题
  url: string;                   // 原文链接
  summary: string | null;        // 摘要
  content_hash: string | null;   // 内容哈希
  author: string | null;         // 作者
  hot_score: number;             // 热度分数
  fan_count: number;             // 粉丝数
  engagement: Engagement;         // 互动数据
  is_low_fan_viral: boolean;     // 低粉爆文标记
  tags: string[];                // 标签
  raw_metadata: object | null;   // 原始元数据
  fetched_at: string;            // ISO 时间
  published_at: string | null;   // 发布时间
  created_at: string;            // 创建时间
  is_bookmarked: boolean;        // 是否收藏
}

interface Engagement {
  likes?: number;
  retweets?: number;
  replies?: number;
  shares?: number;
  views?: number;
}
```

### ArticleListResponse

```typescript
interface ArticleListResponse {
  items: ArticleResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

### ArticleStatsResponse

```typescript
interface ArticleStatsResponse {
  today_count: number;
  week_count: number;
  month_count: number;
  total_count: number;
}
```
