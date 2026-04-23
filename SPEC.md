# AI 新闻自动抓取网站 - 设计规格文档

> 文档版本：v1.0
> 创建日期：2026-03-28
> 状态：开发中 (Phase 4-5 进行中)

---

## 第一部分：产品定位与功能规格

### 1.1 产品概述

**产品名称：** AI News Aggregator

**一句话描述：** 一个自动抓取、分发与精选 AI 领域资讯的平台，帮助用户高效发现低粉爆文与高价值内容。

**核心价值主张：**

- **信息聚合**：一站式聚合多个来源的 AI 新闻，无需逐个网站浏览
- **去重 + 精选**：AI 驱动的去重与质量评分，过滤噪音
- **低粉爆文发现**：识别高价值但未被广泛传播的内容
- **实时监控**：X (Twitter) 关键词/账号实时推送
- **个人知识库**：收藏、标签、策略管理

---

### 1.2 功能模块清单

| # | 模块 | 描述 |
|---|------|------|
| 1 | **热点资讯** | 首页时间线，按热度/时间排序，支持筛选与搜索 |
| 2 | **低粉爆文** | 识别粉丝少但互动高的爆款内容，由 AI 策略引擎驱动 |
| 3 | **X 监控** | 关键词 + 关注账号的实时推送，基于 SSE 实时更新 |
| 4 | **收藏** | 文章收藏、标签管理、搜索过滤 |
| 5 | **信源管理** | 添加/编辑/启禁用爬取源，支持 RSS / Nitter / X 账号 / GitHub Release |
| 6 | **精选策略** | 配置 AI 评分规则，支持版本历史，一键回滚 |
| 7 | **用户管理** | 登录注册、角色权限（管理员/普通用户）、推送配置 |

---

### 1.3 用户角色

| 角色 | 权限范围 |
|------|----------|
| **访客** | 浏览热点资讯（公开内容），注册账号 |
| **普通用户** | 收藏文章、管理标签、配置 X 监控、查看个人仪表盘 |
| **管理员** | 管理所有信源、管理精选策略、管理所有用户、查看系统状态 |

---

## 第二部分：技术架构总览

### 2.1 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│                      UI/UX 层                               │
│   Next.js 15 + React 19 + shadcn/ui + Tailwind CSS         │
│   TanStack Query + Zustand + SSE                            │
└─────────────────────────────────────────────────────────────┘
                              ↕ REST API / SSE
┌─────────────────────────────────────────────────────────────┐
│                      后端层                                  │
│   FastAPI (Python) + Celery + Redis                         │
│   调度引擎 | 内容处理器 | AI分析引擎 | 策略引擎 | 用户服务  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                      数据层                                  │
│   PostgreSQL (主存) + Redis (缓存) + R2/本地存储 (文件)      │
│   向量数据库用于语义去重                                     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈选型

| 层级 | 技术选型 | 选型理由 |
|------|----------|----------|
| 前端框架 | **Next.js 15 + React 19** | App Router 约定式路由，一个仓库管全栈 |
| UI 组件库 | **shadcn/ui + Tailwind CSS** | 代码所有权，可任意定制，生态成熟 |
| 状态管理 | **TanStack Query + Zustand** | 服务器状态用 Query，客户端状态用 Zustand |
| 后端框架 | **FastAPI (Python)** | 异步优先，Swagger 自动文档，性能优异 |
| 任务队列 | **Celery + Redis** | 个人/小团队首选，扩容无压力 |
| 数据库 | **PostgreSQL** | 关系型主存，jsonb 支持灵活配置 |
| 缓存 | **Redis** | 读加速层，热榜数据缓存 |
| AI 服务 | **OpenRouter** | 一站式接入多模型，支持 Claude/GPT 等 |
| 文件存储 | **Cloudflare R2 / 本地** | 图片/附件存储，可兼容 S3 协议 |
| 爬虫生态 | **playwright + httpx + beautifulsoup4** | Python 侧爬虫生态远胜 JS |

