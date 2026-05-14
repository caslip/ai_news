# AI News 日志系统使用手册

本文档描述了 AI News Aggregator 项目的日志系统架构和用法。

---

## 目录

- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [日志格式](#日志格式)
- [访问 Grafana](#访问-grafana)
- [日志查询](#日志查询)
- [环境变量配置](#环境变量配置)
- [常见问题](#常见问题)

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           日志系统架构                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  FastAPI Backend │      │ Celery Worker   │      │  Celery Beat    │
│  (Uvicorn)      │      │                 │      │                 │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                          │                          │
         │  JSON 日志                 │  JSON 日志               │  JSON 日志
         ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Python JSON Logger                                   │
│  {                                                                   │
│    "timestamp": "2024-01-01T12:00:00Z",                              │
│    "level": "INFO",                                                   │
│    "message": "...",                                                  │
│    "service": "ai-news-backend",                                      │
│    "request_id": "uuid-string"                                        │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   /app/logs/*.log       │
                    │   (Docker Volume)       │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   Promtail Agent        │
                    │   (日志收集器)           │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   Loki Server :3100    │
                    │   (日志存储)             │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   Grafana :3200         │
                    │   (可视化面板)           │
                    └─────────────────────────┘
```

### 组件说明

| 组件 | 端口 | 说明 |
|------|------|------|
| **Loki** | 3100 | Grafana 生态的日志聚合服务，存储日志数据 |
| **Grafana** | 3200 | 可视化面板，用于查询和展示日志 |
| **Promtail** | 9080 | Loki 的代理客户端，负责收集日志文件 |
| **Python App** | - | 使用 python-json-logger 输出 JSON 格式日志 |

---

## 快速开始

### 1. 启动日志服务

确保 Docker 和 Docker Compose 已安装，然后运行：

```bash
# 启动所有服务（包括日志系统）
docker-compose up -d

# 查看日志服务状态
docker-compose ps
```

服务启动顺序：
1. PostgreSQL、Redis（基础设施）
2. Backend、Celery（应用服务）
3. Loki（等待就绪）
4. Grafana、Promtail（观察服务）

### 2. 验证日志收集

```bash
# 查看 Promtail 日志
docker-compose logs promtail

# 查看 Loki 状态
curl http://localhost:3100/ready

# 查看 Grafana 状态
curl http://localhost:3200/api/health
```

### 3. 访问 Grafana

打开浏览器访问：http://localhost:3200

- **用户名**: `admin`
- **密码**: `admin`（可在环境变量中修改）

---

## 日志格式

### JSON 日志示例

```json
{
  "timestamp": "2024-01-15T10:30:45.123456+00:00",
  "level": "INFO",
  "message": "Request completed",
  "module": "app.middleware.logging_middleware",
  "function": "dispatch",
  "line": 45,
  "service": "ai-news-backend",
  "service_type": "api",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "GET",
  "path": "/api/news",
  "status_code": 200,
  "duration_ms": 45.23
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | string | ISO 8601 格式的时间戳 (UTC) |
| `level` | string | 日志级别: DEBUG, INFO, WARNING, ERROR |
| `message` | string | 日志消息 |
| `module` | string | Python 模块名 |
| `function` | string | 函数名 |
| `line` | int | 代码行号 |
| `service` | string | 服务名称 |
| `service_type` | string | 服务类型: api, celery |
| `request_id` | string | 请求唯一标识符 (API 服务) |
| `task_id` | string | Celery 任务 ID (Celery 服务) |
| `task_name` | string | Celery 任务名称 (Celery 服务) |
| `method` | string | HTTP 方法 (请求日志) |
| `path` | string | 请求路径 (请求日志) |
| `status_code` | int | HTTP 响应状态码 (请求日志) |
| `duration_ms` | float | 请求耗时 (毫秒) (请求日志) |

### 日志级别

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| DEBUG | 调试信息 | 开发时追踪详细流程 |
| INFO | 一般信息 | 正常操作记录，如请求完成、任务开始 |
| WARNING | 警告 | 潜在问题但不影响功能，如配置缺失使用默认值 |
| ERROR | 错误 | 操作失败，如数据库连接错误、API 调用失败 |

---

## 访问 Grafana

### 仪表盘说明

预配置的仪表盘 "AI News 日志系统" 包含以下面板：

1. **日志级别分布** - 显示各日志级别的数量统计
2. **日志产生速率** - 显示每秒产生的日志数量
3. **日志流** - 实时日志列表，支持筛选

### 筛选功能

- **服务筛选**: 选择查看哪个服务的日志
  - `ai-news-backend`: FastAPI 主服务
  - `ai-news-celery`: Celery 任务服务
- **日志级别筛选**: 选择查看哪些级别的日志
- **时间范围**: 支持相对时间（如 "最近 1 小时"）和绝对时间

### 常用操作

1. **搜索特定请求的日志**
   - 在日志流中搜索 `request_id: <your-request-id>`
   - 请求 ID 可以在响应头 `X-Request-ID` 中找到

2. **查看错误日志**
   - 筛选 `level: ERROR`
   - 可以看到所有错误和异常堆栈

3. **查看 Celery 任务日志**
   - 筛选 `service: ai-news-celery`
   - 可以看到任务执行详情

---

## 日志查询

### LogQL 查询语法

Grafana 使用 LogQL 查询语言，以下是常用查询示例：

#### 基础查询

```logql
# 查看所有日志
{service=~"ai-news-backend|ai-news-celery"}

# 查看错误日志
{service="ai-news-backend"} |= "level":"ERROR"

# 查找包含关键词的日志
{service="ai-news-backend"} |= "database"
```

#### 筛选表达式

```logql
# 排除某关键词
{service="ai-news-backend"} != "health check"

# 正则匹配
{service="ai-news-backend"} |~ "user_\\d+"

# 多条件组合
{service="ai-news-backend"} | json | level="INFO" | duration_ms > 100
```

#### 统计查询

```logql
# 每分钟错误数量
sum by (level) (count_over_time({service="ai-news-backend"}[1m]))

# P99 响应时间（如果有 duration_ms 字段）
quantile_over_time(0.99, {service="ai-news-backend"} | json | unwrap duration_ms [5m])
```

### Python 代码中使用日志

```python
from app.logging_config import get_logger

# 创建 logger
logger = get_logger(__name__)

# 记录日志
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志", extra={"error_code": 500})

# 带请求上下文的日志
from app.middleware import get_logger_with_request_id
request_logger = get_logger_with_request_id(__name__)
request_logger.info("带 request_id 的日志")
```

---

## 环境变量配置

### 日志相关环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `LOG_LEVEL` | `INFO` | 日志级别: DEBUG, INFO, WARNING, ERROR |
| `GRAFANA_PORT` | `3200` | Grafana 访问端口 |
| `GRAFANA_USER` | `admin` | Grafana 用户名 |
| `GRAFANA_PASSWORD` | `admin` | Grafana 密码 |

### 在 .env 文件中配置

```env
# 日志配置
LOG_LEVEL=INFO
GRAFANA_PORT=3200
GRAFANA_USER=admin
GRAFANA_PASSWORD=your-secure-password
```

### 修改日志级别

```bash
# 临时修改（仅当前会话）
export LOG_LEVEL=DEBUG

# 或在启动时指定
LOG_LEVEL=DEBUG docker-compose up -d

# 或在 .env 文件中永久修改
```

---

## 常见问题

### Q: Grafana 显示 "No data"

**可能原因**:
1. 日志服务尚未启动完成
2. Promtail 还未收集到日志
3. 时间范围设置不当

**解决方案**:
```bash
# 1. 等待 30 秒让日志收集
sleep 30

# 2. 检查 Promtail 是否正常运行
docker-compose logs promtail

# 3. 扩大时间范围（如改为 "最近 6 小时"）
```

### Q: 如何查看特定请求的日志？

**方法 1**: 使用 Grafana 搜索
1. 在日志流面板中
2. 搜索框输入: `request_id: <your-request-id>`

**方法 2**: 从响应头获取
1. 发送请求时查看响应头
2. 响应中包含 `X-Request-ID` 字段

### Q: 日志文件在哪里？

日志文件存储在 Docker volume 中：
- Backend 日志: `/app/logs/app.log`
- Celery 日志: `/app/logs/celery.log`

本地映射到 `logs/` 目录。

### Q: 如何调整日志保留期限？

Loki 默认配置不限制日志保留。如需限制，可以在 docker-compose.yml 中为 Loki 添加配置：

```yaml
loki:
  command: -config.file=/etc/loki/config.yaml -storage.config.tsdb.retention-period=672h
```

### Q: Grafana 密码忘记了怎么办？

```bash
# 重置 Grafana 密码（需要进入容器）
docker exec -it ai-news-grafana grafana-cli admin reset-admin-password newpassword
```

### Q: 如何增加更多日志字段？

修改 `backend/app/logging_config.py` 中的 `CustomJsonFormatter` 类：

```python
def add_fields(self, log_record, record, message_dict):
    super().add_fields(log_record, record, message_dict)
    # 添加自定义字段
    log_record["custom_field"] = "value"
```

---

## 维护命令

```bash
# 重启日志服务
docker-compose restart loki grafana promtail

# 查看 Loki 日志
docker-compose logs -f loki

# 查看 Promtail 日志（调试收集问题）
docker-compose logs -f promtail

# 清理 Loki 数据（谨慎使用）
docker-compose down
docker volume rm ai-news_lokidata
docker-compose up -d

# 更新日志系统版本
docker-compose pull loki grafana promtail
docker-compose up -d
```

---

## 技术栈

- **日志格式**: python-json-logger
- **日志收集**: Promtail 2.9.4
- **日志存储**: Loki 2.9.4
- **可视化**: Grafana 10.2.3

---

如有问题，请提交 Issue 或联系维护者。
