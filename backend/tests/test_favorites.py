"""
test_favorites.py - 收藏 API 测试
"""

import pytest
from fastapi import status


class TestFavoritesAPI:
    """收藏 API 测试类"""
    
    def test_list_favorites_empty(self, client, auth_headers):
        """测试空收藏列表"""
        response = client.get("/api/favorites", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_add_favorite(self, client, auth_headers, db_session):
        """测试添加收藏"""
        from app.models.article import Article
        from app.models.source import Source, SourceType
        
        # 创建信源和文章
        source = Source(
            name="Test Source",
            type=SourceType.RSS,
            config={"feed_url": "https://test.com/feed"},
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        article = Article(
            source_id=source.id,
            title="Test Article",
            url="https://test.com/article",
            content_hash="test_hash_fav_123",
            fetched_at=pytest.import_module("datetime").datetime.utcnow(),
        )
        db_session.add(article)
        db_session.commit()
        db_session.refresh(article)
        
        response = client.post(
            "/api/favorites",
            headers=auth_headers,
            params={"article_id": str(article.id)}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["message"] == "Added to favorites"
    
    def test_add_duplicate_favorite(self, client, auth_headers, db_session, test_user):
        """测试重复添加收藏"""
        from app.models.article import Article
        from app.models.bookmark import Bookmark
        from app.models.source import Source, SourceType
        
        # 创建信源和文章
        source = Source(
            name="Test Source",
            type=SourceType.RSS,
            config={"feed_url": "https://test.com/feed"},
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        article = Article(
            source_id=source.id,
            title="Test Article",
            url="https://test.com/article2",
            content_hash="test_hash_fav_456",
            fetched_at=pytest.import_module("datetime").datetime.utcnow(),
        )
        db_session.add(article)
        db_session.commit()
        db_session.refresh(article)
        
        # 添加收藏
        bookmark = Bookmark(
            user_id=test_user.id,
            article_id=article.id,
        )
        db_session.add(bookmark)
        db_session.commit()
        
        # 尝试再次添加
        response = client.post(
            "/api/favorites",
            headers=auth_headers,
            params={"article_id": str(article.id)}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Already bookmarked" in response.json()["detail"]
    
    def test_remove_favorite(self, client, auth_headers, db_session, test_user):
        """测试移除收藏"""
        from app.models.article import Article
        from app.models.bookmark import Bookmark
        from app.models.source import Source, SourceType
        
        # 创建信源和文章
        source = Source(
            name="Test Source",
            type=SourceType.RSS,
            config={"feed_url": "https://test.com/feed"},
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        article = Article(
            source_id=source.id,
            title="Test Article",
            url="https://test.com/article3",
            content_hash="test_hash_fav_789",
            fetched_at=pytest.import_module("datetime").datetime.utcnow(),
        )
        db_session.add(article)
        db_session.commit()
        db_session.refresh(article)
        
        # 添加收藏
        bookmark = Bookmark(
            user_id=test_user.id,
            article_id=article.id,
        )
        db_session.add(bookmark)
        db_session.commit()
        db_session.refresh(bookmark)
        
        # 移除收藏
        response = client.delete(
            f"/api/favorites/{bookmark.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestTagsAPI:
    """标签 API 测试类"""
    
    def test_list_tags(self, client, auth_headers):
        """测试列出标签"""
        response = client.get("/api/favorites/tags", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
    
    def test_create_tag(self, client, auth_headers):
        """测试创建标签"""
        response = client.post(
            "/api/favorites/tags",
            headers=auth_headers,
            params={
                "name": "AI",
                "color": "#3b82f6"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "AI"
        assert data["color"] == "#3b82f6"
    
    def test_create_duplicate_tag(self, client, auth_headers, db_session, test_user):
        """测试创建重复标签"""
        from app.models.bookmark import Tag
        
        # 创建已有标签
        tag = Tag(
            name="LLM",
            user_id=test_user.id,
            color="#22c55e"
        )
        db_session.add(tag)
        db_session.commit()
        
        # 尝试再次创建
        response = client.post(
            "/api/favorites/tags",
            headers=auth_headers,
            params={"name": "LLM"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_delete_tag(self, client, auth_headers, db_session, test_user):
        """测试删除标签"""
        from app.models.bookmark import Tag
        
        # 创建标签
        tag = Tag(
            name="ToDelete",
            user_id=test_user.id,
            color="#6366f1"
        )
        db_session.add(tag)
        db_session.commit()
        db_session.refresh(tag)
        
        # 删除标签
        response = client.delete(
            f"/api/favorites/tags/{tag.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