---

## 第三部分：UI/UX 层设计

### 3.1 路由结构

| 路由 | 页面 | 描述 |
|------|------|------|
| `/` | 首页/热点资讯 | 默认落地页，展示资讯时间线 |
| `/trending` | 低粉爆文 | AI 策略筛选的爆款内容列表 |
| `/monitor` | X 监控 | 关键词/账号监控配置 + 实时推送 |
| `/favorites` | 收藏夹 | 个人收藏管理，支持标签筛选 |
| `/sources` | 信源管理 | 添加/编辑/启禁用爬取源 |
| `/strategies` | 精选策略 | AI 评分策略配置 + 版本历史 |
| `/admin` | 后台管理 | 系统状态、用户管理（仅管理员） |
| `/auth/login` | 登录页 | 邮箱密码登录 |
| `/auth/register` | 注册页 | 用户注册 |
| `/settings` | 个人设置 | 推送配置、界面偏好 |

### 3.2 目录组织（Next.js App Router）

```
ai_news/
├── app/                          # Next.js App Router
│   ├── (main)/                   # 主布局组
│   │   ├── page.tsx              # 热点资讯 /
│   │   ├── trending/page.tsx     # 低粉爆文 /trending
│   │   ├── monitor/page.tsx      # X监控 /monitor
│   │   ├── favorites/page.tsx    # 收藏 /favorites
│   │   ├── sources/page.tsx      # 信源 /sources
│   │   ├── strategies/page.tsx   # 策略 /strategies
│   │   └── layout.tsx            # 主布局（Sidebar + Header）
│   ├── admin/                    # 后台管理路由组
│   │   ├── page.tsx              # 管理员仪表盘
│   │   └── users/page.tsx        # 用户管理
│   ├── auth/                     # 认证路由组
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── settings/page.tsx         # 个人设置
│   ├── api/                      # API 路由（替代独立 BFF）
│   │   ├── articles/
│   │   ├── sources/
│   │   ├── strategies/
│   │   ├── auth/
│   │   ├── monitor/
│   │   └── sse/                  # Server-Sent Events
│   ├── globals.css
│   └── layout.tsx                # 根布局
├── components/                    # 共享组件
│   ├── ui/                       # shadcn/ui 组件
│   ├── layout/                   # Sidebar, Header, Shell
│   ├── articles/                 # 文章卡片、列表
│   ├── sources/                  # 信源相关组件
│   └── strategy/                 # 策略编辑器
├── lib/                          # 工具函数
│   ├── api.ts                   # API 客户端封装
│   ├── openrouter.ts            # OpenRouter 调用封装
│   ├── auth.ts                  # 认证工具
│   └── utils.ts
├── stores/                       # Zustand stores
│   ├── authStore.ts
│   └── uiStore.ts
├── types/                        # TypeScript 类型定义
└── hooks/                        # 自定义 hooks
```

### 3.3 组件策略

**shadcn/ui 哲学：** 代码所有权。运行 `npx shadcn add [component]` 将组件代码复制到项目中，非 npm 依赖引用。

核心使用的组件：

| 组件 | 用途 |
|------|------|
| `Card` | 文章卡片、信源卡片、策略卡片 |
| `Table` | 信源列表、用户列表、策略版本历史 |
| `Select` | 筛选条件（信源类型、排序方式） |
| `Slider` | 精选策略阈值调节 |
| `Badge` | 标签、状态徽章 |
| `Dialog` | 确认操作、编辑表单 |
| `Input / Textarea` | 搜索框、配置输入 |
| `Toast` | 操作反馈 |
| `ScrollArea` | 长列表滚动区域 |

### 3.4 状态管理方案

