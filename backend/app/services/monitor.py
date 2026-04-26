"""
X (Twitter) 监控服务 - 支持关键词和账号监控
通过 Nitter RSS 获取推文数据，无需 API Key
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from celery import shared_task
from app.services.crawler import NitterCrawler

logger = logging.getLogger(__name__)


@dataclass
class MonitoredKeyword:
    """监控关键词"""
    keyword: str
    is_active: bool = True
    case_sensitive: bool = False


@dataclass
class MonitoredAccount:
    """监控账号"""
    account: str  # 带 @ 的用户名
    is_active: bool = True


@dataclass
class MonitorAlert:
    """监控告警"""
    matched_keyword: Optional[str]
    matched_account: Optional[str]
    content: str
    author: str
    url: str
    engagement: Dict[str, int]
    timestamp: datetime
    alert_type: str  # "keyword" or "account"


class XMonitor:
    """X (Twitter) 监控器 - 通过 Nitter RSS 获取数据"""

    def __init__(
        self,
        keywords: List[str],
        accounts: List[str],
    ):
        self.keywords = [MonitoredKeyword(k) for k in keywords]
        self.accounts = [MonitoredAccount(a) for a in accounts]
        self.nitter = NitterCrawler()
    
    def _match_keyword(self, text: str) -> Optional[str]:
        """检查文本是否匹配关键词"""
        for kw in self.keywords:
            if not kw.is_active:
                continue
            
            if kw.case_sensitive:
                if kw.keyword in text:
                    return kw.keyword
            else:
                if kw.keyword.lower() in text.lower():
                    return kw.keyword
        return None
    
    async def fetch_user_tweets(self, username: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """通过 Nitter RSS 获取用户推文"""
        try:
            # 使用同步方法在异步上下文中调用
            tweets = self.nitter.fetch_user_tweets_sync(username, max_results=max_results)
            return [
                {
                    "id": t.url.split("/")[-1] if t.url else "",
                    "text": t.content or t.title,
                    "author": f"@{username}",
                    "author_name": "",
                    "followers": 0,
                    "created_at": t.published_at.isoformat() if t.published_at else "",
                    "metrics": t.engagement or {},
                    "url": t.url,
                }
                for t in tweets
            ]
        except Exception as e:
            logger.error(f"Error fetching tweets from Nitter for @{username}: {e}")
            return []
    
    async def check_tweets(self, tweets: List[Dict[str, Any]]) -> List[MonitorAlert]:
        """检查推文并生成告警"""
        alerts = []

        for tweet in tweets:
            text = tweet.get("text", "")

            # 检查关键词匹配
            matched_keyword = self._match_keyword(text)
            if matched_keyword:
                alerts.append(MonitorAlert(
                    matched_keyword=matched_keyword,
                    matched_account=None,
                    content=text,
                    author=tweet.get("author", ""),
                    url=tweet.get("url", ""),
                    engagement=tweet.get("metrics", {}),
                    timestamp=self._parse_timestamp(tweet.get("created_at")),
                    alert_type="keyword"
                ))
                continue

            # 检查账号匹配
            for acc in self.accounts:
                if not acc.is_active:
                    continue
                if f"@{acc.account.lstrip('@')}" in text or acc.account in tweet.get("author", ""):
                    alerts.append(MonitorAlert(
                        matched_keyword=None,
                        matched_account=acc.account,
                        content=text,
                        author=tweet.get("author", ""),
                        url=tweet.get("url", ""),
                        engagement=tweet.get("metrics", {}),
                        timestamp=self._parse_timestamp(tweet.get("created_at")),
                        alert_type="account"
                    ))
                    break

        return alerts

    def _parse_timestamp(self, ts: str) -> datetime:
        """安全解析时间戳"""
        if not ts:
            return datetime.utcnow()
        try:
            return datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            return datetime.utcnow()
    
    async def monitor_cycle(self) -> List[MonitorAlert]:
        """执行一次监控循环"""
        all_alerts = []
        
        # 监控各账号
        for acc in self.accounts:
            if not acc.is_active:
                continue
            
            try:
                tweets = await self.fetch_user_tweets(acc.account)
                alerts = await self.check_tweets(tweets)
                all_alerts.extend(alerts)
            except Exception as e:
                logger.error(f"Error monitoring {acc.account}: {e}")
        
        return all_alerts


@shared_task
async def run_monitor_cycle(keywords: List[str], accounts: List[str]) -> Dict[str, Any]:
    """
    Celery 任务：运行监控循环（通过 Nitter RSS）

    被定时调用检查新的匹配推文
    """
    alerts = []

    try:
        monitor = XMonitor(keywords, accounts)
        alerts = await monitor.monitor_cycle()

        # 发送告警
        for alert in alerts:
            from app.services.sse_tasks import push_monitor_alert
            await push_monitor_alert(
                keyword=alert.matched_keyword or alert.matched_account,
                tweet_data={
                    "content": alert.content,
                    "author": alert.author,
                    "url": alert.url,
                    "engagement": alert.engagement,
                    "alert_type": alert.alert_type,
                },
                matched_type=alert.alert_type
            )

        return {
            "status": "success",
            "alerts_count": len(alerts),
            "keywords_count": len(keywords),
            "accounts_count": len(accounts),
        }

    except Exception as e:
        logger.error(f"Monitor cycle failed: {e}")
        return {
            "status": "error",
            "message": str(e),
        }


# 简单的共享状态（生产环境应使用 Redis）
_active_monitor: Optional[XMonitor] = None


def set_monitor(monitor: XMonitor):
    """设置全局监控器"""
    global _active_monitor
    _active_monitor = monitor


def get_monitor() -> Optional[XMonitor]:
    """获取全局监控器"""
    return _active_monitor
