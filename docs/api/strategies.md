# 策略 API

> 推荐策略管理相关接口

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/strategies` |
| 认证方式 | Bearer Token（必需） |

---

## 获取策略列表

### 列表查询

**请求方法** `GET /api/strategies`

**描述**: 获取所有策略列表

**认证**: 需要（Bearer Token）

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量（最大 100） |

**请求示例**:

```bash
GET /api/strategies
GET /api/strategies?page=2&page_size=10
```

**响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440001",
      "name": "默认策略",
      "description": "基于热度和时间的综合推荐",
      "version": 2,
      "params": {
        "hot_weight": 0.7,
        "time_weight": 0.3,
        "min_score": 0.5
      },
      "is_active": true,
      "created_by": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440002",
      "name": "AI 优先策略",
      "description": "优先推荐 AI 相关内容",
      "version": 1,
      "params": {
        "keywords": ["AI", "机器学习", "深度学习"],
        "boost_factor": 1.5
      },
      "is_active": false,
      "created_by": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2024-01-10T00:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

---

## 获取当前激活策略

### 激活策略

**请求方法** `GET /api/strategies/active`

**描述**: 获取当前激活的策略

**认证**: 需要（Bearer Token）

**响应示例** (200 OK):

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440001",
  "name": "默认策略",
  "description": "基于热度和时间的综合推荐",
  "version": 2,
  "params": {
    "hot_weight": 0.7,
    "time_weight": 0.3,
    "min_score": 0.5
  },
  "is_active": true,
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 没有激活的策略 |

---

## 创建策略

### 新建策略

**请求方法** `POST /api/strategies`

**描述**: 创建一个新的推荐策略

**认证**: 需要（Bearer Token）

**请求头**:

```
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | string | 是 | 策略名称（1-255 字符） |
| `description` | string | 否 | 策略描述 |
| `params` | object | 否 | 策略参数 |

**请求示例**:

```json
{
  "name": "低粉爆文策略",
  "description": "优先推荐粉丝少但互动高的内容",
  "params": {
    "max_fan_count": 5000,
    "min_engagement_rate": 0.05,
    "hot_weight": 0.8
  }
}
```

**响应示例** (201 Created):

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440003",
  "name": "低粉爆文策略",
  "description": "优先推荐粉丝少但互动高的内容",
  "version": 1,
  "params": {
    "max_fan_count": 5000,
    "min_engagement_rate": 0.05,
    "hot_weight": 0.8
  },
  "is_active": false,
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-15T12:00:00Z"
}
```

**说明**:

- 新创建的策略默认不激活
- 如果已存在同名策略，自动递增版本号

---

## 更新策略

### 更新策略

**请求方法** `PUT /api/strategies/{strategy_id}`

**描述**: 更新策略信息，自动创建新版本

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `strategy_id` | string (UUID) | 是 | 策略 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | string | 否 | 策略名称 |
| `description` | string | 否 | 策略描述 |
| `params` | object | 否 | 策略参数 |

**请求示例**:

```json
{
  "name": "低粉爆文策略 v2",
  "description": "优化后的低粉爆文策略",
  "params": {
    "max_fan_count": 10000,
    "min_engagement_rate": 0.03,
    "hot_weight": 0.9
  }
}
```

**响应示例** (200 OK):

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "name": "低粉爆文策略 v2",
  "description": "优化后的低粉爆文策略",
  "version": 2,
  "params": {
    "max_fan_count": 10000,
    "min_engagement_rate": 0.03,
    "hot_weight": 0.9
  },
  "is_active": false,
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-15T14:00:00Z"
}
```

**说明**:

- 更新策略会创建新版本，旧版本自动禁用
- 返回新创建的策略版本

---

## 激活策略

### 设为激活

**请求方法** `PATCH /api/strategies/{strategy_id}/activate`

**描述**: 将指定策略设为激活状态

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `strategy_id` | string (UUID) | 是 | 策略 ID |

**响应示例** (200 OK):

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "name": "低粉爆文策略 v2",
  "description": "优化后的低粉爆文策略",
  "version": 2,
  "params": {
    "max_fan_count": 10000,
    "min_engagement_rate": 0.03,
    "hot_weight": 0.9
  },
  "is_active": true,
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-15T14:00:00Z"
}
```

**说明**:

- 激活一个策略会自动禁用同名下的其他策略
- 确保同一时间只有一个策略处于激活状态

---

## 获取策略历史

### 版本历史

**请求方法** `GET /api/strategies/{strategy_id}/history`

**描述**: 获取同名策略的所有版本历史

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `strategy_id` | string (UUID) | 是 | 策略 ID |

**响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "name": "低粉爆文策略",
      "description": "优化后的低粉爆文策略",
      "version": 2,
      "params": {
        "max_fan_count": 10000,
        "min_engagement_rate": 0.03,
        "hot_weight": 0.9
      },
      "is_active": true,
      "created_by": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2024-01-15T14:00:00Z"
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440003",
      "name": "低粉爆文策略",
      "description": "优先推荐粉丝少但互动高的内容",
      "version": 1,
      "params": {
        "max_fan_count": 5000,
        "min_engagement_rate": 0.05,
        "hot_weight": 0.8
      },
      "is_active": false,
      "created_by": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2024-01-15T12:00:00Z"
    }
  ],
  "total": 2
}
```

---

## 删除策略

### 删除策略

**请求方法** `DELETE /api/strategies/{strategy_id}`

**描述**: 删除指定的策略

**认证**: 需要（Bearer Token）

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `strategy_id` | string (UUID) | 是 | 策略 ID |

**响应**: 204 No Content

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 404 | 策略不存在 |

---

## 数据模型

### StrategyResponse

```typescript
interface StrategyResponse {
  id: string;            // UUID
  name: string;          // 策略名称
  description: string | null;  // 策略描述
  version: number;       // 版本号
  params: StrategyParams; // 策略参数
  is_active: boolean;    // 是否激活
  created_by: string | null;  // 创建者 ID
  created_at: string;   // 创建时间
}
```

### StrategyParams

```typescript
interface StrategyParams {
  // 通用参数
  hot_weight?: number;      // 热度权重 (0-1)
  time_weight?: number;     // 时间权重 (0-1)
  min_score?: number;       // 最低分数阈值

  // 低粉爆文参数
  max_fan_count?: number;       // 最大粉丝数
  min_engagement_rate?: number; // 最低互动率

  // 关键词参数
  keywords?: string[];     // 关键词列表
  boost_factor?: number;    // 关键词提升因子
}
```

### StrategyListResponse

```typescript
interface StrategyListResponse {
  items: StrategyResponse[];
  total: number;
  page: number;
  page_size: number;
}
```

---

## 策略参数说明

### 通用参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `hot_weight` | float | 0.7 | 热度在综合评分中的权重 |
| `time_weight` | float | 0.3 | 时间在综合评分中的权重 |
| `min_score` | float | 0.5 | 文章进入推荐的最低分数 |

### 低粉爆文参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `max_fan_count` | integer | 5000 | 最大的粉丝数阈值 |
| `min_engagement_rate` | float | 0.05 | 最低互动率 (互动数/粉丝数) |

### 关键词参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `keywords` | array | [] | 关键词列表 |
| `boost_factor` | float | 1.0 | 包含关键词文章的分数提升因子 |
