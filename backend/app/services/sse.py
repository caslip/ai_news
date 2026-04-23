"""
SSE (Server-Sent Events) 实时推送服务
支持 X 监控、爆文通知等实时事件
"""

import asyncio
import json
import logging
from typing import Optional, Set, Dict, Any, Callable, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from fastapi import APIRouter, Request, Response
from sse_starlette.sse import EventSourceResponse
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class EventType(str, Enum):
    """事件类型"""
    PING = "ping"
    NEW_ARTICLE = "new_article"
    TRENDING_UPDATE = "trending_update"
    MONITOR_ALERT = "monitor_alert"
    SYSTEM_NOTIFICATION = "system_notification"


@dataclass
class SSEEvent:
    """SSE 事件"""
    event: EventType
    data: Dict[str, Any]
    id: Optional[str] = None
    retry: Optional[int] = 5000

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "event": self.event.value,
            "data": json.dumps(self.data, ensure_ascii=False),
        }
        if self.id:
            result["id"] = self.id
        if self.retry:
            result["retry"] = self.retry
        return result


class SSEManager:
    """SSE 连接管理器"""
    
    def __init__(self):
        self._connections: Dict[str, Set[asyncio.Queue]] = {}
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
    
    async def connect(self, client_id: str, queue: asyncio.Queue) -> None:
        """添加 SSE 连接"""
        if client_id not in self._connections:
            self._connections[client_id] = set()
        self._connections[client_id].add(queue)
        logger.info(f"Client {client_id} connected. Total connections: {len(self._connections)}")
    
    async def disconnect(self, client_id: str, queue: asyncio.Queue) -> None:
        """移除 SSE 连接"""
        if client_id in self._connections:
            self._connections[client_id].discard(queue)
            if not self._connections[client_id]:
                del self._connections[client_id]
        logger.info(f"Client {client_id} disconnected. Total connections: {len(self._connections)}")
    
    async def broadcast(self, event: SSEEvent, target_clients: Optional[Set[str]] = None) -> None:
        """广播事件到所有或指定客户端"""
        clients = target_clients if target_clients else set(self._connections.keys())
        
        for client_id in clients:
            if client_id in self._connections:
                for queue in self._connections[client_id]:
                    try:
                        await queue.put(event)
                    except Exception as e:
                        logger.error(f"Failed to send event to {client_id}: {e}")
    
    async def publish_to_redis(self, channel: str, event: SSEEvent) -> None:
        """发布事件到 Redis 频道（用于分布式部署）"""
        if self._redis:
            try:
                await self._redis.publish(channel, json.dumps(event.to_dict(), ensure_ascii=False))
            except Exception as e:
                logger.error(f"Failed to publish to Redis: {e}")
    
    async def subscribe_redis(self, channels: list[str]) -> None:
        """订阅 Redis 频道"""
        if self._redis:
            self._pubsub = self._redis.pubsub()
            await self._pubsub.subscribe(*channels)
            logger.info(f"Subscribed to Redis channels: {channels}")
    
    async def listen_redis(self) -> None:
        """监听 Redis 消息"""
        if self._pubsub:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        event = SSEEvent(
                            event=EventType(data["event"]),
                            data=json.loads(data["data"])
                        )
                        await self.broadcast(event)
                    except Exception as e:
                        logger.error(f"Failed to process Redis message: {e}")


# 全局 SSE 管理器
sse_manager = SSEManager()


async def event_generator(request: Request, client_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    SSE 事件生成器
    
    生成器会持续 yield 事件直到客户端断开连接
    """
    queue = asyncio.Queue()
    
    # 注册连接
    await sse_manager.connect(client_id, queue)
    
    try:
        # 发送连接成功事件
        yield {
            "event": "connected",
            "data": json.dumps({"client_id": client_id, "timestamp": datetime.utcnow().isoformat()}),
        }
        
        # 持续发送事件直到客户端断开
        while True:
            # 检查客户端是否断开
            if await request.is_disconnected():
                break
            
            try:
                # 等待事件，最多等待 30 秒
                event = await asyncio.wait_for(queue.get(), timeout=30)
                yield event.to_dict()
            except asyncio.TimeoutError:
                # 发送心跳
                yield {
                    "event": "ping",
                    "data": json.dumps({"timestamp": datetime.utcnow().isoformat()}),
                    "retry": 5000,
                }
    except asyncio.CancelledError:
        pass
    finally:
        # 注销连接
        await sse_manager.disconnect(client_id, queue)


@router.get("/events")
async def sse_events(request: Request):
    """
    SSE 事件流端点
    
    支持的查询参数:
    - channels: 订阅的频道 (new_article, trending, monitor)
    """
    import uuid
    
    client_id = str(uuid.uuid4())[:8]
    
    response = EventSourceResponse(
        event_generator(request, client_id)
    )
    
    return response


@router.get("/events/monitor")
async def monitor_events(request: Request):
    """
    X 监控专用事件流
    
    返回监控关键词匹配和账号推文事件
    """
    import uuid
    
    client_id = f"monitor_{str(uuid.uuid4())[:8]}"
    
    response = EventSourceResponse(
        event_generator(request, client_id)
    )
    
    return response


@router.get("/events/trending")
async def trending_events(request: Request):
    """
    爆文事件流
    
    返回新的低粉爆文通知
    """
    import uuid
    
    client_id = f"trending_{str(uuid.uuid4())[:8]}"
    
    response = EventSourceResponse(
        event_generator(request, client_id)
    )
    
    return response


# 辅助函数：发送新文章事件
async def notify_new_article(article_data: Dict[str, Any]) -> None:
    """通知新文章"""
    event = SSEEvent(
        event=EventType.NEW_ARTICLE,
        data={
            "type": "new_article",
            "article": article_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    await sse_manager.broadcast(event)


# 辅助函数：发送爆文更新
async def notify_trending_update(trending_articles: list) -> None:
    """通知爆文更新"""
    event = SSEEvent(
        event=EventType.TRENDING_UPDATE,
        data={
            "type": "trending_update",
            "articles": trending_articles,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    await sse_manager.broadcast(event)


# 辅助函数：发送监控告警
async def notify_monitor_alert(
    keyword: str,
    tweet_data: Dict[str, Any],
    matched_type: str = "keyword"
) -> None:
    """发送监控告警"""
    event = SSEEvent(
        event=EventType.MONITOR_ALERT,
        data={
            "type": "monitor_alert",
            "keyword": keyword,
            "matched_type": matched_type,
            "tweet": tweet_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    await sse_manager.broadcast(event)


# 辅助函数：发送系统通知
async def notify_system(message: str, level: str = "info") -> None:
    """发送系统通知"""
    event = SSEEvent(
        event=EventType.SYSTEM_NOTIFICATION,
        data={
            "type": "system",
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    await sse_manager.broadcast(event)
