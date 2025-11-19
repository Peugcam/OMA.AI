"""
Tests for State Manager
"""

import pytest
import tempfile
from pathlib import Path
from core.state_manager import StateManager


class TestStateManager:
    """Test SQLite state manager"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        yield db_path

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def test_create_state_manager(self, temp_db):
        """Test creating state manager"""
        sm = StateManager(temp_db)
        assert sm.db_path == Path(temp_db)
        sm.close()

    def test_save_request(self, temp_db):
        """Test saving request"""
        sm = StateManager(temp_db)

        state = {
            "brief": {"title": "Test"},
            "current_phase": 1
        }

        sm.save_request("req123", state, status="in_progress")

        # Verify saved
        req = sm.get_request("req123")
        assert req is not None
        assert req['request_id'] == "req123"
        assert req['status'] == "in_progress"
        assert req['state']['brief']['title'] == "Test"

        sm.close()

    def test_update_status(self, temp_db):
        """Test updating request status"""
        sm = StateManager(temp_db)

        state = {"test": "data"}
        sm.save_request("req123", state, status="pending")

        # Update status
        sm.update_status("req123", "in_progress")

        req = sm.get_request("req123")
        assert req['status'] == "in_progress"

        # Update to completed
        sm.update_status("req123", "completed")

        req = sm.get_request("req123")
        assert req['status'] == "completed"

        sm.close()

    def test_list_requests(self, temp_db):
        """Test listing requests"""
        sm = StateManager(temp_db)

        # Create multiple requests
        sm.save_request("req1", {"data": 1}, status="completed")
        sm.save_request("req2", {"data": 2}, status="in_progress")
        sm.save_request("req3", {"data": 3}, status="completed")
        sm.save_request("req4", {"data": 4}, status="failed")

        # List all
        all_requests = sm.list_requests()
        assert len(all_requests) == 4

        # List by status
        completed = sm.list_requests(status="completed")
        assert len(completed) == 2

        in_progress = sm.list_requests(status="in_progress")
        assert len(in_progress) == 1

        failed = sm.list_requests(status="failed")
        assert len(failed) == 1

        sm.close()

    def test_get_stats(self, temp_db):
        """Test getting statistics"""
        sm = StateManager(temp_db)

        # Create requests with different statuses
        sm.save_request("req1", {}, status="completed")
        sm.save_request("req2", {}, status="completed")
        sm.save_request("req3", {}, status="in_progress")
        sm.save_request("req4", {}, status="failed")

        stats = sm.get_stats()

        assert stats['total'] == 4
        assert stats['completed'] == 2
        assert stats['in_progress'] == 1
        assert stats['failed'] == 1
        assert stats['success_rate'] == 50.0  # 2/4 = 50%

        sm.close()

    def test_delete_request(self, temp_db):
        """Test deleting request"""
        sm = StateManager(temp_db)

        sm.save_request("req123", {"data": "test"})

        # Verify exists
        assert sm.get_request("req123") is not None

        # Delete
        sm.delete_request("req123")

        # Verify deleted
        assert sm.get_request("req123") is None

        sm.close()

    def test_save_with_result(self, temp_db):
        """Test saving request with result"""
        sm = StateManager(temp_db)

        state = {"brief": {}}
        result = {"video_path": "/path/to/video.mp4"}

        sm.save_request(
            "req123",
            state,
            status="completed",
            result=result
        )

        req = sm.get_request("req123")
        assert req['status'] == "completed"
        assert req['result']['video_path'] == "/path/to/video.mp4"

        sm.close()

    def test_save_with_error(self, temp_db):
        """Test saving request with error"""
        sm = StateManager(temp_db)

        state = {"brief": {}}

        sm.save_request(
            "req123",
            state,
            status="failed",
            error="API timeout"
        )

        req = sm.get_request("req123")
        assert req['status'] == "failed"
        assert req['error'] == "API timeout"

        sm.close()
