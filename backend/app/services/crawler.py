"""
爬虫服务 - RSS / Twitter / GitHub 抓取
"""

import hashlib
import feedparser
import asyncio
from datetime import datetime
from typing import Optional, Literal
from dataclasses import dataclass
import httpx
from bs4 import BeautifulSoup
from app.services.openrouter import generate_content_hash


@dataclass
class ParsedArticle:
    """解析后的文章数据"""
    title: str
    url: str
    summary: str
    content: str
    author: str
    published_at: datetime
    source_name: str
    source_type: str
    raw_metadata: dict
    content_hash: str
    fan_count: int = 0
    engagement: dict = None

    def __post_init__(self):
        if self.engagement is None:
            self.engagement = {"likes": 0, "retweets": 0, "comments": 0}


class RSSCrawler:
    """RSS Feed 爬虫"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": "AI-News-Aggregator/1.0",
                },
            )
        return self.client

    async def fetch(self, feed_url: str) -> list[ParsedArticle]:
        """
        抓取 RSS Feed

        Args:
            feed_url: RSS Feed URL

        Returns:
            list[ParsedArticle]: 解析后的文章列表
        """
        client = await self._get_client()
        articles = []

        try:
            response = await client.get(feed_url)
            response.raise_for_status()

            # 解析 RSS
            feed = feedparser.parse(response.text)

            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry, feed.feed)
                    if article:
                        articles.append(article)
                except Exception as e:
                    # 单篇文章解析失败不影响其他文章
                    continue

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch RSS feed: {str(e)}")

        return articles

    def _parse_entry(self, entry, feed) -> Optional[ParsedArticle]:
        """解析单条 RSS 条目"""
        # 获取标题
        title = getattr(entry, "title", "") or ""

        # 获取链接
        url = getattr(entry, "link", "") or ""

        if not title or not url:
            return None

        # 获取摘要/内容
        summary = ""
        content = ""

        if hasattr(entry, "summary"):
            summary = self._clean_html(entry.summary)
        elif hasattr(entry, "description"):
            summary = self._clean_html(entry.description)

        if hasattr(entry, "content"):
            content = self._clean_html(entry.content[0].value) if entry.content else ""
        elif hasattr(entry, "content_encoded"):
            content = self._clean_html(entry.content_encoded)

        # 获取作者
        author = ""
        if hasattr(entry, "author"):
            author = entry.author
        elif hasattr(entry, "authors") and entry.authors:
            author = entry.authors[0].get("name", "")

        # 获取发布时间
        published_at = datetime.now()
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            from time import mktime
            published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            from time import mktime
            published_at = datetime.fromtimestamp(mktime(entry.updated_parsed))

        # 获取来源名称
        source_name = getattr(feed, "title", "Unknown Source")

        # 生成内容哈希
        content_hash = generate_content_hash(title, url)

        # 元数据
        raw_metadata = {
            "source": feed_url,
            "feed_title": getattr(feed, "title", ""),
            "entry_id": getattr(entry, "id", ""),
            "tags": [tag.term for tag in getattr(entry, "tags", [])],
        }

        return ParsedArticle(
            title=title,
            url=url,
            summary=summary[:1000] if summary else "",
            content=content[:5000] if content else "",
            author=author,
            published_at=published_at,
            source_name=source_name,
            source_type="rss",
            raw_metadata=raw_metadata,
            content_hash=content_hash,
            fan_count=0,
            engagement={"likes": 0, "retweets": 0, "comments": 0},
        )

    def _clean_html(self, html: str) -> str:
        """清理 HTML 标签"""
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def fetch_sync(self, feed_url: str) -> list[ParsedArticle]:
        """同步版本的 fetch"""
        import requests
        response = requests.get(feed_url, headers={"User-Agent": "AI-News-Aggregator/1.0"}, timeout=self.timeout)
        response.raise_for_status()

        feed = feedparser.parse(response.text)
        articles = []

        for entry in feed.entries:
            try:
                article = self._parse_entry(entry, feed.feed)
                if article:
                    articles.append(article)
            except Exception:
                continue

        return articles


class GitHubCrawler:
    """GitHub Trending 爬虫"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": "AI-News-Aggregator/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
        return self.client

    async def fetch_trending(
        self,
        language: str = "",
        since: str = "daily",
    ) -> list[ParsedArticle]:
        """
        抓取 GitHub Trending

        Args:
            language: 编程语言过滤，如 "python", "typescript"，空字符串表示不限语言
            since: 时间范围，"daily" | "weekly" | "monthly"

        Returns:
            list[ParsedArticle]: 解析后的 trending 项目列表
        """
        client = await self._get_client()
        articles = []

        try:
            url = "https://github.com/trending"
            if language:
                url = f"https://github.com/trending/{language}"
            params = {"since": since} if since != "daily" else None

            response = await client.get(url, params=params)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            repos = soup.select("article.Box-row")

            for repo in repos:
                article = self._parse_repo(repo, language)
                if article:
                    articles.append(article)

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch GitHub trending: {str(e)}")

        return articles

    def fetch_trending_sync(
        self,
        language: str = "",
        since: str = "daily",
    ) -> list[ParsedArticle]:
        """同步版本的 fetch_trending"""
        import requests

        headers = {
            "User-Agent": "AI-News-Aggregator/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        url = "https://github.com/trending"
        if language:
            url = f"https://github.com/trending/{language}"
        params = {"since": since} if since != "daily" else None

        response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        repos = soup.select("article.Box-row")
        articles = []

        for repo in repos:
            article = self._parse_repo(repo, language)
            if article:
                articles.append(article)

        return articles

    def _parse_repo(self, repo, language: str = "") -> Optional[ParsedArticle]:
        """解析单个 trending repo 节点"""
        # 项目名称: owner/repo
        title_tag = repo.select_one("h2 a")
        if not title_tag:
            return None

        href = title_tag.get("href", "")
        if not href.startswith("/"):
            return None

        full_name = href.lstrip("/")
        parts = full_name.split("/")
        if len(parts) != 2:
            return None
        org, repo_name = parts

        url = f"https://github.com/{full_name}"

        # 标题
        title = f"{org}/{repo_name}"

        # 描述
        desc_tag = repo.select_one("p")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        # 编程语言
        lang_tag = repo.select_one("span[itemprop='programmingLanguage']")
        lang = lang_tag.get_text(strip=True) if lang_tag else language or "Unknown"

        # Stars / Forks
        stars_tag = repo.select_one("a.Link--muted[href$='/stargazers']")
        stars_str = stars_tag.get_text(strip=True).replace(",", "") if stars_tag else "0"
        stars = self._parse_number(stars_str)

        forks_tag = repo.select_one("a.Link--muted[href$='/forks']")
        forks_str = forks_tag.get_text(strip=True).replace(",", "") if forks_tag else "0"
        forks = self._parse_number(forks_str)

        # 今日 stars（Trending 页面上有这个数据）
        stars_today_tag = repo.select_one("span.d-inline-block.float-sm-right")
        stars_today = 0
        if stars_today_tag:
            text = stars_today_tag.get_text(strip=True)
            # 格式如 "2,345 stars today"
            import re
            m = re.search(r"([\d,]+)\s+stars?\s+today", text, re.IGNORECASE)
            if m:
                stars_today = self._parse_number(m.group(1))

        # 生成内容哈希
        content_hash = generate_content_hash(title, url)

        # 元数据
        raw_metadata = {
            "org": org,
            "repo": repo_name,
            "language": lang,
            "stars": stars,
            "forks": forks,
            "stars_today": stars_today,
        }

        return ParsedArticle(
            title=title,
            url=url,
            summary=description,
            content=f"Language: {lang}\nStars: {stars}\nForks: {forks}\nStars Today: {stars_today}\n\n{description}",
            author=org,
            published_at=datetime.now(),
            source_name=full_name,
            source_type="github",
            raw_metadata=raw_metadata,
            content_hash=content_hash,
            fan_count=stars,
            engagement={"likes": stars, "retweets": forks, "comments": 0},
        )

    def _parse_number(self, text: str) -> int:
        """解析带 K/M 后缀的数字，如 1.2k -> 1200"""
        import re
        text = text.strip().upper()
        match = re.match(r"([\d.]+)\s*([KM])?", text)
        if not match:
            return 0
        num = float(match.group(1))
        suffix = match.group(2)
        if suffix == "K":
            return int(num * 1000)
        elif suffix == "M":
            return int(num * 1_000_000)
        return int(num)


# Twitter 爬虫（需要 Twitter API v2）
class TwitterCrawler:
    """Twitter/X 爬虫（需要 Bearer Token）"""

    def __init__(self, bearer_token: str, timeout: int = 30):
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.bearer_token}",
                    "User-Agent": "AI-News-Aggregator/1.0",
                },
            )
        return self.client

    async def fetch_user_tweets(
        self,
        username: str,
        max_results: int = 10,
    ) -> list[ParsedArticle]:
        """
        抓取用户推文

        Args:
            username: Twitter 用户名（不带 @）
            max_results: 最大数量

        Returns:
            list[ParsedArticle]: 解析后的推文列表
        """
        client = await self._get_client()
        articles = []

        try:
            # 获取用户 ID
            user_response = await client.get(
                "https://api.twitter.com/2/users/by/username/" + username
            )
            user_response.raise_for_status()
            user_data = user_response.json()
            user_id = user_data["data"]["id"]

            # 获取推文
            tweets_response = await client.get(
                f"https://api.twitter.com/2/users/{user_id}/tweets",
                params={
                    "max_results": min(max_results, 100),
                    "tweet.fields": "created_at,public_metrics,author_id",
                    "expansions": "author_id",
                    "user.fields": "name,username,public_metrics",
                },
            )
            tweets_response.raise_for_status()
            tweets_data = tweets_response.json()

            # 构建用户映射
            users = {
                u["id"]: u
                for u in tweets_data.get("includes", {}).get("users", [])
            }

            for tweet in tweets_data.get("data", []):
                article = self._parse_tweet(tweet, users.get(tweet["author_id"]))
                if article:
                    articles.append(article)

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch Twitter tweets: {str(e)}")

        return articles

    async def search_tweets(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[ParsedArticle]:
        """
        搜索推文

        Args:
            query: 搜索查询
            max_results: 最大数量

        Returns:
            list[ParsedArticle]: 解析后的推文列表
        """
        client = await self._get_client()
        articles = []

        try:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                params={
                    "query": query,
                    "max_results": min(max_results, 100),
                    "tweet.fields": "created_at,public_metrics,author_id",
                    "expansions": "author_id",
                    "user.fields": "name,username,public_metrics",
                },
            )
            response.raise_for_status()
            data = response.json()

            users = {
                u["id"]: u
                for u in data.get("includes", {}).get("users", [])
            }

            for tweet in data.get("data", []):
                article = self._parse_tweet(tweet, users.get(tweet["author_id"]))
                if article:
                    articles.append(article)

        except httpx.HTTPError as e:
            raise Exception(f"Failed to search Twitter: {str(e)}")

        return articles

    def _parse_tweet(self, tweet: dict, user: dict) -> Optional[ParsedArticle]:
        """解析单条推文"""
        tweet_id = tweet["id"]
        text = tweet["text"]
        created_at_str = tweet.get("created_at")
        metrics = tweet.get("public_metrics", {})

        # 构建 URL
        username = user.get("username", "unknown") if user else "unknown"
        url = f"https://twitter.com/{username}/status/{tweet_id}"

        # 标题使用推文内容前 100 字符
        title = text[:100] + ("..." if len(text) > 100 else "")

        # 摘要使用完整内容
        summary = text

        # 发布时间
        published_at = datetime.now()
        if created_at_str:
            from dateutil.parser import parse
            published_at = parse(created_at_str)

        # 粉丝数
        fan_count = user.get("public_metrics", {}).get("followers_count", 0) if user else 0

        # 互动数据
        engagement = {
            "likes": metrics.get("like_count", 0),
            "retweets": metrics.get("retweet_count", 0),
            "comments": metrics.get("reply_count", 0),
        }

        # 生成内容哈希
        content_hash = generate_content_hash(title, url)

        # 元数据
        raw_metadata = {
            "tweet_id": tweet_id,
            "username": username,
            "fan_count": fan_count,
            "engagement": engagement,
        }

        return ParsedArticle(
            title=title,
            url=url,
            summary=summary[:500] if summary else "",
            content=text,
            author=f"@{username}",
            published_at=published_at,
            source_name=f"@{username}",
            source_type="twitter",
            raw_metadata=raw_metadata,
            content_hash=content_hash,
            fan_count=fan_count,
            engagement=engagement,
        )

    def fetch_user_tweets_sync(
        self,
        username: str,
        max_results: int = 10,
    ) -> list[ParsedArticle]:
        """同步版本的 fetch_user_tweets"""
        import requests

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "AI-News-Aggregator/1.0",
        }

        # 获取用户 ID
        user_response = requests.get(
            f"https://api.twitter.com/2/users/by/username/{username}",
            headers=headers,
            timeout=self.timeout,
        )
        user_response.raise_for_status()
        user_id = user_response.json()["data"]["id"]

        # 获取推文
        tweets_response = requests.get(
            f"https://api.twitter.com/2/users/{user_id}/tweets",
            headers=headers,
            params={
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,public_metrics,author_id",
                "expansions": "author_id",
                "user.fields": "name,username,public_metrics",
            },
            timeout=self.timeout,
        )
        tweets_response.raise_for_status()
        data = tweets_response.json()

        users = {
            u["id"]: u
            for u in data.get("includes", {}).get("users", [])
        }

        articles = []
        for tweet in data.get("data", []):
            article = self._parse_tweet(tweet, users.get(tweet["author_id"]))
            if article:
                articles.append(article)

        return articles


