# 收藏 API

> 收藏夹和标签管理相关接口

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/favorites` |
| 认证方式 | Bearer Token（必需） |

---

## 获取收藏列表

### 列表查询

**请求方法** `GET /api/favorites`

**描述**: 获取当前用户的收藏列表

**认证**: 需要（Bearer Token）

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `tag` | string | 否 | - | 按标签过滤 |
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量（最大 100） |

**请求示例**:

```bash
# 获取所有收藏
GET /api/favorites

# 按标签过滤
GET /api/favorites?tag=AI

# 分页查询
GET /api/favorites?page=2&page_size=10
```

**响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440001",
      "article_id": "550e8400-e29b-41d4-a716-446655440000",
      "article": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "ChatGPT 发布重大更新",
        "url": "https://twitter.com/xxx/status/123456",
        "summary": "OpenAI 宣布 ChatGPT 迎来重大更新...",
        "author": "@openai",
        "hot_score": 9520.5,
        "tags": ["AI", "ChatGPT"],
        "fetched_at": "2024-01-15T10:30:00Z"
      },
      "tags": [
        {
          "id": "880e8400-e29b-41d4-a716-446655440001",
          "name": "AI",
          "color": "#6366f1"
        }
      ],
      "created_at": "2024-01-15T11:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `items` | array | 收藏列表 |
| `total` | integer | 总数量 |
| `page` | integer | 当前页码 |
| `page_size` | integer | 每页数量 |

---

## 添加收藏

### 收藏文章

**请求方法** `POST /api/favorites`

**描述**: 将文章添加到收藏夹

**认证**: 需要（Bearer Token）

**请求参数**:

| 参数名 | 类型 | 必填 | 位置 | 描述 |
|--------|------|------|------|------|
| `article_id` | string | 是 | Query | 文章 ID |

**请求示例**:

```bash
POST /api/favorites?article_id=550e8400-e29b-41d4-a716-446655440000
```

**响应示例** (201 Created):

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "message": "Added to favorites"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 400 | 文章已在收藏夹中 |

---

## 移除收藏

### 取消收藏

**请求方法** `DELETE /api/favorites/{bookmark_id}`

**描述**: 从收藏夹移除文章

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookmark_id` | string (UUID) | 是 | 收藏记录 ID |

**响应**: 204 No Content

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 收藏记录不存在 |

---

## 添加标签到收藏

### 添加收藏标签

**请求方法** `POST /api/favorites/{bookmark_id}/tags`

**描述**: 为收藏添加标签

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookmark_id` | string (UUID) | 是 | 收藏记录 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 位置 | 描述 |
|--------|------|------|------|------|
| `tag_id` | string | 是 | Query | 标签 ID |

**请求示例**:

```bash
POST /api/favorites/770e8400-e29b-41d4-a716-446655440001/tags?tag_id=880e8400-e29b-41d4-a716-446655440001
```

**响应示例** (200 OK):

```json
{
  "message": "Tag added"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 收藏记录或标签不存在 |

---

## 移除收藏标签

### 移除收藏标签

**请求方法** `DELETE /api/favorites/{bookmark_id}/tags/{tag_id}`

**描述**: 从收藏移除标签

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookmark_id` | string (UUID) | 是 | 收藏记录 ID |
| `tag_id` | string (UUID) | 是 | 标签 ID |

**响应**: 204 No Content

---

## 获取标签列表

### 用户标签

**请求方法** `GET /api/favorites/tags`

**描述**: 获取当前用户的所有标签

**认证**: 需要（Bearer Token）

**响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440001",
      "name": "AI",
      "color": "#6366f1"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440002",
      "name": "机器学习",
      "color": "#10b981"
    }
  ]
}
```

---

## 创建标签

### 新建标签

**请求方法** `POST /api/favorites/tags`

**描述**: 创建一个新的标签

**认证**: 需要（Bearer Token）

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `name` | string | 是 | - | 标签名称 |
| `color` | string | 否 | #6366f1 | 标签颜色（十六进制） |

**请求示例**:

```bash
POST /api/favorites/tags?name=AI&color=%236366f1
```

**响应示例** (201 Created):

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "name": "AI",
  "color": "#6366f1"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 400 | 标签已存在 |

---

## 删除标签

### 删除标签

**请求方法** `DELETE /api/favorites/tags/{tag_id}`

**描述**: 删除指定的标签

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `tag_id` | string (UUID) | 是 | 标签 ID |

**响应**: 204 No Content

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 标签不存在 |

---

## 数据模型

### BookmarkResponse

```typescript
interface BookmarkResponse {
  id: string;                      // UUID
  article_id: string;              // 文章 ID
  article: {
    id: string;
    title: string;
    url: string;
    summary: string | null;
    author: string | null;
    hot_score: number;
    tags: string[];
    fetched_at: string;
  };
  tags: Tag[];
  created_at: string;
}
```

### Tag

```typescript
interface Tag {
  id: string;     // UUID
  name: string;   // 标签名称
  color: string;  // 颜色（十六进制）
}
```

### BookmarkListResponse

```typescript
interface BookmarkListResponse {
  items: BookmarkResponse[];
  total: number;
  page: number;
  page_size: number;
}
```