| 数据类型 | 方案 | 说明 |
|----------|------|------|
| **服务器状态** | TanStack Query | 文章列表、信源数据、策略数据，自动缓存/预取/失效 |
| **URL 同步状态** | `useSearchParams` | 筛选条件（时间范围、信源类型、排序）同步到 URL，刷新不丢失 |
| **全局 UI 状态** | Zustand | 用户信息、Sidebar 折叠状态、主题偏好 |
| **表单状态** | React Hook Form + Zod | 信源编辑、策略编辑等表单 |

### 3.5 实时更新方案（SSE）

X 监控页面使用 **Server-Sent Events** 而非 WebSocket：

- **原因：** 单向推送足够，Next.js Route Handler 原生支持，无需额外 WebSocket 服务器
- **端点：** `GET /api/sse/monitor?keywords=xxx&accounts=xxx`
- **事件类型：** `new_article`, `connection_established`, `heartbeat`
- **重连机制：** 前端自动重连，后端心跳间隔 30 秒

### 3.6 前端页面详细设计

#### 3.6.1 首页 / 热点资讯 (`/`)

**布局：** 三栏布局（Sidebar + 主内容 + 可选详情面板）

**核心组件：**

- `ArticleCard`：标题、来源图标、时间、热度分数、收藏按钮、标签
- `FilterBar`：时间范围下拉（今日/本周/本月）、信源多选、排序方式（热度/时间）
- `SearchInput`：全文搜索（前端防抖 300ms）
- `InfiniteScroll`：无限滚动加载（每页 20 条）
- `ArticleDetailPanel`：点击卡片展开右侧详情抽屉（摘要、AI 评分、操作按钮）

**状态示例：**

```
URL: /?source=twitter&timeRange=today&sort=hot&page=1
```

#### 3.6.2 低粉爆文 (`/trending`)

**布局：** 瀑布流 + 筛选侧栏

**核心组件：**

- `TrendCard`：放大展示互动数据（点赞/转发/评论）、粉丝数、爆文指数
- `StrategyIndicator`：显示当前使用的策略名称和关键阈值
- `ComparisonChart`：展示低粉 vs 大 V 内容的对比分布

#### 3.6.3 X 监控 (`/monitor`)

**布局：** 配置区 + 实时推送列表

**核心组件：**

- `KeywordInput`：标签输入框，支持逗号分隔多个关键词
- `AccountFollow`：关注账号列表，支持 @username 添加
- `SSELiveFeed`：实时推送列表，新文章从顶部插入，支持一键收藏
- `MonitorStats`：监控统计（今日抓取数、触发数、延迟）

#### 3.6.4 收藏夹 (`/favorites`)

**布局：** 网格视图 + 侧边标签栏

**核心组件：**

- `TagSidebar`：标签列表，支持折叠，点击过滤
- `FavoriteGrid`：收藏卡片网格，支持批量操作
- `BatchTagModal`：批量添加/移除标签

#### 3.6.5 信源管理 (`/sources`)

**布局：** Table 视图 + 顶部操作栏

**核心组件：**

- `SourceTable`：列——名称、类型、URL/账号、状态（启用/禁用）、最后抓取时间、操作
- `SourceForm`：新建/编辑信源表单，支持类型切换（RSS / Nitter / X 账号 / GitHub Release）
- `SourceTypeBadge`：信源类型标签（RSS / Nitter / Twitter / GitHub）

#### 3.6.6 精选策略 (`/strategies`)

**布局：** 策略卡片 + 版本历史面板

**核心组件：**

- `StrategyCard`：策略名称、描述、关键参数（评分阈值、最小互动数、最大粉丝数）
- `StrategyEditor`：Slider + Input 配置各项参数
- `VersionHistory`：版本列表（版本号、时间、操作人、变更说明），支持一键激活历史版本
- `StrategyPreview`：实时预览当前策略筛选结果

#### 3.6.7 后台管理 (`/admin`)

**布局：** 仪表盘卡片 + 侧边导航

**核心组件：**

- `StatsCards`：总文章数、今日新增、活跃用户、系统负载
- `UserTable`：用户列表、角色切换、状态管理
- `SourceHealthTable`：各信源健康状态（抓取成功率、错误率）
- `QueueStatus`：Celery 任务队列状态

