# API 404/数据为空 错误分析报告

**生成时间**: 2026-05-14  
**分析对象**: https://ai-news-nine-phi.vercel.app/  
**后端服务器**: roshxopx.cn (101.200.48.161)

---

## 错误现象

前端页面加载时，部分 API 请求返回 404 错误，控制台出现 Mixed Content 警告。

### 1. SSE 事件流 404

**请求 URL**: `https://roshxopx.cn//api/events`

**错误日志**:
```
[browser] Mixed Content: The page at 'https://ai-news-nine-phi.vercel.app/' was loaded 
over HTTPS, but requested an insecure XMLHttpRequest endpoint 
'http://roshxopx.cn/api/articles/?page=1&page_size=20&time_range=today&source_type=twitter,nitter'. 
This request has been blocked; the content must be served over HTTPS.
```

**网络请求记录**:
```
GET https://roshxopx.cn//api/events  → 404 (多次重试)
```

### 2. 请求 URL 多余斜杠

**问题**: 前端请求 `/api/events` 时，实际请求 URL 变成 `https://roshxopx.cn//api/events` (多了斜杠)

---

## 根因分析

### 1. SSE 端点路由问题

**后端 API 路由定义** (`/api/events`):
- 路由存在于 OpenAPI 文档中
- 直接调用 `curl http://localhost:8000/api/events` 返回超时
- 原因：SSE 是长连接，后端可能需要特定处理

**Nginx 重定向**:
```
HTTP → HTTPS: 301 重定向
/api/articles → https://roshxopx.cn/api/articles (HTTPS)
```

### 2. Mixed Content 错误

前端部署在 Vercel (HTTPS)，但 `NEXT_PUBLIC_API_URL` 配置为 `http://roshxopx.cn`。

浏览器安全策略阻止了 HTTP 请求：
- 页面协议: `https://`
- API 协议: `http://` ❌ 被阻止

### 3. URL 拼接问题

`useSSE.ts` 中 URL 拼接：
```typescript
const fullUrl = `${apiUrl}${url}`;
// 当 apiUrl = "https://roshxopx.cn" 且 url = "/api/events"
// 结果 = "https://roshxopx.cn/api/events" ✅

// 但有时 apiUrl = "https://roshxopx.cn/" 且 url = "/api/events"
// 结果 = "https://roshxopx.cn//api/events" ❌ 双斜杠
```

---

### 3. SSE 实现分析

SSE 后端代码结构：
```
/api/events      → event_generator() 通用事件流
/api/events/monitor → 监控事件流
/api/events/trending → 爆文事件流
```

**问题**: SSE 是长连接，curl 测试会超时，这是正常行为。但浏览器返回 404 表明可能有以下问题：

1. **Nginx 超时配置**: Nginx 默认 `proxy_read_timeout` 可能太短
2. **负载均衡**: 如果有多个 uvicorn 实例，SSE 可能无法正确路由

---

## 服务器状态检查

### 后端服务状态
```
✅ uvicorn 运行中 (PID 44313)
✅ 端口 8000 监听中
✅ Nginx 反向代理配置正确
✅ SSL 证书有效 (Let's Encrypt)
```

### 可用 API 端点 (已验证)
| 端点 | 状态 |
|------|------|
| `/api/articles/` | ✅ 200 |
| `/api/articles/stats` | ✅ 200 |
| `/api/events` | ⚠️ 超时 (SSE 长连接) |
| `/api/events/trending` | ❓ 未测试 |
| `/api/events/monitor` | ❓ 未测试 |

---

## 问题汇总

| # | 问题 | 严重程度 | 状态 |
|---|------|----------|------|
| 1 | Mixed Content: HTTP API 被 HTTPS 页面阻止 | 🔴 高 | ✅ 已修复（用户已配置 HTTPS） |
| 2 | **数据太旧 - 首页无文章** | 🔴 高 | ⚠️ 爬虫未运行，数据库最新文章是 3 天前 |
| 3 | `/api/events` 404 可能由 SSE 超时导致 | 🟡 中 | ⚠️ SSE 功能，但不影响首页显示 |
| 4 | URL 拼接可能产生双斜杠 | 🟢 低 | 代码隐患 |

---

## 🔴 核心问题：爬虫未运行，数据太旧

### 数据库状态
| 指标 | 值 |
|------|-----|
| 文章总数 | 17 |
| 本周新增 | 11 |
| 本月新增 | 17 |
| **今日新增** | **0** |

### 最新文章
| 时间 | 来源 | 标题 |
|------|------|------|
| 2026-05-11 21:34 | OpenAI (nitter) | Introducing Daybreak: frontier AI for cyber... |
| 2026-05-11 18:34 | OpenAI (nitter) | OpenAI Deployment Compan... |
| 2026-05-11 17:34 | OpenAI (nitter) | Today we're launching... |

**问题**：最后爬取时间是 **May 11**，距今 **3 天**，期间爬虫未运行。

### 原因分析
1. uvicorn 后端启动时会执行一次爬取，但之后没有定时任务
2. 爬虫服务（Celery worker）可能未运行
3. 爬虫代码可能报错导致任务失败

