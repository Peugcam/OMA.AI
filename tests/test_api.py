"""
API Integration Tests
=====================

Test suite for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.models import VideoBriefing, VideoStyle, VideoTone


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_briefing():
    """Sample video briefing for tests"""
    return {
        "title": "Test Video",
        "description": "This is a test video description for testing purposes.",
        "duration": 30,
        "target_audience": "Test audience",
        "style": "professional",
        "tone": "neutral",
        "cta": "Test CTA"
    }


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client):
        """Test /health endpoint"""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]
        assert "version" in data
        assert "uptime_seconds" in data
        assert "checks" in data

    def test_readiness_check(self, client):
        """Test /ready endpoint"""
        response = client.get("/api/v1/ready")

        assert response.status_code == 200
        data = response.json()

        assert "ready" in data
        assert isinstance(data["ready"], bool)

    def test_ping(self, client):
        """Test /ping endpoint"""
        response = client.get("/api/v1/ping")

        assert response.status_code == 200
        data = response.json()

        assert data == {"ping": "pong"}


class TestVideoEndpoints:
    """Test video generation endpoints"""

    def test_generate_video_success(self, client, sample_briefing):
        """Test successful video generation request"""
        response = client.post(
            "/api/v1/videos/generate",
            json={"briefing": sample_briefing, "async_mode": False}
        )

        assert response.status_code == 202
        data = response.json()

        assert data["success"] is True
        assert "task_id" in data
        assert data["task_id"].startswith("video_")

    def test_generate_video_invalid_duration(self, client, sample_briefing):
        """Test video generation with invalid duration"""
        sample_briefing["duration"] = 500  # Too long

        response = client.post(
            "/api/v1/videos/generate",
            json={"briefing": sample_briefing}
        )

        assert response.status_code == 422
        data = response.json()

        assert "error" in data
        assert data["error"] == "ValidationError"

    def test_generate_video_missing_title(self, client, sample_briefing):
        """Test video generation without title"""
        del sample_briefing["title"]

        response = client.post(
            "/api/v1/videos/generate",
            json={"briefing": sample_briefing}
        )

        assert response.status_code == 422

    def test_get_video_status_not_found(self, client):
        """Test getting status of non-existent task"""
        response = client.get("/api/v1/videos/status/nonexistent_task")

        assert response.status_code == 404
        data = response.json()

        assert "error" in data
        assert data["error"] == "ResourceNotFoundError"

    def test_list_tasks(self, client):
        """Test listing all tasks"""
        response = client.get("/api/v1/videos/tasks")

        assert response.status_code == 200
        data = response.json()

        assert "tasks" in data
        assert "total" in data
        assert isinstance(data["tasks"], list)


class TestStatisticsEndpoints:
    """Test statistics endpoints"""

    def test_get_stats(self, client):
        """Test /stats endpoint"""
        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        data = response.json()

        assert "total_videos_generated" in data
        assert "total_cost" in data
        assert "average_generation_time" in data
        assert "success_rate" in data
        assert "uptime_seconds" in data


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root(self, client):
        """Test / endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"


class TestValidation:
    """Test Pydantic model validation"""

    def test_video_style_enum(self):
        """Test VideoStyle enum validation"""
        assert VideoStyle.PROFESSIONAL.value == "professional"
        assert VideoStyle.MODERN.value == "modern"

    def test_video_tone_enum(self):
        """Test VideoTone enum validation"""
        assert VideoTone.NEUTRAL.value == "neutral"
        assert VideoTone.ENTHUSIASTIC.value == "enthusiastic"

    def test_briefing_validation(self):
        """Test VideoBriefing validation"""
        briefing = VideoBriefing(
            title="Test",
            description="Test description for validation",
            duration=30
        )

        assert briefing.title == "Test"
        assert briefing.duration == 30
        assert briefing.style == VideoStyle.PROFESSIONAL  # Default

    def test_briefing_invalid_duration(self):
        """Test VideoBriefing with invalid duration"""
        with pytest.raises(ValueError):
            VideoBriefing(
                title="Test",
                description="Test description",
                duration=5  # Too short (< 15)
            )


class TestErrorHandling:
    """Test error handling"""

    def test_validation_error_format(self, client):
        """Test validation error response format"""
        response = client.post(
            "/api/v1/videos/generate",
            json={"briefing": {"title": "ab"}}  # Too short
        )

        assert response.status_code == 422
        data = response.json()

        assert "error" in data
        assert "message" in data
        assert "details" in data
        assert "request_id" in data

    def test_not_found_error_format(self, client):
        """Test not found error response format"""
        response = client.get("/api/v1/videos/status/fake_id")

        assert response.status_code == 404
        data = response.json()

        assert "error" in data
        assert "message" in data
        assert "details" in data
