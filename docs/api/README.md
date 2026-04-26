# AI News API 文档

> AI News Aggregator 后端 API 参考文档 - 自动抓取、分发与精选 AI 领域资讯

## 项目简介

AI News API 是一个高效的信息聚合平台后端服务，支持：

- **多源采集**：RSS 订阅源、Twitter/X、GitHub、微信公众号等信源
- **智能筛选**：基于策略的个性化内容推荐
- **实时推送**：通过 WebSocket/SSE 实现内容实时推送
- **低粉爆文**：发现高价值的小众创作者内容

## Base URL

| 环境 | Base URL |
|------|----------|
| 开发环境 | `http://localhost:8000` |
| 生产环境 | `https://api.example.com` |

## 认证方式

API 采用 **Bearer Token** 认证方式进行用户身份验证。

### 获取 Token

通过登录或注册接口获取访问令牌：

```http
POST /api/auth/login
Authorization: Bearer <access_token>
```

### Token 刷新

访问令牌有效期为 30 分钟（可配置），可通过刷新接口获取新令牌：

```http
POST /api/auth/refresh
Authorization: Bearer <access_token>
```

### 请求示例

```bash
curl -X GET "http://localhost:8000/api/articles" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 通用响应格式

所有 API 响应均采用统一的 JSON 格式。

### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 分页响应

列表类接口返回分页数据：

```json
{
  "items": [ ... ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 错误响应

```json
{
  "detail": "错误描述信息"
}
```

## HTTP 状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `200` | OK | 请求成功 |
| `201` | Created | 资源创建成功 |
| `204` | No Content | 请求成功，无返回内容（通常用于删除操作） |
| `400` | Bad Request | 请求参数错误 |
| `401` | Unauthorized | 未认证或 Token 无效 |
| `403` | Forbidden | 无权限访问 |
| `404` | Not Found | 资源不存在 |
| `422` | Unprocessable Entity | 请求数据验证失败 |
| `500` | Internal Server Error | 服务器内部错误 |

## 错误码说明

| 错误码 | 含义 | 处理建议 |
|--------|------|----------|
| `AUTH_001` | 邮箱已注册 | 尝试登录或使用其他邮箱 |
| `AUTH_002` | 邮箱或密码错误 | 检查登录凭据 |
| `AUTH_003` | Token 已过期 | 调用刷新接口获取新 Token |
| `AUTH_004` | 无效的 Token | 重新登录获取新 Token |
| `AUTH_005` | 需要管理员权限 | 联系管理员授权 |
| `RESOURCE_001` | 资源不存在 | 检查资源 ID 是否正确 |
| `RESOURCE_002` | 资源已存在 | 检查是否重复创建 |
| `VALIDATION_001` | 参数验证失败 | 检查请求参数格式 |

## 通用请求参数

### 分页参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码，从 1 开始 |
| `page_size` | integer | 否 | 20 | 每页数量，最大 100 |

### 排序参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `sort` | string | 否 | hot | 排序方式：hot（热度）/ time（时间） |

## API 文档索引

- [认证 API](auth.md) - 用户注册、登录、OAuth 等
- [文章 API](articles.md) - 文章列表、详情、收藏等
- [信源 API](sources.md) - RSS、Twitter、GitHub 等信源管理
- [收藏 API](favorites.md) - 收藏夹和标签管理
- [策略 API](strategies.md) - 推荐策略管理
- [监控 API](monitor.md) - 关键词和账号监控
- [GitHub API](github.md) - GitHub Trending 数据
- [管理后台 API](admin.md) - 系统管理和用户管理
- [WebSocket API](websocket.md) - 实时推送

## SDK 和示例

### JavaScript / TypeScript

```typescript
const API_BASE = 'http://localhost:8000/api';

// 登录获取 Token
const login = async (email: string, password: string) => {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
};

// 认证请求示例
const getArticles = async (token: string) => {
  const res = await fetch(`${API_BASE}/articles`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return res.json();
};
```

### Python

```python
import httpx

API_BASE = "http://localhost:8000/api"

# 登录获取 Token
def login(email: str, password: str):
    with httpx.Client() as client:
        response = client.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password}
        )
        return response.json()

# 认证请求示例
def get_articles(token: str):
    with httpx.Client() as client:
        response = client.get(
            f"{API_BASE}/articles",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## 联系我们

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至 support@example.com
