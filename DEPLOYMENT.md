# AI News Aggregator - 部署检查清单

## 部署前检查

### 1. 环境变量配置
```bash
# 复制并配置环境变量
cp .env.example .env

# 必填项
OPENROUTER_API_KEY=sk-or-v1-xxxxx    # OpenRouter API Key
SECRET_KEY=your-super-secret-key    # JWT 密钥 (至少 32 字符)
DATABASE_URL=postgresql://...        # PostgreSQL 连接

# 可选项
TWITTER_BEARER_TOKEN=xxxxx          # Twitter API Token
GITHUB_TOKEN=ghp_xxxxx              # GitHub Token
```

### 2. Docker 环境
- [ ] Docker 已安装 (v20.10+)
- [ ] Docker Compose 已安装 (v2.0+)
- [ ] Docker daemon 正在运行

### 3. 代码构建测试
```bash
# 本地构建测试
cd frontend && npm run build
cd ../backend && python -m pytest tests/ -v
```

## 生产部署

### 使用 Docker Compose (推荐)

```bash
# 1. 配置环境变量
vim .env

# 2. 启动服务
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. 检查服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f backend
```

### 手动部署

**后端:**
```bash
cd backend
pip install -r requirements.txt
python -m alembic upgrade head
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

**前端:**
```bash
cd frontend
npm install
npm run build
npm run start
```

**Celery Workers:**
```bash
celery -A app.celery_app worker --loglevel=info --concurrency=2
celery -A app.celery_app beat --loglevel=info
```

## 部署后验证

### 健康检查
- [ ] Frontend: http://localhost:3000
- [ ] Backend: http://localhost:8000/api/health
- [ ] API Docs: http://localhost:8000/docs

### 功能测试
- [ ] 用户注册/登录
- [ ] 文章列表加载
- [ ] 信源添加和测试
- [ ] 收藏功能
- [ ] SSE 连接 (可选)

## Nginx 生产配置

```nginx
# /etc/nginx/sites-available/ai-news
upstream frontend {
    server 127.0.0.1:3000;
}

upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_buffering off;
    }
}
```

## 故障排除

### 数据库迁移失败
```bash
docker-compose exec backend python -m alembic downgrade -1
docker-compose exec backend python -m alembic upgrade head
```

### Celery 任务不执行
```bash
# 检查 Worker 状态
docker-compose logs celery_worker

# 重启 Worker
docker-compose restart celery_worker celery_beat
```

### 常见问题
1. **端口冲突**: 检查 3000, 8000, 5432, 6379 端口
2. **数据库连接**: 确认 DATABASE_URL 格式正确
3. **CORS 错误**: 检查 ALLOWED_ORIGINS 配置