---

## 第四部分：后端层设计

### 4.1 服务架构

采用**单体应用架构**，五个内部模块通过 Redis 队列通信（不是进程间直接调用）：

```
┌──────────────────────────────────────────────────────────┐
│                     FastAPI 应用                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 调度引擎  │  │ 内容处理  │  │ AI分析引擎│              │
│  │ Scheduler│  │ Processor │  │ Analyzer │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │             │                      │
│  ┌──────────┐  ┌──────────┐                               │
│  │ 策略引擎  │  │ 用户服务  │                              │
│  │ Strategy │  │  Auth    │                              │
│  └──────────┘  └──────────┘                               │
└──────────────────────────────────────────────────────────┘
                    ↓ Redis 队列
              ┌─────────────────┐
              │  Celery Workers  │
              │  (可水平扩展)    │
              └─────────────────┘
```

**初期简化：** 信源少于 30 个时，调度器直接 `await` 异步任务，跳过 Celery 队列。等需要并发控制和失败重试时再接入 Celery，只改提交方式，不改业务逻辑。

### 4.2 完整数据流

```
抓取触发
    │
    ▼
调度引擎 (Scheduler) ──→ Redis 队列 ──→ Celery Worker
    │                                    │
    │                                    ▼
    │                            内容处理器 (Processor)
    │                                    │
    │                                    ▼
    │                            内容解析 + 去重 (content_hash)
    │                                    │
    │                               ┌─────┴─────┐
    │                               ▼           ▼
    │                          [新内容]    [已存在-跳过]
    │                               │
    │                               ▼
    │                         AI 分析引擎 (Analyzer)
    │                         via OpenRouter API
    │                               │
    │                               ▼
    │                         生成 hot_score + tags
    │                               │
    │                               ▼
    │                         策略引擎 (Strategy)
    │                         判断是否「低粉爆文」
    │                               │
    │                               ▼
    │                          PostgreSQL
    │                               │
    │                               ▼
    │                         推送通知 (SSE / 邮件)
    │
    ▼
缓存热榜数据 → Redis (TTL 5min)
```

### 4.3 API 接口设计

#### 认证模块 `/api/auth/`

| 方法 | 路径 | 描述 |
|------|------|------|
| `POST` | `/api/auth/register` | 用户注册（邮箱 + 密码） |
| `POST` | `/api/auth/login` | 登录，返回 JWT Token |
| `POST` | `/api/auth/logout` | 登出，使 Token 失效 |
| `POST` | `/api/auth/refresh` | 刷新 Token |
| `GET` | `/api/auth/me` | 获取当前用户信息 |
| `POST` | `/api/auth/oauth/github` | GitHub OAuth 登录 |
| `GET` | `/api/auth/oauth/github/callback` | GitHub OAuth 回调 |

#### 文章模块 `/api/articles/`

| 方法 | 路径 | 描述 |
|------|------|------|
| `GET` | `/api/articles` | 列表（分页 + 筛选 + 搜索） |
| `GET` | `/api/articles/:id` | 详情 |
| `GET` | `/api/articles/trending` | 低粉爆文列表（策略筛选） |
| `GET` | `/api/articles/stats` | 统计数据（今日/本周/本月） |

**Query 参数：**

```
page=1&pageSize=20
&source=twitter,rss              # 信源类型过滤
&timeRange=today|week|month      # 时间范围
&sort=hot|time                   # 排序
&q=keyword                       # 搜索
```

#### 信源模块 `/api/sources/`

| 方法 | 路径 | 描述 |
|------|------|------|
| `GET` | `/api/sources` | 列表 |
| `POST` | `/api/sources` | 创建信源 |
| `PUT` | `/api/sources/:id` | 更新信源 |
| `PATCH` | `/api/sources/:id/toggle` | 启禁用切换 |
| `DELETE` | `/api/sources/:id` | 删除信源 |
| `POST` | `/api/sources/:id/test` | 测试抓取（手动触发） |

