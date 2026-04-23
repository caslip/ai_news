"""
test_articles.py - 文章 API 测试
"""

import pytest
from fastapi import status
from datetime import datetime


class TestArticlesAPI:
    """文章 API 测试类"""
    
    def test_list_articles_empty(self, client, auth_headers):
        """测试空文章列表"""
        response = client.get("/api/articles", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
    
    def test_list_articles_with_data(self, client, auth_headers, db_session):
        """测试有数据的文章列表"""
        from app.models.article import Article
        from app.models.source import Source, SourceType
        
        # 创建测试信源
        source = Source(
            name="Test Source",
            type=SourceType.RSS,
            config={"feed_url": "https://example.com/feed.xml"},
            is_active=True,
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        # 创建测试文章
        article = Article(
            source_id=source.id,
            title="Test Article",
            url="https://example.com/article",
            summary="Test summary",
            content_hash="test_hash_123",
            hot_score=85.5,
            is_low_fan_viral=True,
            fetched_at=datetime.utcnow(),
        )
        db_session.add(article)
        db_session.commit()
        
        response = client.get("/api/articles", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert any(a["title"] == "Test Article" for a in data["items"])
    
    def test_list_articles_filter_by_source_type(self, client, auth_headers, db_session):
        """测试按信源类型过滤"""
        response = client.get("/api/articles?source_type=rss", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_articles_filter_by_time_range(self, client, auth_headers):
        """测试按时间范围过滤"""
        response = client.get("/api/articles?time_range=week", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_articles_search(self, client, auth_headers):
        """测试搜索功能"""
        response = client.get("/api/articles?q=test", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_articles_pagination(self, client, auth_headers):
        """测试分页"""
        response = client.get("/api/articles?page=1&page_size=10", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
    
    def test_list_trending_articles(self, client, auth_headers, db_session):
        """测试低粉爆文列表"""
        response = client.get("/api/articles/trending", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
    
    def test_get_article_stats(self, client, auth_headers):
        """测试文章统计"""
        response = client.get("/api/articles/stats", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "today_count" in data
        assert "week_count" in data
        assert "month_count" in data
        assert "total_count" in data
    
    def test_get_article_not_found(self, client, auth_headers):
        """测试获取不存在的文章"""
        response = client.get(
            "/api/articles/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestArticleFiltering:
    """文章筛选逻辑测试"""
    
    def test_filter_low_fan_viral(self, client, auth_headers, db_session):
        """测试低粉爆文筛选"""
        response = client.get(
            "/api/articles?is_low_fan_viral=true",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_sort_by_hot(self, client, auth_headers):
        """测试按热度排序"""
        response = client.get("/api/articles?sort=hot", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_sort_by_time(self, client, auth_headers):
        """测试按时间排序"""
        response = client.get("/api/articles?sort=time", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
