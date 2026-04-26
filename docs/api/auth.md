# 认证 API

> 用户认证相关接口，包括注册、登录、OAuth 等

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/auth` |
| 认证方式 | Bearer Token（部分接口需要） |

---

## 用户注册

### 注册新用户

**请求方法** `POST /api/auth/register`

**描述**: 创建新的用户账户

**认证**: 不需要

**请求头**:

```
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `email` | string | 是 | 邮箱地址 |
| `password` | string | 是 | 密码（最少 8 字符） |
| `nickname` | string | 是 | 昵称（2-100 字符） |

**请求示例**:

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "nickname": "AI爱好者"
}
```

**响应示例** (201 Created):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "nickname": "AI爱好者",
    "avatar_url": null,
    "role": "user",
    "push_config": {},
    "oauth_provider": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  }
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `access_token` | string | JWT 访问令牌 |
| `token_type` | string | 令牌类型，固定为 "bearer" |
| `user.id` | string | 用户唯一标识符 |
| `user.email` | string | 用户邮箱 |
| `user.nickname` | string | 用户昵称 |
| `user.role` | string | 用户角色：user / admin |
| `user.created_at` | datetime | 创建时间 |

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 400 | 邮箱已注册 |
| 422 | 参数验证失败 |

---

## 用户登录

### 邮箱密码登录

**请求方法** `POST /api/auth/login`

**描述**: 使用邮箱和密码登录

**认证**: 不需要

**请求头**:

```
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `email` | string | 是 | 邮箱地址 |
| `password` | string | 是 | 密码 |

**请求示例**:

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**响应示例** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "nickname": "AI爱好者",
    "avatar_url": null,
    "role": "user",
    "push_config": {},
    "oauth_provider": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  }
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 401 | 邮箱或密码错误 |
| 422 | 参数验证失败 |

---

## 获取当前用户

### 获取登录用户信息

**请求方法** `GET /api/auth/me`

**描述**: 获取当前已登录用户的信息

**认证**: 需要（Bearer Token）

**请求头**:

```
Authorization: Bearer <access_token>
```

**响应示例** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "nickname": "AI爱好者",
  "avatar_url": null,
  "role": "user",
  "push_config": {},
  "oauth_provider": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T08:00:00Z"
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 401 | 未认证或 Token 无效 |
| 403 | 用户账户已被禁用 |

---

## 更新当前用户

### 更新用户信息

**请求方法** `PATCH /api/auth/me`

**描述**: 更新当前登录用户的信息

**认证**: 需要（Bearer Token）

**请求头**:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `nickname` | string | 否 | 新昵称（2-100 字符） |
| `avatar_url` | string | 否 | 头像 URL |
| `push_config` | object | 否 | 推送配置 |

**请求示例**:

```json
{
  "nickname": "新昵称",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

**响应示例** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "nickname": "新昵称",
  "avatar_url": "https://example.com/avatar.jpg",
  "role": "user",
  "push_config": {},
  "oauth_provider": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T09:00:00Z"
}
```

---

## 用户登出

### 退出登录

**请求方法** `POST /api/auth/logout`

**描述**: 清除登录状态，删除访问令牌

**认证**: 不强制要求

**请求头**:

```
Authorization: Bearer <access_token>  # 可选
```

**响应示例** (200 OK):

```json
{
  "message": "Successfully logged out"
}
```

**说明**: 此接口不强制要求有效的 Token，主要用于清除客户端的认证状态。

---

## 刷新 Token

### 刷新访问令牌

**请求方法** `POST /api/auth/refresh`

**描述**: 使用当前有效的 Token 获取新的访问令牌

**认证**: 需要（Bearer Token）

**请求头**:

```
Authorization: Bearer <access_token>
```

**响应示例** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "nickname": "AI爱好者",
    "avatar_url": null,
    "role": "user",
    "push_config": {},
    "oauth_provider": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  }
}
```

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 401 | Token 无效或已过期 |
| 404 | 用户不存在 |

---

## GitHub OAuth

### 初始化 GitHub OAuth

**请求方法** `GET /api/auth/oauth/github`

**描述**: 获取 GitHub 授权 URL，用于第三方登录

**认证**: 不需要

**响应示例** (200 OK):

```json
{
  "authorization_url": "https://github.com/login/oauth/authorize?client_id=xxx&scope=read:user&state=xxx",
  "state": "xxx-xxx-xxx-xxx"
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `authorization_url` | string | GitHub 授权页面 URL |
| `state` | string | 用于防止 CSRF 攻击的状态码 |

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 503 | GitHub OAuth 未配置 |

---

### GitHub OAuth 回调

**请求方法** `GET /api/auth/oauth/github/callback`

**描述**: GitHub OAuth 授权成功后的回调接口

**认证**: 不需要

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `code` | string | 是 | GitHub 授权码 |
| `state` | string | 否 | 验证状态码 |

**响应示例** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "nickname": "github_user",
    "avatar_url": "https://avatars.githubusercontent.com/u/12345",
    "role": "user",
    "push_config": {},
    "oauth_provider": "github",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  }
}
```

**OAuth 登录逻辑**:

1. 如果用户已通过该 GitHub 账号绑定，直接登录
2. 如果用户邮箱已存在但未绑定，自动绑定 GitHub 账号
3. 如果是新用户，自动创建账户并绑定 GitHub

**错误响应**:

| 状态码 | 描述 |
|--------|------|
| 400 | 授权码无效 / 无法获取用户信息 / 无法获取邮箱 |
| 503 | GitHub OAuth 未配置 |

---

## 数据模型

### UserResponse

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | string (UUID) | 用户唯一标识 |
| `email` | string (Email) | 用户邮箱 |
| `nickname` | string | 用户昵称 |
| `avatar_url` | string \| null | 头像 URL |
| `role` | string | 角色：user / admin |
| `push_config` | object | 推送配置 |
| `oauth_provider` | string \| null | OAuth 提供商：github / google |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime \| null | 更新时间 |

### TokenResponse

| 字段 | 类型 | 描述 |
|------|------|------|
| `access_token` | string | JWT 访问令牌 |
| `token_type` | string | 令牌类型，固定为 "bearer" |
| `user` | UserResponse | 用户信息 |
