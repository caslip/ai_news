# AI News API 测试教程

## 快速开始

### 1. 导入 Postman 集合

1. 打开 Postman
2. 点击左上角 **Import** 按钮
3. 选择文件 `AI_News_API_Collection.json` 或拖拽到 Postman
4. 集合导入成功后，你会看到以下结构：

```
AI News API 测试
├── 1. 认证
│   └── 登录
├── 2. 信源管理
│   ├── 获取 Twitter 信源列表
│   ├── 测试信源爬取
│   └── 创建 Twitter 信源
└── 3. 文章查询
    └── 获取 Twitter 推文列表
```

### 2. 登录获取 Token

1. 展开 **1. 认证** 文件夹
2. 点击 **登录** 请求
3. 点击 **Send** 按钮发送请求
4. 登录成功后：
   - Token 会自动保存到变量 `access_token`
   - 控制台会打印 Token 信息

**测试账号**：
- Email: `test@example.com`
- Password: `Test123456`

### 3. 测试 Twitter 信源爬取

#### 方式一：创建新信源并测试

1. 展开 **2. 信源管理**
2. 点击 **创建 Twitter 信源**
3. 点击 **Send** - 创建 karpathy 信源
4. 复制返回的 `id` 字段
5. 点击 **测试信源爬取**
6. 将 URL 中的 `{source_id}` 替换为刚才复制的 ID
7. 点击 **Send** - 测试爬取

#### 方式二：测试已有信源

1. 点击 **获取 Twitter 信源列表**
2. 点击 **Send** - 查看所有 Twitter 信源
3. 复制需要的信源 `id`
4. 点击 **测试信源爬取**
5. 替换 `{source_id}` 并发送

### 4. 查询推文

1. 展开 **3. 文章查询**
2. 点击 **获取 Twitter 推文列表**
3. 点击 **Send**

支持参数：
- `source_type`: `twitter`, `netter` 或 `twitter,netter`
- `sort`: `hot`, `latest`, `popular`
- `time_range`: `day`, `week`, `month`
- `page_size`: 每页数量

---

## curl 命令示例

### 登录

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'
```

返回示例：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "bf7f643e-f659-4a74-b29e-a2abad365897",
    "email": "test@example.com",
    "nickname": "testuser"
  }
}
```

### 获取 Twitter 信源列表

```bash
curl -X GET "http://localhost:8000/api/sources?type=twitter" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 测试信源爬取

```bash
curl -X POST "http://localhost:8000/api/sources/{source_id}/test" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 创建 Twitter 信源

```bash
curl -X POST http://localhost:8000/api/sources \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Andrej Karpathy (Twitter)",
    "type": "twitter",
    "config": {
      "account": "karpathy"
    },
    "is_active": true
  }'
```

### 获取推文列表

```bash
curl -X GET "http://localhost:8000/api/articles?source_type=twitter,netter&sort=hot&page_size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## API 端点汇总

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/register` | 用户注册 |
| GET | `/api/sources` | 获取信源列表 |
| POST | `/api/sources` | 创建信源 |
| GET | `/api/sources/{id}` | 获取信源详情 |
| POST | `/api/sources/{id}/test` | 测试信源爬取 |
| DELETE | `/api/sources/{id}` | 删除信源 |
| GET | `/api/articles` | 获取文章列表 |

---

## 常见问题

### Q: 返回 401 Unauthorized

**原因**：未携带认证 Token 或 Token 过期

**解决**：
1. 重新执行登录请求获取新 Token
2. 确保请求头包含 `Authorization: Bearer {token}`

### Q: 返回 404 Not Found

**原因**：信源 ID 不存在

**解决**：
1. 先执行获取信源列表，确认 ID 正确
2. 或创建新信源获取新 ID

### Q: Token 有效期

**答案**：24 小时

Token 过期后需要重新登录获取。

### Q: Nitter 爬虫说明

系统使用 [Nitter](https://nitter.net/) RSS 获取 Twitter 推文，**无需 Twitter API Key**。

支持的信源类型：
- `twitter`: 使用 Nitter RSS 获取，保留原始类型
- `netter`: 使用 Nitter RSS 获取
