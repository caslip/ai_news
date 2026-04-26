# 监控 API

> 关键词和账号监控配置相关接口

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/monitor` |
| 认证方式 | Bearer Token（必需） |

---

## 关键词监控

### 获取监控关键词列表

**请求方法** `GET /api/monitor/keywords`

**描述**: 获取当前用户配置的所有监控关键词

**认证**: 需要（Bearer Token）

**响应示例** (200 OK):

```json
[
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440001",
    "config_type": "keyword",
    "name": "AI 新闻",
    "value": "AI 人工智能",
    "is_active": true,
    "params": {
      "platform": "twitter",
      "language": "zh"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440002",
    "config_type": "keyword",
    "name": "机器学习",
    "value": "machine learning",
    "is_active": true,
    "params": {
      "platform": "twitter",
      "language": "en"
    },
    "created_at": "2024-01-02T00:00:00Z",
    "updated_at": "2024-01-02T00:00:00Z"
  }
]
```

---

### 创建监控关键词

**请求方法** `POST /api/monitor/keywords`

**描述**: 创建一个新的监控关键词

**认证**: 需要（Bearer Token）

**请求头**:

```
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | string | 是 | 关键词名称 |
| `value` | string | 是 | 关键词值 |
| `is_active` | boolean | 否 | 是否启用（默认 true） |
| `params` | object | 否 | 额外参数 |

**请求示例**:

```json
{
  "name": "大模型",
  "value": "LLM GPT Claude",
  "is_active": true,
  "params": {
    "platform": "twitter",
    "language": "all"
  }
}
```

**响应示例** (201 Created):

```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440003",
  "config_type": "keyword",
  "name": "大模型",
  "value": "LLM GPT Claude",
  "is_active": true,
  "params": {
    "platform": "twitter",
    "language": "all"
  },
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

### 更新监控关键词

**请求方法** `PUT /api/monitor/keywords/{keyword_id}`

**描述**: 更新指定的监控关键词

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `keyword_id` | string (UUID) | 是 | 关键词 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | string | 否 | 关键词名称 |
| `value` | string | 否 | 关键词值 |
| `is_active` | boolean | 否 | 是否启用 |
| `params` | object | 否 | 额外参数 |

**请求示例**:

```json
{
  "name": "大模型（更新）",
  "value": "LLM GPT Claude Gemini",
  "is_active": false,
  "params": {
    "platform": "twitter",
    "language": "en"
  }
}
```

**响应示例** (200 OK):

```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440003",
  "config_type": "keyword",
  "name": "大模型（更新）",
  "value": "LLM GPT Claude Gemini",
  "is_active": false,
  "params": {
    "platform": "twitter",
    "language": "en"
  },
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 关键词不存在 |

---

### 删除监控关键词

**请求方法** `DELETE /api/monitor/keywords/{keyword_id}`

**描述**: 删除指定的监控关键词

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `keyword_id` | string (UUID) | 是 | 关键词 ID |

**响应示例** (200 OK):

