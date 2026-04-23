"""
test_sources.py - 信源管理 API 测试
"""

import pytest
from fastapi import status


class TestSourcesAPI:
    """信源管理 API 测试类"""
    
    def test_list_sources_empty(self, client, auth_headers):
        """测试空信源列表"""
        response = client.get("/api/sources", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_create_source_rss(self, client, auth_headers):
        """测试创建 RSS 信源"""
        response = client.post(
            "/api/sources",
            headers=auth_headers,
            json={
                "name": "机器之心",
                "type": "rss",
                "config": {"feed_url": "https://example.com/rss"}
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "机器之心"
        assert data["type"] == "rss"
        assert data["is_active"] == True
        assert "id" in data
    
    def test_create_source_github(self, client, auth_headers):
        """测试创建 GitHub 信源"""
        response = client.post(
            "/api/sources",
            headers=auth_headers,
            json={
                "name": "OpenAI Releases",
                "type": "github",
                "config": {"org": "openai", "repo": "chatgpt-release"}
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["type"] == "github"
        assert data["config"]["org"] == "openai"
    
    def test_create_source_twitter(self, client, auth_headers):
        """测试创建 Twitter 信源"""
        response = client.post(
            "/api/sources",
            headers=auth_headers,
            json={
                "name": "Karpathy",
                "type": "twitter",
                "config": {"account": "@karpathy"}
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["type"] == "twitter"
        assert "@karpathy" in data["config"]["account"]
    
    def test_create_source_invalid_type(self, client, auth_headers):
        """测试无效信源类型"""
        response = client.post(
            "/api/sources",
            headers=auth_headers,
            json={
                "name": "Test",
                "type": "invalid",
                "config": {}
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_source(self, client, auth_headers, db_session):
        """测试获取单个信源"""
        from app.models.source import Source, SourceType
        
        source = Source(
            name="Test Source",
            type=SourceType.RSS,
            config={"feed_url": "https://test.com/feed"},
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        response = client.get(f"/api/sources/{source.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Source"
    
    def test_get_source_not_found(self, client, auth_headers):
        """测试获取不存在的信源"""
        response = client.get(
            "/api/sources/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_source(self, client, auth_headers, db_session):
        """测试更新信源"""
        from app.models.source import Source, SourceType
        
        source = Source(
            name="Original Name",
            type=SourceType.RSS,
            config={"feed_url": "https://test.com/feed"},
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        response = client.put(
            f"/api/sources/{source.id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
    
    def test_toggle_source(self, client, auth_headers, db_session):
        """测试启禁用信源"""
        from app.models.source import Source, SourceType
        
        source = Source(
            name="Toggle Test",
            type=SourceType.RSS,
            config={"feed_url": "https://test.com/feed"},
            is_active=True,
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        response = client.patch(
            f"/api/sources/{source.id}/toggle",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] == False
        
        # 再切换回来
        response = client.patch(
            f"/api/sources/{source.id}/toggle",
            headers=auth_headers
        )
        
        assert response.json()["is_active"] == True
    
    def test_delete_source(self, client, auth_headers, db_session):
        """测试删除信源"""
        from app.models.source import Source, SourceType
        
        source = Source(
            name="To Delete",
            type=SourceType.RSS,
            config={"feed_url": "https://test.com/feed"},
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        response = client.delete(f"/api/sources/{source.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_filter_sources_by_type(self, client, auth_headers, db_session):
        """测试按类型筛选信源"""
        from app.models.source import Source, SourceType
        
        # 创建 RSS 信源
        rss_source = Source(
            name="RSS Source",
            type=SourceType.RSS,
            config={"feed_url": "https://rss.com/feed"},
        )
        db_session.add(rss_source)
        
        # 创建 GitHub 信源
        github_source = Source(
            name="GitHub Source",
            type=SourceType.GITHUB,
            config={"org": "test", "repo": "repo"},
        )
        db_session.add(github_source)
        db_session.commit()
        
        response = client.get("/api/sources?type=rss", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(s["type"] == "rss" for s in data["items"])

    def test_batch_delete_sources(self, client, auth_headers, db_session):
        """测试批量删除信源"""
        from app.models.source import Source, SourceType

        # 创建多个测试信源
        sources = []
        for i in range(3):
            source = Source(
                name=f"BatchTest Source {i}",
                type=SourceType.RSS,
                config={"feed_url": f"https://batch{i}.com/feed"},
            )
            db_session.add(source)
            sources.append(source)
        db_session.commit()
        for s in sources:
            db_session.refresh(s)

        source_ids = [sources[0].id, sources[1].id]

        response = client.post(
            "/api/sources/batch-delete",
            headers=auth_headers,
            json={"source_ids": source_ids}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted_count"] == 2
        assert data["total_requested"] == 2
        assert data["not_found_ids"] == []

        # 验证被删除的信源确实不存在了
        remaining_ids = [s.id for s in db_session.query(Source).all()]
        assert sources[0].id not in remaining_ids
        assert sources[1].id not in remaining_ids
        assert sources[2].id in remaining_ids

    def test_batch_delete_partial_not_found(self, client, auth_headers, db_session):
        """测试批量删除时部分 ID 不存在"""
        from app.models.source import Source, SourceType

        source = Source(
            name="Existing Source",
            type=SourceType.RSS,
            config={"feed_url": "https://test.com/feed"},
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)

        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            "/api/sources/batch-delete",
            headers=auth_headers,
            json={"source_ids": [source.id, fake_id]}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted_count"] == 1
        assert fake_id in data["not_found_ids"]

    def test_batch_delete_empty_list(self, client, auth_headers):
        """测试批量删除空列表"""
        response = client.post(
            "/api/sources/batch-delete",
            headers=auth_headers,
            json={"source_ids": []}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
