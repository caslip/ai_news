"""
OpenRouter AI Service - AI 内容分析与评分
支持 Claude、GPT、Mistral 等多模型
"""

import os
import json
import hashlib
import logging
from typing import Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"
BASE_URL = "https://openrouter.ai/api/v1"


class AIServiceError(Exception):
    """AI Service 相关错误"""
    pass


async def get_openrouter_client() -> httpx.AsyncClient:
    """获取 OpenRouter 客户端"""
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-news-aggregator",
            "X-Title": "AI News Aggregator",
        },
        timeout=60.0,
    )


async def score_article(
    title: str,
    content: str,
    metadata: dict,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    使用 AI 分析文章并给出评分

    Args:
        title: 文章标题
        content: 文章内容/摘要
        metadata: 文章元数据
        model: 使用的模型

    Returns:
        dict: 评分结果
    """
    if not settings.openrouter_api_key:
        raise AIServiceError("OpenRouter API key not configured")

    system_prompt = """你是一个专业的AI内容分析师，专门评估AI领域资讯的价值。

请从以下三个维度对文章进行评分（每个维度 1-10 分）：

1. **内容质量 (quality)**
   - 深度：是否有独到见解、技术深度如何
   - 原创性：是否提供新信息、新观点
   - 准确性：技术细节是否准确可靠

2. **话题热度 (hotness)**
   - 时效性：是否是当前热门话题
   - 行业关注度：在AI领域的影响力
   - 趋势性：是否代表某种技术趋势

3. **传播潜力 (spread_potential)**
   - 易懂程度：非专业人士能否理解
   - 话题延展性：是否能引发讨论
   - 实用价值：对读者有多少实际帮助

请返回严格的 JSON 格式，不要有任何额外文字：
{
    "quality": 7.5,
    "hotness": 8.0,
    "spread_potential": 6.5,
    "reasoning": "这篇文章分析了...",
    "tags": ["标签1", "标签2", "标签3"]
}"""

    user_content = f"""文章标题：{title}

文章内容：
{content[:2000] if content else "无内容摘要"}

元数据：
- 来源：{metadata.get('source', '未知')}
- 作者：{metadata.get('author', '未知')}
- 互动数据：{json.dumps(metadata.get('engagement', {}), ensure_ascii=False)}"""

    client = await get_openrouter_client()
    try:
        response = await client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
                "max_tokens": 500,
            },
        )

        if response.status_code != 200:
            error_text = response.text
            logger.error(f"OpenRouter API error: {response.status_code} - {error_text}")
            raise AIServiceError(f"API returned {response.status_code}: {error_text}")

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        parsed = json.loads(content)
        return {
            "quality": float(parsed.get("quality", 5.0)),
            "hotness": float(parsed.get("hotness", 5.0)),
            "spread_potential": float(parsed.get("spread_potential", 5.0)),
            "reasoning": str(parsed.get("reasoning", "")),
            "tags": list(parsed.get("tags", [])),
        }

    except httpx.HTTPError as e:
        logger.error(f"HTTP error calling OpenRouter: {e}")
        raise AIServiceError(f"HTTP error: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response: {e}")
        raise AIServiceError(f"Failed to parse response: {str(e)}")
    finally:
        await client.aclose()


async def generate_summary(
    content: str,
    max_length: int = 500,
    model: str = DEFAULT_MODEL,
) -> str:
    """生成文章摘要"""
    if not settings.openrouter_api_key:
        raise AIServiceError("OpenRouter API key not configured")

    system_prompt = f"""你是一个专业的AI内容摘要专家。请为以下文章生成简洁、准确的摘要。

要求：
- 长度控制在 {max_length} 字以内
- 保留核心信息和关键观点
- 语言简洁明了
- 直接输出摘要内容，不需要额外说明"""

    client = await get_openrouter_client()
    try:
        response = await client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content[:5000]},
                ],
                "temperature": 0.3,
                "max_tokens": max_length // 2,
            },
        )

        if response.status_code != 200:
            raise AIServiceError(f"API returned {response.status_code}")

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    finally:
        await client.aclose()


def calculate_hot_score(
    quality: float,
    hotness: float,
    spread: float,
    engagement: dict,
) -> float:
    """
    计算热度分数

    公式：综合评分 = (质量*0.3 + 热度*0.4 + 传播力*0.3) * 10 + 互动加权

    Args:
        quality: 质量评分 (1-10)
        hotness: 热度评分 (1-10)
        spread: 传播力评分 (1-10)
        engagement: 互动数据

    Returns:
        float: 0-100 的热度分数
    """
    base_score = quality * 0.3 + hotness * 0.4 + spread * 0.3

    likes = engagement.get("likes", 0)
    retweets = engagement.get("retweets", 0)
    comments = engagement.get("comments", 0)

    engagement_score = (
        likes * 1 +
        retweets * 3 +
        comments * 2
    ) / 1000

    final_score = min(100, base_score * 10 + engagement_score)
    return round(final_score, 2)


def is_low_fan_viral(
    fan_count: int,
    engagement: dict,
    quality_score: float,
    strategy_params: dict,
) -> bool:
    """
    判断是否为低粉爆文

    低粉爆文条件：
    1. 粉丝数低于阈值
    2. 互动数超过阈值
    3. 爆文指数达到阈值
    4. AI 质量评分达标
    """
    max_fan_count = strategy_params.get("max_fan_count", 10000)
    min_engagement = strategy_params.get("min_engagement", 100)
    min_viral_score = strategy_params.get("min_viral_score", 5.0)
    min_quality_score = strategy_params.get("min_quality_score", 6.0)

    if fan_count > max_fan_count:
        return False

    total_engagement = (
        engagement.get("likes", 0) +
        engagement.get("retweets", 0) * 3 +
        engagement.get("comments", 0) * 2
    )
    if total_engagement < min_engagement:
        return False

    viral_score = total_engagement / (fan_count + 1) * 1000
    if viral_score < min_viral_score:
        return False

    if quality_score < min_quality_score:
        return False

    return True


def generate_content_hash(title: str, url: str) -> str:
    """生成内容哈希用于去重"""
    content = f"{title}|{url}".encode("utf-8")
    return hashlib.sha256(content).hexdigest()