```json
{
  "message": "删除成功"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 关键词不存在 |

---

## 账号监控

### 获取监控账号列表

**请求方法** `GET /api/monitor/accounts`

**描述**: 获取当前用户配置的所有监控账号

**认证**: 需要（Bearer Token）

**响应示例** (200 OK):

```json
[
  {
    "id": "bb0e8400-e29b-41d4-a716-446655440001",
    "config_type": "account",
    "name": "OpenAI 官方",
    "value": "@OpenAI",
    "is_active": true,
    "params": {
      "platform": "twitter",
      "notify_on_retweet": true
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### 创建监控账号

**请求方法** `POST /api/monitor/accounts`

**描述**: 创建一个新的监控账号

**认证**: 需要（Bearer Token）

**请求头**:

```
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | string | 是 | 账号名称 |
| `value` | string | 是 | 账号标识（如 @username） |
| `is_active` | boolean | 否 | 是否启用（默认 true） |
| `params` | object | 否 | 额外参数 |

**请求示例**:

```json
{
  "name": "AI 专家",
  "value": "@AndrewYNg",
  "is_active": true,
  "params": {
    "platform": "twitter",
    "notify_on_retweet": false
  }
}
```

**响应示例** (201 Created):

```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440002",
  "config_type": "account",
  "name": "AI 专家",
  "value": "@AndrewYNg",
  "is_active": true,
  "params": {
    "platform": "twitter",
    "notify_on_retweet": false
  },
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

### 更新监控账号

**请求方法** `PUT /api/monitor/accounts/{account_id}`

**描述**: 更新指定的监控账号

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `account_id` | string (UUID) | 是 | 账号 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | string | 否 | 账号名称 |
| `value` | string | 否 | 账号标识 |
| `is_active` | boolean | 否 | 是否启用 |
| `params` | object | 否 | 额外参数 |

**请求示例**:

```json
{
  "name": "AI 专家（更新）",
  "is_active": false
}
```

**响应示例** (200 OK):

```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440002",
  "config_type": "account",
  "name": "AI 专家（更新）",
  "value": "@AndrewYNg",
  "is_active": false,
  "params": {
    "platform": "twitter",
    "notify_on_retweet": false
  },
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 账号不存在 |

---

### 删除监控账号

**请求方法** `DELETE /api/monitor/accounts/{account_id}`

**描述**: 删除指定的监控账号

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `account_id` | string (UUID) | 是 | 账号 ID |

**响应示例** (200 OK):

```json
{
  "message": "删除成功"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 账号不存在 |

---

## 测试监控配置

### 测试监控配置

**请求方法** `POST /api/monitor/test`

**描述**: 测试监控配置是否有效

**认证**: 需要（Bearer Token）

**请求参数**:

| 参数名 | 类型 | 必填 | 位置 | 描述 |
|--------|------|------|------|------|
| `value` | string | 是 | Query | 要测试的值 |
| `config_type` | string | 是 | Query | 配置类型：keyword / account |

**请求示例**:

```bash
POST /api/monitor/test?value=AI&config_type=keyword
POST /api/monitor/test?value=@OpenAI&config_type=account
```

**响应示例** (200 OK):

```json
{
  "status": "success",
  "message": "测试 keyword: AI 连接成功",
  "mock": true
}
```

---

## 数据模型

### MonitorConfigResponse

```typescript
interface MonitorConfigResponse {
  id: string;                      // UUID
  config_type: string;             // 配置类型：keyword / account
  name: string;                     // 名称
  value: string;                   // 值（关键词或账号）
  is_active: boolean;              // 是否启用
  params: MonitorParams | null;    // 额外参数
  created_at: string;             // 创建时间
  updated_at: string;             // 更新时间
}
```

### MonitorParams

```typescript
interface MonitorParams {
  // 平台参数
  platform?: string;    // 平台：twitter, weibo, etc.

  // 语言参数
  language?: string;    // 语言：zh, en, all

  // 通知参数
  notify_on_retweet?: boolean;  // 转推时通知
  notify_on_reply?: boolean;    // 回复时通知
  notify_on_quote?: boolean;    // 引用推文时通知
}
```

### MonitorConfigCreate

```typescript
interface MonitorConfigCreate {
  name: string;             // 名称
  value: string;           // 值
  is_active?: boolean;      // 是否启用（默认 true）
  params?: MonitorParams;   // 额外参数
}
```

### MonitorConfigUpdate

```typescript
interface MonitorConfigUpdate {
  name?: string;
  value?: string;
  is_active?: boolean;
  params?: MonitorParams;
}
```

---

## params 参数说明

### 平台参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `platform` | string | - | 监控平台：twitter, weibo |

### 语言参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `language` | string | all | 筛选语言：zh（中文）/ en（英文）/ all（全部） |

### 通知参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `notify_on_retweet` | boolean | false | 转推时是否通知 |
| `notify_on_reply` | boolean | false | 回复时是否通知 |
| `notify_on_quote` | boolean | false | 引用推文时是否通知 |
