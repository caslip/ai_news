# Network Error 分析报告

## 错误现象

前端 (`frontend_writer`，端口 3002) 登录后，所有需要调用后端 API 的请求都返回 **Network Error**：

```
[browser] [API Error] GET /api/auth/me {
  data: undefined,
  message: 'Network Error',
  status: undefined,
  statusText: undefined
}
```

受影响的前端页面路由：
- `/` (首页)
- `/auth/login` (登录页)

受影响的 API 端点：
- `GET /api/auth/me` — 获取当前用户信息
- `GET /api/writer/stats` — 获取写作统计
- `GET /api/writer/drafts/` — 获取草稿列表

---

## 根因分析

### 1. CORS 预检请求被拦截（最可能的原因）

CORS 流程分为两步：

1. **OPTIONS 预检请求**（浏览器自动发起）
2. **实际请求**（GET/POST 等）

如果后端服务未运行、或后端服务端口（8001）不在允许列表中，预检请求会失败，导致浏览器阻止所有后续请求，直接报 `Network Error`。

### 2. 后端服务未启动

如果后端 FastAPI 服务未运行，`fetch` / `axios` 请求会因为无法建立 TCP 连接而失败，错误类型为 `Network Error`，无 HTTP 状态码。

**检查命令**：

```bash
# Windows
netstat -ano | findstr 8001

# 或检查 Docker 容器
docker ps | grep backend
```

### 3. `allowed_origins` 配置缺失

当前端请求的 origin（如 `http://localhost:3002`）不在后端的 `allowed_origins` 列表中时：

- FastAPI 会返回无 CORS 头的响应
- 浏览器会阻止实际请求（有时表现为 Network Error）

当前配置支持：
```python
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
]
```

### 4. API_BASE_URL 配置错误

前端 API 地址配置在 `frontend_writer/src/lib/api.ts`：

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
```

如果后端实际运行在不同的端口或地址，请求会失败。

---

## 排查步骤

### Step 1：确认后端服务状态

```bash
# 直接测试后端是否可访问
curl http://localhost:8001/api/health
```

期望响应：
```json
{"status": "healthy", "version": "1.0.0"}
```

### Step 2：测试完整 CORS 流程

```bash
# 测试 OPTIONS 预检请求
curl -X OPTIONS "http://localhost:8001/api/auth/me" \
  -H "Origin: http://localhost:3002" \
  -H "Access-Control-Request-Method: GET" \
  -v

# 测试实际 GET 请求（带 token）
curl http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer <your_token>" \
  -H "Origin: http://localhost:3002"
```

检查响应头中是否包含：
```
Access-Control-Allow-Origin: http://localhost:3002
Access-Control-Allow-Credentials: true
```

### Step 3：检查前端环境变量

查看 `frontend_writer/.env.local` 是否存在且配置正确：

```bash
cat frontend_writer/.env.local
```

应包含：
```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Step 4：检查浏览器 Network 面板

1. 打开浏览器 DevTools（F12）
2. 切换到 **Network** 标签
3. 复现登录操作
4. 查找失败的请求，观察：
   - 请求的 **URL** 是否正确
   - **Status** 是否为 `(failed)` 或 `net::ERR_*`
   - **Timing** 是否为 0ms（连接被拒绝）

---

## 修复方案

### 方案 A：确保后端服务正常运行

```bash
# 使用 uvicorn 启动后端
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 或使用 Docker
docker-compose up backend
```

### 方案 B：更新 CORS 配置

如果需要支持新的域名，修改 `backend/app/config.py`：

```python
allowed_origins: list[str] | str = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    # 添加其他需要的域名
    "http://your-domain.com",
]
```

### 方案 C：设置前端环境变量

创建 `frontend_writer/.env.local`：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## 关联问题：刷新页面后状态丢失（Token 被误清除）

### 问题现象

用户登录后刷新页面，页面跳转回登录页，状态丢失。

### 根因

`authStore.ts` 中 `fetchCurrentUser` 的 `catch` 块在**任何错误**（包括网络错误）时都会清除 token：

```typescript
// 修复前
} catch {
  delete apiClient.defaults.headers.common["Authorization"];
  set({
    user: null,
    token: null,
    isAuthenticated: false,
  });
  return false;
}
```

当后端服务未运行时，`/api/auth/me` 抛出 **Network Error**（`error.response` 为 `undefined`），但代码仍然清除了 token，导致用户状态丢失。

### 修复方案

区分 HTTP 错误和网络错误：只有收到有效 HTTP 响应且非 2xx 时才清除 token，网络不可达时保留状态。

### 错误代码对照表

| 错误类型 | 表现 | 可能原因 |
|---------|------|---------|
| `Network Error` + `status: undefined` | TCP 连接失败 | 后端服务未启动、端口不通、防火墙拦截 |
| `CORS Error` + 4xx 状态码 | 跨域被拦截 | origin 不在 allowed_origins 中 |
| `401 Unauthorized` | 认证失败 | token 过期或无效 |
| `404 Not Found` | 路由不存在 | API 路径错误、后端路由未注册 |
| `500 Internal Server Error` | 服务器异常 | 后端代码报错 |

---

## 记录时间

**2026-05-12**

**涉及服务**：
- 前端：`frontend_writer` (Next.js, port 3002)
- 后端：`backend` (FastAPI, port 8001)