**信源类型 `config` 示例：**

```json
// Nitter 信源（无需 API Key）
{
  "type": "netter",
  "username": "ylee"
}

// RSS 信源
{
  "type": "rss",
  "feed_url": "https://example.com/feed.xml"
}

// X 账号信源
{
  "type": "twitter",
  "account": "@karpathy"
}

// GitHub Release 信源
{
  "type": "github",
  "org": "openai",
  "repo": "chatgpt-release",
  "event": "release"
}
```

#### 策略模块 `/api/strategies/`

| 方法 | 路径 | 描述 |
|------|------|------|
| `GET` | `/api/strategies` | 列表（含版本历史） |
| `GET` | `/api/strategies/active` | 当前激活策略 |
| `POST` | `/api/strategies` | 创建新策略 |
| `PUT` | `/api/strategies/:id` | 更新策略（生成新版本） |
| `PATCH` | `/api/strategies/:id/activate` | 激活指定版本 |
| `GET` | `/api/strategies/:id/history` | 版本历史 |

#### 收藏模块 `/api/favorites/`

| 方法 | 路径 | 描述 |
|------|------|------|
| `GET` | `/api/favorites` | 用户收藏列表 |
| `POST` | `/api/favorites` | 收藏文章 |
| `DELETE` | `/api/favorites/:id` | 取消收藏 |
| `POST` | `/api/favorites/:id/tags` | 添加标签 |
| `DELETE` | `/api/favorites/:id/tags/:tagId` | 移除标签 |
| `GET` | `/api/tags` | 所有标签列表 |

#### 监控模块 `/api/monitor/`

| 方法 | 路径 | 描述 |
|------|------|------|
| `GET` | `/api/monitor/config` | 获取用户监控配置 |
| `PUT` | `/api/monitor/config` | 更新监控配置（关键词/账号） |
| `GET` | `/api/sse/monitor` | SSE 实时推送端点 |

#### 管理模块 `/api/admin/`

| 方法 | 路径 | 描述 |
|------|------|------|
| `GET` | `/api/admin/stats` | 系统统计 |
| `GET` | `/api/admin/users` | 用户列表 |
| `PATCH` | `/api/admin/users/:id` | 更新用户角色/状态 |
| `GET` | `/api/admin/queue` | 队列状态 |

### 4.4 任务调度策略

| 任务 | 调度方式 | 频率 |
|------|----------|------|
| RSS 抓取 | Celery Beat | 每 15 分钟 |
| Nitter 抓取 | Celery Beat | 每 5 分钟 |
| GitHub Release 抓取 | Celery Beat | 每 30 分钟 |
| AI 评分计算 | Celery Task（触发式） | 新文章入库时 |
| 热榜缓存刷新 | Celery Beat | 每 5 分钟 |
| 健康检查 | Celery Beat | 每小时 |
| SSE 心跳 | 后端定时任务 | 每 30 秒 |

---

## 第五部分：数据层设计

### 5.1 ERD 表结构

```
┌─────────────────┐     ┌─────────────────┐
│     users       │     │    sources       │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ email           │     │ name            │
│ password_hash   │     │ type            │
│ nickname        │     │ config (jsonb)   │
│ avatar_url      │     │ is_active       │
│ role            │     │ last_fetched_at │
│ push_config     │     │ created_by (FK) │
│ created_at      │     │ created_at      │
│ updated_at      │     │ updated_at      │
└────────┬────────┘     └─────────────────┘
         │                       │
         │              ┌────────┴────────┐
         │              │                 │
         ▼              ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    articles     │ │    bookmarks     │ │  monitor_config │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ id (PK)         │ │ id (PK)         │ │ id (PK)         │
│ source_id (FK)  │ │ user_id (FK)    │ │ user_id (FK)    │
│ title           │ │ article_id (FK) │ │ keywords (text) │
│ url             │ │ created_at      │ │ twitter_accounts│
│ summary         │ └────────┬────────┘ │ created_at      │
│ content_hash    │          │          │ updated_at      │
│ author          │          │          └─────────────────┘
│ hot_score       │          ▼
│ fan_count       │    ┌─────────────┐
│ engagement      │    │bookmark_tags│
│ is_low_fan_viral│    ├─────────────┤
│ tags (jsonb)    │    │bookmark_id(FK│
│ raw_metadata    │    │tag_id (FK)  │
│ fetched_at       │    │PRIMARY KEY  │
│ published_at     │    └─────────────┘
│ created_at      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   strategies    │     │   tags          │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ name            │     │ name            │
│ description     │     │ user_id (FK)    │
│ version         │     │ color           │
│ params (jsonb)  │     │ created_at      │
│ is_active       │     └─────────────────┘
│ created_by (FK) │
│ created_at      │
└─────────────────┘
```

