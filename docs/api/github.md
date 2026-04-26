# GitHub Trending API

> GitHub Trending 数据获取相关接口

## 基础信息

| 项目 | 说明 |
|------|------|
| Base Path | `/api/github` |
| 认证方式 | 不需要 |

---

## 获取 GitHub Trending

### GitHub 热门仓库

**请求方法** `GET /api/github/trending`

**描述**: 获取 GitHub Trending 页面的热门仓库列表

**认证**: 不需要

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `language` | string | 否 | 空 | 编程语言过滤，如 `python`, `typescript`, `javascript` |
| `since` | string | 否 | daily | 时间范围：`daily`（今日）/ `weekly`（本周）/ `monthly`（本月） |
| `limit` | integer | 否 | 10 | 返回数量（1-50） |

**请求示例**:

```bash
# 获取今日 Python 热门项目
GET /api/github/trending?language=python&since=daily&limit=10

# 获取本周 TypeScript 热门项目
GET /api/github/trending?language=typescript&since=weekly&limit=20

# 获取本月 JavaScript 热门项目
GET /api/github/trending?language=javascript&since=monthly&limit=50
```

**响应示例** (200 OK):

```json
{
  "repos": [
    {
      "rank": 1,
      "owner": "openai",
      "repo": "openai-agents-sdk",
      "url": "https://github.com/openai/openai-agents-sdk",
      "description": "OpenAI Agents SDK - Build agentic applications with OpenAI",
      "language": "Python",
      "language_color": "#3572A5",
      "stars": 12500,
      "stars_today": 3420,
      "forks": 1200,
      "built_by": ["alice", "bob", "charlie"]
    },
    {
      "rank": 2,
      "owner": "anthropics",
      "repo": "anthropic-cookbook",
      "url": "https://github.com/anthropics/anthropic-cookbook",
      "description": "A collection of notebooks/recipes for building with Anthropic models",
      "language": "Jupyter Notebook",
      "language_color": "#DA5B0B",
      "stars": 8900,
      "stars_today": 2100,
      "forks": 850,
      "built_by": ["david", "eve"]
    },
    {
      "rank": 3,
      "owner": "mistralai",
      "repo": "mistral-finetune",
      "url": "https://github.com/mistralai/mistral-finetune",
      "description": "Lightweight fine-tuning framework for Mistral models",
      "language": "Python",
      "language_color": "#3572A5",
      "stars": 6200,
      "stars_today": 1580,
      "forks": 430,
      "built_by": ["frank"]
    }
  ],
  "fetched_at": "2024-01-15T10:30:00Z",
  "language": "python",
  "since": "daily"
}
```

**响应说明**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `repos` | array | 仓库列表 |
| `fetched_at` | string | 数据获取时间（ISO 格式） |
| `language` | string \| null | 筛选的编程语言 |
| `since` | string | 时间范围 |

### GitHubTrendingRepo 字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `rank` | integer | 排名 |
| `owner` | string | 仓库所有者 |
| `repo` | string | 仓库名称 |
| `url` | string | 仓库 URL |
| `description` | string | 仓库描述 |
| `language` | string \| null | 编程语言 |
| `language_color` | string \| null | 语言颜色（十六进制） |
| `stars` | integer | 总 Star 数 |
| `stars_today` | integer | 今日新增 Star 数 |
| `forks` | integer | Fork 数 |
| `built_by` | array | 主要贡献者用户名列表 |

---

## 常见编程语言

以下是 GitHub Trending 支持的常见编程语言：

| 语言 | 参数值 | 语言 | 参数值 |
|------|--------|------|--------|
| Python | `python` | TypeScript | `typescript` |
| JavaScript | `javascript` | Java | `java` |
| Go | `go` | Rust | `rust` |
| C++ | `c++` | C | `c` |
| Ruby | `ruby` | Swift | `swift` |
| Kotlin | `kotlin` | Dart | `dart` |
| Vue | `vue` | CSS | `css` |
| HTML | `html` | Shell | `shell` |
| Jupyter Notebook | `jupyter-notebook` | - | - |

---

## 使用示例

### JavaScript 示例

```javascript
// 获取今日 Python 热门项目
async function getPythonTrending() {
  const response = await fetch(
    'http://localhost:8000/api/github/trending?language=python&since=daily&limit=10'
  );
  const data = await response.json();

  console.log('今日 Python 热门项目:');
  data.repos.forEach(repo => {
    console.log(`${repo.rank}. ${repo.owner}/${repo.repo}`);
    console.log(`   Stars: ${repo.stars} (+${repo.stars_today} today)`);
    console.log(`   Description: ${repo.description}`);
  });
}
```

### Python 示例

```python
import httpx

async def get_trending(language: str = "python", since: str = "daily"):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/github/trending",
            params={"language": language, "since": since, "limit": 10}
        )
        return response.json()

# 使用示例
import asyncio

async def main():
    data = await get_trending("typescript", "weekly")
    print(f"本周 TypeScript 热门项目:")
    for repo in data["repos"]:
        print(f"- {repo['owner']}/{repo['repo']}: {repo['description']}")

asyncio.run(main())
```

---

## 数据说明

### 数据来源

GitHub Trending 数据直接从 GitHub 官网（github.com/trending）抓取，确保数据的实时性。

### 更新频率

建议客户端每 15-30 分钟刷新一次数据，以获取最新的 Trending 信息。

### 注意事项

1. **请求频率限制**：请勿频繁请求，建议添加本地缓存
2. **数据延迟**：由于直接从 GitHub 抓取，可能存在几分钟的延迟
3. **语言过滤**：某些小众语言可能在特定时间段内没有数据

---

## 数据模型

### GitHubTrendingResponse

```typescript
interface GitHubTrendingResponse {
  repos: GitHubTrendingRepo[];
  fetched_at: string;
  language: string | null;
  since: string;
}
```

### GitHubTrendingRepo

```typescript
interface GitHubTrendingRepo {
  rank: number;
  owner: string;
  repo: string;
  url: string;
  description: string;
  language: string | null;
  language_color: string | null;
  stars: number;
  stars_today: number;
  forks: number;
  built_by: string[];
}
```
