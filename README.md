# AI News Aggregator - AI 新闻自动抓取网站

一个自动抓取、分发与精选 AI 领域资讯的平台，帮助用户高效发现低粉爆文与高价值内容。

## 功能特性

- **热点资讯** - 聚合多个来源的 AI 新闻，按热度/时间排序
- **低粉爆文** - AI 驱动的低粉丝爆款内容发现
- **X 监控** - Twitter/X 关键词和账号实时监控推送
- **收藏管理** - 文章收藏、标签分类
- **信源管理** - 支持 RSS / Twitter / GitHub Release 多种信源
- **精选策略** - 可配置的 AI 评分策略，支持版本管理
- **用户管理** - 多角色权限，支持 OAuth 登录

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | Next.js 15 + React 19 + TypeScript |
| UI | shadcn/ui + Tailwind CSS |
| 状态管理 | TanStack Query + Zustand |
| 后端 | FastAPI + Python |
| 任务队列 | Celery + Redis |
| 数据库 | PostgreSQL 16 |
| AI 服务 | OpenRouter (Claude/GPT 等) |

## 快速开始

### 环境要求

- Docker 和 Docker Compose
- Node.js 20+
- Python 3.11+

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd ai_news
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 必须配置:
# - OPENROUTER_API_KEY: 从 https://openrouter.ai/keys 获取
# - SECRET_KEY: 生成随机密钥
```

### 3. 一键启动（Docker）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务启动后：

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 4. 本地开发

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload
```

## 项目结构

```
ai_news/
├── frontend/               # Next.js 前端
│   ├── src/
│   │   ├── app/           # App Router 页面
│   │   │   ├── (main)/     # 主布局组
│   │   │   │   ├── page.tsx           # 首页/热点资讯
│   │   │   │   ├── trending/          # 低粉爆文
│   │   │   │   ├── monitor/           # X监控
│   │   │   │   ├── favorites/         # 收藏
│   │   │   │   ├── sources/           # 信源管理
│   │   │   │   └── strategies/         # 策略管理
│   │   │   ├── auth/        # 认证页面
│   │   │   ├── admin/       # 后台管理
│   │   │   └── api/         # API 路由
│   │   ├── components/      # React 组件
│   │   │   ├── ui/          # shadcn/ui 基础组件
│   │   │   └── layout/      # 布局组件
│   │   ├── stores/          # Zustand 状态
│   │   ├── lib/             # 工具函数
│   │   └── types/          # TypeScript 类型
│   └── package.json
│
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic schema
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   │   ├── crawler.py  # 爬虫服务
│   │   │   ├── openrouter.py # AI 服务
│   │   │   └── celery_tasks.py # 定时任务
│   │   ├── main.py         # FastAPI 入口
│   │   └── celery_app.py   # Celery 配置
│   ├── alembic/            # 数据库迁移
│   └── requirements.txt
│
├── docker-compose.yml      # Docker Compose 配置
├── .env.example            # 环境变量模板
└── SPEC.md                 # 完整设计文档
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看完整的 Swagger API 文档。

### 主要接口

| 模块 | 端点 | 描述 |
|------|------|------|
| 认证 | `POST /api/auth/register` | 用户注册 |
| 认证 | `POST /api/auth/login` | 用户登录 |
| 文章 | `GET /api/articles` | 获取文章列表 |
| 文章 | `GET /api/articles/trending` | 获取低粉爆文 |
| 信源 | `GET /api/sources` | 获取信源列表 |
| 信源 | `POST /api/sources` | 创建信源 |
| 收藏 | `GET /api/favorites` | 获取收藏 |
| 收藏 | `POST /api/favorites` | 添加收藏 |
| 策略 | `GET /api/strategies` | 获取策略列表 |
| 策略 | `POST /api/strategies` | 创建策略 |

## 开发指南

### 添加新的 shadcn/ui 组件

```bash
cd frontend
npx shadcn@latest add [component-name]
```

### 创建新的数据库迁移

```bash
cd backend
# 编辑模型后创建迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head
```

### 添加新的定时任务

在 `backend/app/services/celery_tasks.py` 中添加任务函数，并在 `schedule.py` 中配置调度。

## 部署

### Docker Compose 生产部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose -f docker-compose.yml up -d
```

### 环境变量配置

生产环境必须设置以下变量：

```bash
# 安全
SECRET_KEY=<强随机密钥>

# 数据库（生产应使用外部 PostgreSQL）
DATABASE_URL=postgresql://user:pass@host:5432/db

# AI 服务
OPENROUTER_API_KEY=<你的API密钥>

# CORS（生产域名）
ALLOWED_ORIGINS=https://your-domain.com
```

## License

MIT