### 5.2 表结构详细定义

#### `users` 用户表

```sql
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    nickname    VARCHAR(100),
    avatar_url  TEXT,
    role        VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    push_config JSONB DEFAULT '{"email": false, "sse": true}',
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
```

#### `sources` 信源表

```sql
CREATE TABLE sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    type            VARCHAR(50) NOT NULL CHECK (type IN ('rss', 'netter', 'twitter', 'github')),
    config          JSONB NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    last_fetched_at TIMESTAMP,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_sources_type ON sources(type);
CREATE INDEX idx_sources_active ON sources(is_active) WHERE is_active = TRUE;
```

#### `articles` 文章表

```sql
CREATE TABLE articles (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id        UUID REFERENCES sources(id),
    title            VARCHAR(1000) NOT NULL,
    url              TEXT NOT NULL,
    summary          TEXT,
    content_hash     VARCHAR(64) NOT NULL,
    author           VARCHAR(255),
    hot_score        FLOAT DEFAULT 0,
    fan_count        INTEGER DEFAULT 0,
    engagement       JSONB DEFAULT '{"likes": 0, "retweets": 0, "comments": 0}',
    is_low_fan_viral BOOLEAN DEFAULT FALSE,
    tags             JSONB DEFAULT '[]',
    raw_metadata     JSONB,
    fetched_at       TIMESTAMP DEFAULT NOW(),
    published_at     TIMESTAMP,
    created_at       TIMESTAMP DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_articles_content_hash ON articles(content_hash);
CREATE INDEX idx_articles_hot_score ON articles(hot_score DESC);
CREATE INDEX idx_articles_fetched_at ON articles(source_id, fetched_at DESC);
CREATE INDEX idx_articles_low_fan_viral ON articles(is_low_fan_viral) WHERE is_low_fan_viral = TRUE;
```

#### `bookmarks` 收藏表

```sql
CREATE TABLE bookmarks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    article_id  UUID NOT NULL REFERENCES articles(id),
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, article_id)
);
CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);
```

#### `bookmark_tags` 收藏标签关联表

```sql
CREATE TABLE bookmark_tags (
    bookmark_id  UUID REFERENCES bookmarks(id) ON DELETE CASCADE,
    tag_id       UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (bookmark_id, tag_id)
);
```

#### `tags` 标签表

```sql
CREATE TABLE tags (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    user_id     UUID NOT NULL REFERENCES users(id),
    color       VARCHAR(7) DEFAULT '#6366f1',
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, name)
);
```

#### `strategies` 精选策略表

```sql
CREATE TABLE strategies (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    version     INTEGER NOT NULL DEFAULT 1,
    params      JSONB NOT NULL,
    is_active   BOOLEAN DEFAULT FALSE,
    created_by  UUID REFERENCES users(id),
    created_at  TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_strategies_active ON strategies(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_strategies_name ON strategies(name, version DESC);
```

#### `monitor_config` 监控配置表

