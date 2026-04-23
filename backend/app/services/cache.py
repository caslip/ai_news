"""
Redis 缓存服务
提供热榜缓存、分布式锁等功能
"""

import json
import logging
from typing import Optional, Any, List, Dict
from datetime import timedelta
import hashlib

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis 缓存服务"""
    
    # 缓存键前缀
    PREFIX = "ai_news:"
    
    # TTL 配置 (秒)
    TTL_HOT_ARTICLES = 300  # 5 分钟
    TTL_TRENDING = 300  # 5 分钟
    TTL_STATS = 600  # 10 分钟
    TTL_SOURCE = 600  # 10 分钟
    TTL_USER_SESSION = 86400  # 24 小时
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
    
    async def get_redis(self) -> redis.Redis:
        """获取 Redis 连接"""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis
    
    async def close(self):
        """关闭连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    def _key(self, *parts) -> str:
        """生成缓存键"""
        return self.PREFIX + ":".join(str(p) for p in parts)
    
    # ============ 基础操作 ============
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        try:
            r = await self.get_redis()
            return await r.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """设置值"""
        try:
            r = await self.get_redis()
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            await r.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除键"""
        try:
            r = await self.get_redis()
            await r.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            r = await self.get_redis()
            return await r.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    # ============ 热榜缓存 ============
    
    async def get_hot_articles(self, page: int = 1, page_size: int = 20) -> Optional[Dict]:
        """获取热榜缓存"""
        key = self._key("hot", f"page_{page}", f"size_{page_size}")
        data = await self.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_hot_articles(
        self,
        articles: List[Dict],
        page: int = 1,
        page_size: int = 20,
    ) -> bool:
        """设置热榜缓存"""
        key = self._key("hot", f"page_{page}", f"size_{page_size}")
        return await self.set(key, articles, self.TTL_HOT_ARTICLES)
    
    async def invalidate_hot_cache(self) -> None:
        """清除热榜缓存"""
        try:
            r = await self.get_redis()
            keys = await r.keys(self._key("hot", "*"))
            if keys:
                await r.delete(*keys)
        except Exception as e:
            logger.error(f"Invalidate hot cache error: {e}")
    
    # ============ 爆文缓存 ============
    
    async def get_trending_articles(self, page: int = 1) -> Optional[Dict]:
        """获取爆文缓存"""
        key = self._key("trending", f"page_{page}")
        data = await self.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_trending_articles(self, articles: List[Dict], page: int = 1) -> bool:
        """设置爆文缓存"""
        key = self._key("trending", f"page_{page}")
        return await self.set(key, articles, self.TTL_TRENDING)
    
    async def invalidate_trending_cache(self) -> None:
        """清除爆文缓存"""
        try:
            r = await self.get_redis()
            keys = await r.keys(self._key("trending", "*"))
            if keys:
                await r.delete(*keys)
        except Exception as e:
            logger.error(f"Invalidate trending cache error: {e}")
    
    # ============ 统计缓存 ============
    
    async def get_stats(self) -> Optional[Dict]:
        """获取统计缓存"""
        key = self._key("stats")
        data = await self.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_stats(self, stats: Dict) -> bool:
        """设置统计缓存"""
        key = self._key("stats")
        return await self.set(key, stats, self.TTL_STATS)
    
    # ============ 用户会话 ============
    
    async def set_user_session(self, user_id: str, session_data: Dict) -> bool:
        """设置用户会话"""
        key = self._key("session", user_id)
        return await self.set(key, session_data, self.TTL_USER_SESSION)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict]:
        """获取用户会话"""
        key = self._key("session", user_id)
        data = await self.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def delete_user_session(self, user_id: str) -> bool:
        """删除用户会话"""
        key = self._key("session", user_id)
        return await self.delete(key)
    
    # ============ Token 黑名单 ============
    
    async def add_token_to_blacklist(self, token_jti: str, ttl: int) -> bool:
        """将 Token 加入黑名单"""
        key = self._key("blacklist", "token", token_jti)
        return await self.set(key, "1", ttl)
    
    async def is_token_blacklisted(self, token_jti: str) -> bool:
        """检查 Token 是否在黑名单"""
        key = self._key("blacklist", "token", token_jti)
        return await self.exists(key)
    
    # ============ 分布式锁 ============
    
    async def acquire_lock(
        self,
        lock_name: str,
        ttl: int = 30,
        blocking: bool = True,
        blocking_timeout: int = 10,
    ) -> Optional[str]:
        """
        获取分布式锁
        
        返回锁的持有标识，用于释放锁
        """
        import uuid
        
        lock_key = self._key("lock", lock_name)
        lock_value = str(uuid.uuid4())
        
        try:
            r = await self.get_redis()
            
            if blocking:
                end_time = timedelta(seconds=blocking_timeout) + timedelta(seconds=1)
                
                for _ in range(int(blocking_timeout)):
                    if await r.set(lock_key, lock_value, nx=True, ex=ttl):
                        return lock_value
                    import asyncio
                    await asyncio.sleep(0.1)
                
                return None
            else:
                if await r.set(lock_key, lock_value, nx=True, ex=ttl):
                    return lock_value
                return None
                
        except Exception as e:
            logger.error(f"Acquire lock error: {e}")
            return None
    
    async def release_lock(self, lock_name: str, lock_value: str) -> bool:
        """释放分布式锁"""
        lock_key = self._key("lock", lock_name)
        
        try:
            r = await self.get_redis()
            
            # 使用 Lua 脚本确保原子性
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            result = await r.eval(script, 1, lock_key, lock_value)
            return result == 1
            
        except Exception as e:
            logger.error(f"Release lock error: {e}")
            return False
    
    # ============ 队列操作 ============
    
    async def enqueue_task(self, queue_name: str, task_data: Dict) -> bool:
        """入队任务"""
        key = self._key("queue", queue_name)
        
        try:
            r = await self.get_redis()
            await r.lpush(key, json.dumps(task_data, ensure_ascii=False))
            return True
        except Exception as e:
            logger.error(f"Enqueue task error: {e}")
            return False
    
    async def dequeue_task(self, queue_name: str, timeout: int = 0) -> Optional[Dict]:
        """出队任务"""
        key = self._key("queue", queue_name)
        
        try:
            r = await self.get_redis()
            
            if timeout > 0:
                result = await r.brpop(key, timeout)
                if result:
                    return json.loads(result[1])
            else:
                result = await r.rpop(key)
                if result:
                    return json.loads(result)
            
            return None
        except Exception as e:
            logger.error(f"Dequeue task error: {e}")
            return None
    
    async def get_queue_length(self, queue_name: str) -> int:
        """获取队列长度"""
        key = self._key("queue", queue_name)
        
        try:
            r = await self.get_redis()
            return await r.llen(key)
        except Exception as e:
            logger.error(f"Get queue length error: {e}")
            return 0


# 全局缓存服务实例
cache_service = CacheService()
