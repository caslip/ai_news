"""
Unit tests for Writer module API endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.models.draft import Draft
from app.models.writer import WriterTemplate


class TestDraftsAPI:
    """Tests for /api/writer/drafts endpoints"""
    
    def test_list_drafts_empty(self, client, auth_headers):
        """Test listing drafts when empty"""
        response = client.get("/api/writer/drafts/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
    
    def test_list_drafts_with_items(self, client, auth_headers, test_draft, test_user):
        """Test listing drafts with items"""
        response = client.get("/api/writer/drafts/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["id"] == "draft-123"
    
    def test_list_drafts_pagination(self, client, auth_headers, db_session, test_user):
        """Test drafts pagination"""
        # Create multiple drafts
        for i in range(25):
            draft = Draft(
                title=f"Draft {i}",
                content=f"Content {i}",
                status="completed",
                word_count=10 + i,
                style="technical",
                tone="professional",
                length="medium",
                created_by=test_user.id,
            )
            db_session.add(draft)
        db_session.commit()
        
        # Test first page
        response = client.get("/api/writer/drafts/?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10
        
        # Test second page
        response = client.get("/api/writer/drafts/?page=2&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 2
    
    def test_list_drafts_filter_by_status(self, client, auth_headers, db_session, test_user):
        """Test filtering drafts by status"""
        # Create drafts with different statuses
        for status in ["generating", "completed", "failed"]:
            draft = Draft(
                title=f"Draft {status}",
                content=f"Content {status}",
                status=status,
                word_count=10,
                style="technical",
                tone="professional",
                length="medium",
                created_by=test_user.id,
            )
            db_session.add(draft)
        db_session.commit()
        
        # Filter by completed
        response = client.get("/api/writer/drafts/?status=completed", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "completed"
    
    def test_get_draft(self, client, auth_headers, test_draft):
        """Test getting a single draft"""
        response = client.get("/api/writer/drafts/draft-123", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "draft-123"
        assert data["title"] == "Test Draft"
        assert data["status"] == "completed"
    
    def test_get_draft_not_found(self, client, auth_headers):
        """Test getting non-existent draft"""
        response = client.get("/api/writer/drafts/nonexistent", headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_draft(self, client, auth_headers, test_draft):
        """Test deleting a draft"""
        response = client.delete("/api/writer/drafts/draft-123", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify deleted
        response = client.get("/api/writer/drafts/draft-123", headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_draft_not_found(self, client, auth_headers):
        """Test deleting non-existent draft"""
        response = client.delete("/api/writer/drafts/nonexistent", headers=auth_headers)
        assert response.status_code == 404
    
    def test_batch_delete_drafts(self, client, auth_headers, db_session, test_user):
        """Test batch deleting drafts"""
        # Create multiple drafts
        draft_ids = []
        for i in range(5):
            draft = Draft(
                title=f"Draft {i}",
                content=f"Content {i}",
                status="completed",
                word_count=10,
                style="technical",
                tone="professional",
                length="medium",
                created_by=test_user.id,
            )
            db_session.add(draft)
            db_session.flush()
            draft_ids.append(draft.id)
        db_session.commit()
        
        # Delete first 3
        response = client.post(
            "/api/writer/drafts/batch-delete",
            json={"draft_ids": draft_ids[:3]},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 3
    
    def test_batch_delete_empty(self, client, auth_headers):
        """Test batch delete with empty list"""
        response = client.post(
            "/api/writer/drafts/batch-delete",
            json={"draft_ids": []},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 0


class TestWriterStats:
    """Tests for /api/writer/drafts/stats endpoint"""
    
    def test_get_stats_empty(self, client, auth_headers):
        """Test stats with no drafts"""
        response = client.get("/api/writer/drafts/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["today_count"] == 0
        assert data["total_drafts"] == 0
        assert data["total_words"] == 0
    
    def test_get_stats_with_drafts(self, client, auth_headers, test_draft):
        """Test stats with drafts"""
        response = client.get("/api/writer/drafts/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_drafts"] == 1
        assert data["total_words"] == 10


class TestTemplatesAPI:
    """Tests for /api/writer/templates endpoints"""
    
    def test_list_templates(self, client, auth_headers):
        """Test listing templates (should auto-seed)"""
        response = client.get("/api/writer/templates/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should auto-seed default templates
        assert data["total"] > 0
        assert len(data["items"]) > 0
    
    def test_list_templates_with_items(self, client, auth_headers, test_template):
        """Test listing templates with custom template"""
        response = client.get("/api/writer/templates/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should have default + custom templates
        assert data["total"] >= 1
        template = next((t for t in data["items"] if t["id"] == "template-123"), None)
        assert template is not None
        assert template["name"] == "Test Template"
    
    def test_template_fields(self, client, auth_headers, test_template):
        """Test template has all required fields"""
        response = client.get("/api/writer/templates/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        template = next((t for t in data["items"] if t["id"] == "template-123"), None)
        assert template is not None
        
        required_fields = ["id", "name", "description", "category", "style", "tone", "length", "use_count", "created_at"]
        for field in required_fields:
            assert field in template


class TestGenerateAPI:
    """Tests for /api/writer/generate endpoint"""
    
    def test_generate_requires_source(self, client, auth_headers):
        """Test that generate requires source_url or source_content"""
        response = client.post(
            "/api/writer/generate",
            json={
                "style": "technical",
                "tone": "professional",
                "length": "medium",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "source_url or source_content" in response.json()["detail"]
    
    def test_generate_validation(self, client, auth_headers):
        """Test generate request validation"""
        # Invalid style
        response = client.post(
            "/api/writer/generate",
            json={
                "source_content": "Test content",
                "style": "invalid_style",
                "tone": "professional",
                "length": "medium",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error
        
        # Invalid tone
        response = client.post(
            "/api/writer/generate",
            json={
                "source_content": "Test content",
                "style": "technical",
                "tone": "invalid_tone",
                "length": "medium",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422
        
        # Invalid length
        response = client.post(
            "/api/writer/generate",
            json={
                "source_content": "Test content",
                "style": "technical",
                "tone": "professional",
                "length": "invalid_length",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestDraftModel:
    """Tests for Draft model"""
    
    def test_draft_creation(self, db_session, test_user):
        """Test creating a draft"""
        draft = Draft(
            title="My Draft",
            content="Draft content here",
            status="completed",
            word_count=3,
            style="technical",
            tone="professional",
            length="medium",
            created_by=test_user.id,
        )
        db_session.add(draft)
        db_session.commit()
        
        assert draft.id is not None
        assert draft.title == "My Draft"
        assert draft.created_at is not None
    
    def test_draft_word_count_calculation(self):
        """Test word count calculation"""
        draft = Draft(
            title="Test",
            content="One two three four five",
        )
        assert draft.calculate_word_count() == 5
    
    def test_draft_title_extraction(self):
        """Test title extraction from content"""
        from app.models.draft import extract_title_from_content
        
        # Test # Title format
        content = "# This is a Title\n\nSome content here."
        title = extract_title_from_content(content)
        assert title == "This is a Title"
        
        # Test empty content
        title = extract_title_from_content("")
        assert title == "Untitled"
        
        # Test no title format
        content = "Just some regular text without a title format."
        title = extract_title_from_content(content)
        assert title == "Just some regular text without a title format."