```sql
CREATE TABLE monitor_configs (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID UNIQUE NOT NULL REFERENCES users(id),
    keywords          TEXT[] DEFAULT '{}',
    twitter_accounts  TEXT[] DEFAULT '{}',
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW()
);
```

### 5.3 索引策略

| 索引 | 用途 | 备注 |
|------|------|------|
| `articles(content_hash)` | 去重（UNIQUE） | 核心去重索引 |
| `articles(hot_score DESC)` | 热榜排序 | 热榜读取走 Redis，但写入时用到 |
| `articles(source_id, fetched_at DESC)` | 按信源过滤时间线 | 最常用查询 |
| `articles(is_low_fan_viral)` | 低粉爆文筛选 | 布尔索引，仅索引 true 行 |
| `sources(is_active)` | 获取活跃信源 | 部分索引 |
| `strategies(is_active)` | 获取激活策略 | 部分索引 |

### 5.4 存储架构

| 存储 | 用途 | 说明 |
|------|------|------|
| **PostgreSQL** | 单一真相来源 | 所有业务数据，信源 config 用 jsonb 存储 |
| **Redis** | 读加速 + 队列 | 热榜数据缓存（TTL 5min）、Celery 消息队列、Token 黑名单 |
| **R2 / 本地** | 文件存储 | 文章图片、导出文件备份 |

### 5.5 去重策略

`articles.content_hash` 是去重核心：

1. 爬取完成后，对 `标题 + URL` 做 **SHA-256** 哈希
2. 写入前执行 `INSERT ... ON CONFLICT (content_hash) DO NOTHING`
3. 一行 SQL 解决幂等写入，无需单独去重服务
4. 未来可扩展为向量相似度去重（语义重复），接入向量数据库

---

## 第六部分：AI 服务设计（OpenRouter）

### 6.1 OpenRouter 集成方案

**为什么选 OpenRouter：**

- 一站式接入 Claude、GPT、Mistral 等多模型
- 统一 API 接口，按 token 计费
- 支持模型对比调用

**基础封装：**

```python
# lib/openrouter.py
from openrouter import OpenRouter

client = OpenRouter(api_key=os.environ["OPENROUTER_API_KEY"])

async def score_article(title: str, content: str, metadata: dict) -> dict:
    response = await client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {
                "role": "system",
                "content": """你是一个专业的AI内容分析师。请分析以下文章并给出评分。
评分维度：1-10分。
- 内容质量（深度、原创性）
- 话题热度（时效性、行业关注度）
- 传播潜力（易懂程度、话题延展性）

请返回JSON格式：{"quality": 7.5, "hotness": 8.0, "spread_potential": 6.5, "reasoning": "..."}"""
            },
            {
                "role": "user",
                "content": f"标题：{title}\\n\\n内容摘要：{content[:500]}\\n\\n元数据：{metadata}"
            }
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
```

### 6.2 低粉爆文识别策略

**核心公式：**

```
爆文指数 = (点赞 * 1 + 转发 * 3 + 评论 * 2) / 粉丝数 * 1000
```

**AI 辅助判断：**

```python
# 低粉爆文判断伪代码
def is_low_fan_viral(article: Article, strategy: Strategy) -> bool:
    params = strategy.params

    # 基础条件
    fan_threshold = params.get("max_fan_count", 10000)
    engagement_threshold = params.get("min_engagement", 100)
    viral_score_threshold = params.get("min_viral_score", 5.0)

    # 条件1：粉丝数低于阈值
    if article.fan_count > fan_threshold:
        return False

    # 条件2：互动数超过阈值
    total_engagement = (
        article.engagement.get("likes", 0) +
        article.engagement.get("retweets", 0) * 3 +
        article.engagement.get("comments", 0) * 2
    )
    if total_engagement < engagement_threshold:
        return False

    # 条件3：爆文指数
    viral_score = total_engagement / (article.fan_count + 1) * 1000
    if viral_score < viral_score_threshold:
        return False

    # 条件4：AI 质量评分
    ai_score = article.ai_scores or {}
    if ai_score.get("quality", 0) < params.get("min_quality_score", 6.0):
        return False

    return True
```