# Nitter 爬虫（无需 API Key，通过 RSS Feed 抓取公开推文）
class NitterCrawler:
    """Nitter (Twitter 代理) 爬虫 - 通过 RSS Feed 抓取用户推文"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": "AI-News-Aggregator/1.0",
                },
            )
        return self.client

    async def fetch_user_tweets(
        self,
        username: str,
        max_results: int = 20,
        source_type_override: str = None,
    ) -> list[ParsedArticle]:
        """
        通过 Nitter RSS 抓取用户推文

        Args:
            username: Twitter 用户名（不带 @）
            max_results: 最大数量（Nitter RSS 默认返回约 20 条）
            source_type_override: 覆盖 source_type（如设为 "twitter" 而非默认的 "nitter"）

        Returns:
            list[ParsedArticle]: 解析后的推文列表
        """
        client = await self._get_client()
        articles = []

        try:
            # Nitter RSS 格式: https://nitter.net/{username}/rss
            url = f"https://nitter.net/{username}/rss"
            response = await client.get(url)
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry, username, source_type_override)
                    if article:
                        articles.append(article)
                        if len(articles) >= max_results:
                            break
                except Exception:
                    continue

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch Nitter feed: {str(e)}")

        return articles

    def _parse_entry(self, entry, username: str, source_type_override: str = None) -> Optional[ParsedArticle]:
        """解析单条 Nitter RSS 条目
        
        Args:
            entry: RSS entry
            username: Twitter username
            source_type_override: Override the source_type (e.g., 'twitter' instead of 'nitter')
        """
        import re

        # 标题/正文
        title = getattr(entry, "title", "") or ""
        description = getattr(entry, "description", "") or ""
        link = getattr(entry, "link", "") or ""
        
        # 移除 Nitter URL 后缀 "#m"，转换为真正的 Twitter URL
        if link:
            link = link.replace("#m", "")
            # 替换 nitter.net 为 x.com
            link = link.replace("nitter.net", "x.com")

        # Nitter 的 description 包含 HTML，需要解析
        # 格式: <p>推文内容</p><br><a href="...">❤️ 123</a> <a href="...">🔁 45</a> <a href="...">💬 6</a>
        soup = BeautifulSoup(description, "html.parser")

        # 提取推文正文（<p> 标签内容）
        p_tags = soup.find_all("p")
        tweet_text = ""
        for p in p_tags:
            text = p.get_text(strip=True)
            if text:
                tweet_text += text + "\n"
        tweet_text = tweet_text.strip()

        # 提取互动数据
        engagement = {"likes": 0, "retweets": 0, "comments": 0}
        fan_count = 0  # Nitter RSS 不提供粉丝数

        # 查找互动数字
        links = soup.find_all("a")
        for link_tag in links:
            href = link_tag.get("href", "")
            text = link_tag.get_text(strip=True)

            # 点赞格式: ❤️ 123 或 ❤️123
            if "like" in href.lower() or "❤️" in text:
                match = re.search(r"([\d,]+)", text)
                if match:
                    engagement["likes"] = int(match.group(1).replace(",", ""))

            # 转发格式: 🔁 45 或 45 Retweets
            elif "retweet" in href.lower() or "🔁" in text or "retweet" in text.lower():
                match = re.search(r"([\d,]+)", text)
                if match:
                    engagement["retweets"] = int(match.group(1).replace(",", ""))

            # 评论格式: 💬 6 或 6 Replies
            elif "reply" in href.lower() or "💬" in text or "reply" in text.lower():
                match = re.search(r"([\d,]+)", text)
                if match:
                    engagement["comments"] = int(match.group(1).replace(",", ""))

        # 发布时间
        published_at = datetime.now()
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            from time import mktime
            published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            from time import mktime
            published_at = datetime.fromtimestamp(mktime(entry.updated_parsed))

        # 生成内容哈希
        content_hash = generate_content_hash(title, link)

        # 元数据
        raw_metadata = {
            "username": username,
            "engagement": engagement,
            "fan_count": fan_count,
        }

        # 清理标题
        # 如果 title 是链接格式（如 x.com/i/article/...），检查提取的内容是否有意义
        is_url_title = "x.com" in title or "nitter.net" in title or title.startswith("http")
        
        # 检查 tweet_text 是否只是链接
        is_url_text = tweet_text.startswith("x.com") or tweet_text.startswith("http") or "x.com/i/article" in tweet_text
        
        if is_url_title or is_url_text:
            # title 或提取的文本都是链接，使用有意义的标题
            title = "[图片/链接推文]"
        
        # 如果没有从 description 提取到正文，用 title
        if not tweet_text or tweet_text.startswith("x.com") or "x.com/i/article" in tweet_text:
            tweet_text = title

        # Use override source_type if provided, otherwise default to "nitter"
        source_type = source_type_override if source_type_override else "nitter"
        
        return ParsedArticle(
            title=title[:100] + ("..." if len(title) > 100 else ""),
            url=link,
            summary=tweet_text[:500] if tweet_text else title,
            content=tweet_text,
            author=f"@{username}",
            published_at=published_at,
            source_name=f"@{username} (Nitter)",
            source_type=source_type,
            raw_metadata=raw_metadata,
            content_hash=content_hash,
            fan_count=fan_count,
            engagement=engagement,
        )

    def fetch_user_tweets_sync(
        self,
        username: str,
        max_results: int = 20,
        source_type_override: str = None,
    ) -> list[ParsedArticle]:
        """同步版本的 fetch_user_tweets
        
        Args:
            username: Twitter 用户名（不带 @）
            max_results: 最大数量
            source_type_override: 覆盖 source_type（如设为 "twitter" 而非默认的 "nitter"）
        """
        import requests

        response = requests.get(
            f"https://nitter.net/{username}/rss",
            headers={"User-Agent": "AI-News-Aggregator/1.0"},
            timeout=self.timeout,
        )
        response.raise_for_status()

        feed = feedparser.parse(response.text)
        articles = []

        for entry in feed.entries:
            try:
                article = self._parse_entry(entry, username, source_type_override)
                if article:
                    articles.append(article)
                    if len(articles) >= max_results:
                        break
            except Exception:
                continue

        return articles


def crawl_source(source_config: dict) -> list[dict]:
    """
    根据信源配置抓取内容（同步版本，用于 Celery 任务）

    Args:
        source_config: 信源配置

    Returns:
        list[dict]: 文章数据列表
    """
    articles = []
    source_type = source_config.get("type", "")

    if source_type == "rss":
        crawler = RSSCrawler()
        feed_url = source_config.get("feed_url")
        if feed_url:
            parsed = crawler.fetch_sync(feed_url)
            articles = [article_to_dict(a) for a in parsed]

    elif source_type == "github":
        crawler = GitHubCrawler()
        language = source_config.get("language", "")
        since = source_config.get("since", "daily")
        parsed = crawler.fetch_trending_sync(language=language, since=since)
        articles = [article_to_dict(a) for a in parsed]

    elif source_type == "twitter":
        # Twitter 类型使用 Nitter RSS 获取，但保留原始 source_type
        crawler = NitterCrawler()
        username = source_config.get("account", "").lstrip("@") or source_config.get("username", "")
        if username:
            parsed = crawler.fetch_user_tweets_sync(username, source_type_override="twitter")
            articles = [article_to_dict(a) for a in parsed]

    elif source_type == "nitter":
        crawler = NitterCrawler()
        username = source_config.get("username", "")
        if username:
            parsed = crawler.fetch_user_tweets_sync(username)
            articles = [article_to_dict(a) for a in parsed]

    return articles


def article_to_dict(article: ParsedArticle) -> dict:
    """将 ParsedArticle 转换为字典"""
    return {
        "title": article.title,
        "url": article.url,
        "summary": article.summary,
        "content": article.content,
        "author": article.author,
        "published_at": article.published_at,
        "source_name": article.source_name,
        "source_type": article.source_type,
        "raw_metadata": article.raw_metadata,
        "content_hash": article.content_hash,
        "fan_count": article.fan_count,
        "engagement": article.engagement,
    }