### 排查步骤

```bash
# 1. 检查 Celery worker 状态
ps aux | grep celery

# 2. 检查 Celery 队列
celery -A app.celery_app inspect active

# 3. 查看 Celery 日志
journalctl | grep celery

# 4. 手动触发爬取测试
curl -X POST http://localhost:8000/api/admin/sources/refresh
```

---

## 爬虫调度器分析

### 架构
调度器使用 **APScheduler** (不是 Celery)，每小时定时执行爬取任务：
- 直接调用 `celery_tasks` 中的 `do_*` 函数
- 在后台线程中执行，不阻塞主进程

### 问题定位
1. uvicorn 启动时间: **May 14** (今天)
2. 数据库最新文章: **May 11** (3天前)
3. 调度器启动后应该每小时爬取一次
4. 但文章日期没有更新 → **调度器可能未正常工作**

### 可能原因
1. 调度器启动后首次爬取失败
2. 爬虫代码报错
3. 爬取的网站结构变化
4. 网络问题

### 解决方案

**方案 A: 手动触发爬取**
```bash
# SSH 到服务器后执行
curl -X POST http://localhost:8000/api/admin/sources/refresh
```

**方案 B: 重启 uvicorn (会重新触发首次爬取)**
```bash
systemctl restart uvicorn
# 或
kill -HUP <uvicorn_pid>
```

---

## 修复建议

### 1. Mixed Content ✅ 已修复

修改前端环境变量，将 `NEXT_PUBLIC_API_URL` 从 `http://` 改为 `https://`:

```bash
# Vercel 环境变量
NEXT_PUBLIC_API_URL=https://roshxopx.cn
```

或在代码中动态处理：
```typescript
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    return window.location.protocol === 'https:' 
      ? 'https://roshxopx.cn' 
      : 'http://roshxopx.cn';
  }
  return 'https://roshxopx.cn';
};
```

### 2. 修复 SSE 路由

检查 `/api/events` 端点的实际实现，确保 SSE 长连接正确处理：

```python
# 后端 SSE 路由应使用 StreamingResponse
@router.get("/events")
async def sse_events(request: Request):
    async def event_generator():
        while True:
            # 生成事件
            yield {"event": "ping", "data": {...}}
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### 3. 修复 URL 拼接

```typescript
// 使用 URL 构造函数避免双斜杠
const fullUrl = new URL(url, apiUrl).toString();
```

---

## 错误代码对照表

| 错误类型 | 表现 | 原因 |
|---------|------|------|
| Mixed Content | HTTPS 页面请求 HTTP 资源被阻止 | API URL 使用了 http:// |
| 404 + 双斜杠 | `//api/events` | URL 拼接逻辑有问题 |
| SSE 超时 | 连接建立后无响应 | SSE 端点实现问题 |
| **首页无文章** | 显示"暂无资讯" | **爬虫未运行，数据太旧（3天前）** |

---

## 下一步行动

1. [ ] 更新 Vercel 环境变量 `NEXT_PUBLIC_API_URL=https://roshxopx.cn`
2. [ ] 检查 `/api/events` 端点的完整实现
3. [ ] 修复 URL 拼接逻辑避免双斜杠
4. [ ] 重新部署后验证

### 4. Nginx 超时配置 (SSE 需要)

如果 SSE 持续失败，需要调整 Nginx 配置：

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    
    # SSE 相关超时配置
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
    proxy_buffering off;
    proxy_cache off;
    
    # HTTP/1.1 需要
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}
```

执行命令：
```bash
# 编辑 Nginx 配置
sudo nano /etc/nginx/sites-enabled/www.roshxopx.cn

# 重载 Nginx
sudo nginx -t && sudo nginx -s reload
```

---

## 服务器配置检查

### Nginx 配置 (已检查)
```nginx
server {
    server_name roshxopx.cn www.roshxopx.cn;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/roshxopx.cn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/roshxopx.cn/privkey.pem;
}
```

⚠️ **注意**: 当前 Nginx 配置缺少 SSE 所需的超时配置！

### 检查命令

```bash
# 检查 Nginx 配置语法
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -50 /var/log/nginx/error.log

# 查看 uvicorn 日志
journalctl -u uvicorn --since '1h ago'

# 测试 API 响应
curl -I https://roshxopx.cn/api/health
curl -I https://roshxopx.cn/api/articles/
```

---

## 错误记录汇总

| 时间 | 错误类型 | 请求 URL | 状态码 | 说明 |
|------|----------|----------|---------|------|
| 2026-05-14 | Mixed Content | `http://roshxopx.cn/api/articles/` | blocked | 浏览器阻止 HTTP 请求 |
| 2026-05-14 | 404 | `https://roshxopx.cn//api/events` | 404 | URL 双斜杠 + SSE 超时 |
| 2026-05-14 | 404 | `https://roshxopx.cn/api/events` | - | SSE 长连接，curl 超时 |

---

## 关联文档

- `NETWORK_ERROR_ANALYSIS.md` - 之前的网络错误分析