### 6.3 策略参数结构（jsonb）

```json
{
  "name": "低粉爆文 v1",
  "max_fan_count": 10000,
  "min_engagement": 100,
  "min_viral_score": 5.0,
  "min_quality_score": 6.0,
  "hotness_boost_threshold": 7.5,
  "exclude_keywords": ["广告", "推广", "抽奖"],
  "target_domains": ["arxiv.org", "github.com"]
}
```

---

## 第七部分：部署方案

### 7.1 Docker Compose 部署

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ai_news:password@db:5432/ai_news
      - REDIS_URL=redis://redis:6379/0
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_ORIGINS=http://localhost:3000
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery_worker:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://ai_news:password@db:5432/ai_news
      - REDIS_URL=redis://redis:6379/0
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery_beat:
    build: ./backend
    command: celery -A app.celery beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://ai_news:password@db:5432/ai_news
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=ai_news
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ai_news
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    restart: unless-stopped

volumes:
  pgdata:
  redisdata:
```

### 7.2 环境变量清单

**后端 (.env)**

```
# 数据库
DATABASE_URL=postgresql://ai_news:password@localhost:5432/ai_news

# Redis
REDIS_URL=redis://localhost:6379/0

# 安全
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时

# AI 服务
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# 爬虫（可选）
TWITTER_BEARER_TOKEN=xxxxx
GITHUB_TOKEN=ghp_xxxxx

# 文件存储（可选）
R2_ACCOUNT_ID=xxxxx
R2_ACCESS_KEY_ID=xxxxx
R2_SECRET_ACCESS_KEY=xxxxx
R2_BUCKET_NAME=ai-news
```

**前端 (.env.local)**

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 7.3 数据库迁移

使用 Alembic 进行数据库版本管理：

```bash
# 初始化
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "init tables"

# 执行迁移
alembic upgrade head
```

### 7.4 Oracle Cloud 免费机部署建议

单台 Oracle Cloud 免费机（2 OCPU + 1GB RAM）配置：

| 服务 | 资源分配 |
|------|----------|
| PostgreSQL | 共享，预留 256MB |
| Redis | 共享，预留 128MB |
| FastAPI | 1 核心 |
| Celery Worker | 1 核心 |
| Celery Beat | 共享进程 |

**性能目标：** 支撑 10-20 个信源，1000+ 文章/天。

---

## 第八部分：开发计划

### Phase 1：项目初始化（第 1-2 天）

- [x] 初始化 Next.js 项目，配置 Tailwind + shadcn/ui
- [x] 初始化 FastAPI 项目，配置 SQLAlchemy + Alembic
- [x] 配置 Docker Compose 本地开发环境
- [x] 创建 PostgreSQL 数据库，完成表迁移
- [x] 配置 OpenRouter API 连接

### Phase 2：核心功能（第 3-7 天）

- [x] 完成用户认证（注册/登录/JWT + GitHub OAuth）
- [x] 实现信源管理 CRUD（RSS 爬取优先）
- [x] 实现文章列表 API + 前端展示
- [x] 实现收藏功能（添加/标签/过滤）

### Phase 3：AI 增强（第 8-12 天）

- [x] 接入 Celery + Redis 任务队列
- [x] 实现定时抓取调度
- [x] 实现 OpenRouter AI 评分
- [x] 实现低粉爆文筛选
- [x] 实现精选策略管理

### Phase 4：实时功能（第 13-16 天）

- [x] 实现 X 监控配置
- [x] 实现 SSE 实时推送
- [x] 实现 Twitter API 爬取

### Phase 5：完善与上线（第 17-20 天）

- [x] 完善 Docker Compose 配置
- [x] 编写部署脚本和文档
- [x] 数据库迁移配置 (Alembic)
- [ ] 后台管理面板
- [ ] 性能优化与测试
- [ ] 部署上线

---

*文档结束*
