# AI Writer

AI 内容生成平台，基于 Next.js 16 + TypeScript + Tailwind CSS v4 + shadcn/ui 构建。

## 技术栈

- **框架**: Next.js 16.2.1 (App Router, RSC)
- **语言**: TypeScript 5
- **样式**: Tailwind CSS v4 + shadcn/ui (Radix UI primitives)
- **状态**: Zustand + TanStack Query v5
- **表单**: React Hook Form + Zod
- **图标**: Lucide React
- **字体**: Geist Sans + Geist Mono

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发环境

```bash
npm run dev
```

访问 http://localhost:3002

### 生产构建

```bash
npm run build
npm run start
```

## 环境变量

复制 `.env.local.example` 为 `.env.local`，配置后端 API 地址：

```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## 主要功能

- **文章生成**: 输入素材或 URL，AI 生成优质内容
- **草稿管理**: 查看、编辑、导出、删除草稿
- **模板库**: 预设写作模板快速开始
- **写作偏好**: 自定义默认写作风格和语气

## 目录结构

```
frontend_writer/
├── src/
│   ├── app/                 # Next.js App Router 页面
│   │   ├── (main)/          # 带侧边栏的页面组
│   │   └── auth/            # 登录/注册页面
│   ├── components/
│   │   ├── ui/              # shadcn/ui 组件
│   │   ├── layout/          # 布局组件
│   │   └── writer/          # 业务组件
│   ├── hooks/               # React Hooks
│   ├── lib/                 # 工具函数和 API
│   └── stores/              # Zustand 状态管理
├── public/
├── package.json
├── tailwind.config.js
└── next.config.ts
```

## Docker 部署

```bash
# 开发环境
docker-compose up frontend-writer

# 生产环境
docker-compose -f docker-compose.prod.yml up frontend-writer
```

## License

MIT
