"""
GitHub Trending API - 直接从 GitHub 爬取 Trending 数据
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime

router = APIRouter()


class GitHubTrendingRepo(BaseModel):
    """GitHub Trending 仓库"""
    rank: int
    owner: str
    repo: str
    url: str
    description: str
    language: Optional[str] = None
    language_color: Optional[str] = None
    stars: int
    stars_today: int
    forks: int
    built_by: list[str] = []


class GitHubTrendingResponse(BaseModel):
    """GitHub Trending 响应"""
    repos: list[GitHubTrendingRepo]
    fetched_at: str
    language: Optional[str] = None
    since: str = "daily"


def parse_number(text: str) -> int:
    """解析带 K/M 后缀的数字，如 1.2k -> 1200"""
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


def parse_trending_html(html: str, language: str = "") -> list[GitHubTrendingRepo]:
    """解析 GitHub Trending 页面 HTML"""
    soup = BeautifulSoup(html, "html.parser")
    repos = soup.select("article.Box-row")
    results = []

    for rank, repo in enumerate(repos, 1):
        try:
            # 项目名称
            title_tag = repo.select_one("h2 a")
            if not title_tag:
                continue

            href = title_tag.get("href", "")
            if not href.startswith("/"):
                continue

            full_name = href.lstrip("/")
            parts = full_name.split("/")
            if len(parts) != 2:
                continue

            org, repo_name = parts
            url = f"https://github.com/{full_name}"

            # 描述
            desc_tag = repo.select_one("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # 编程语言
            lang_tag = repo.select_one("span[itemprop='programmingLanguage']")
            lang = lang_tag.get_text(strip=True) if lang_tag else language or None

            lang_color_tag = repo.select_one("span.repo-language-color")
            lang_color = lang_color_tag.get("style", "").split("background-color:")[-1].strip() if lang_color_tag else None

            # Stars
            stars_tag = repo.select_one("a.Link--muted[href$='/stargazers']")
            stars_str = stars_tag.get_text(strip=True).replace(",", "") if stars_tag else "0"
            stars = parse_number(stars_str)

            # Forks
            forks_tag = repo.select_one("a.Link--muted[href$='/forks']")
            forks_str = forks_tag.get_text(strip=True).replace(",", "") if forks_tag else "0"
            forks = parse_number(forks_str)

            # 今日 stars
            stars_today = 0
            stars_today_tag = repo.select_one("span.d-inline-block.float-sm-right")
            if stars_today_tag:
                text = stars_today_tag.get_text(strip=True)
                m = re.search(r"([\d,]+)\s+stars?\s+today", text, re.IGNORECASE)
                if m:
                    stars_today = parse_number(m.group(1))

            # 构建者
            built_by = []
            built_by_tags = repo.select("span.mr-3 a img.avatar")
            for img in built_by_tags[:5]:
                alt = img.get("alt", "")
                if alt.startswith("@"):
                    built_by.append(alt[1:])

            results.append(GitHubTrendingRepo(
                rank=rank,
                owner=org,
                repo=repo_name,
                url=url,
                description=description,
                language=lang,
                language_color=lang_color,
                stars=stars,
                stars_today=stars_today,
                forks=forks,
                built_by=built_by,
            ))
        except Exception:
            continue

    return results


@router.get("/trending", response_model=GitHubTrendingResponse)
async def get_github_trending(
    language: str = Query("", description="编程语言过滤，如 python, typescript"),
    since: str = Query("daily", description="时间范围: daily, weekly, monthly"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
):
    """
    获取 GitHub Trending 数据

    直接从 GitHub 爬取当前的 Trending 仓库信息。
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = "https://github.com/trending"
        if language:
            url = f"https://github.com/trending/{language}"

        headers = {
            "User-Agent": "AI-News-Aggregator/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        params = {}
        if since != "daily":
            params["since"] = since

        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()

        repos = parse_trending_html(response.text, language)

        # 限制返回数量
        repos = repos[:limit]

        return GitHubTrendingResponse(
            repos=repos,
            fetched_at=datetime.utcnow().isoformat(),
            language=language or None,
            since=since,
        )
