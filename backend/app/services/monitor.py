"""
X (Twitter) 监控服务 - 支持关键词和账号监控
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import asyncio
import httpx

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
    """X (Twitter) 监控器"""
    
    def __init__(
        self,
        keywords: List[str],
        accounts: List[str],
        bearer_token: Optional[str] = None
    ):
        self.keywords = [MonitoredKeyword(k) for k in keywords]
        self.accounts = [MonitoredAccount(a) for a in accounts]
        self.bearer_token = bearer_token or ""
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": "AI-News-Monitor/1.0",
            },
            timeout=30.0
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
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
        """获取用户推文"""
        if not self.client or not self.bearer_token:
            logger.warning("No bearer token provided for Twitter API")
            return []
        
        try:
            # 获取用户 ID
            username_clean = username.lstrip("@")
            user_response = await self.client.get(
                f"https://api.twitter.com/2/users/by/username/{username_clean}"
            )
            
            if user_response.status_code != 200:
                logger.error(f"Failed to get user ID for {username}: {user_response.status_code}")
                return []
            
            user_data = user_response.json()
            user_id = user_data["data"]["id"]
            
            # 获取推文
            tweets_response = await self.client.get(
                f"https://api.twitter.com/2/users/{user_id}/tweets",
                params={
                    "max_results": min(max_results, 100),
                    "tweet.fields": "created_at,public_metrics,author_id",
                    "expansions": "author_id",
                    "user.fields": "name,username,public_metrics",
                }
            )
            
            if tweets_response.status_code != 200:
                logger.error(f"Failed to get tweets: {tweets_response.status_code}")
                return []
            
            data = tweets_response.json()
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            
            tweets = []
            for tweet in data.get("data", []):
                author = users.get(tweet["author_id"], {})
                tweets.append({
                    "id": tweet["id"],
                    "text": tweet["text"],
                    "author": f"@{author.get('username', username_clean)}",
                    "author_name": author.get("name", ""),
                    "followers": author.get("public_metrics", {}).get("followers_count", 0),
                    "created_at": tweet.get("created_at"),
                    "metrics": tweet.get("public_metrics", {}),
                    "url": f"https://twitter.com/{username_clean}/status/{tweet['id']}",
                })
            
            return tweets
        
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
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
                    timestamp=datetime.fromisoformat(tweet.get("created_at", datetime.utcnow().isoformat())),
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
                        timestamp=datetime.fromisoformat(tweet.get("created_at", datetime.utcnow().isoformat())),
                        alert_type="account"
                    ))
                    break
        
        return alerts
    
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
    Celery 任务：运行监控循环
    
    被定时调用检查新的匹配推文
    """
    alerts = []
    
    try:
        bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")
        
        async with XMonitor(keywords, accounts, bearer_token) as monitor:
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
