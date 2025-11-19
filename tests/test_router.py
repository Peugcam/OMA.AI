"""
Tests for SmartRouter
"""

import pytest
from core.router import SmartRouter


class TestSmartRouter:
    """Test smart routing logic"""

    def test_router_creation(self):
        """Test creating router"""
        router = SmartRouter(enable_cache=True, enable_fallback=True)
        assert router.enable_cache is True
        assert router.enable_fallback is True

    def test_route_with_rules_no_script(self):
        """Test routing when no script exists"""
        router = SmartRouter(enable_cache=False, enable_fallback=True)

        state = {
            'script': None,
            'visual_plan': None,
            'audio_files': None,
            'video_path': None
        }

        decision = router.route(state)
        assert decision == "script_agent"

    def test_route_with_rules_no_visual(self):
        """Test routing when script exists but no visual"""
        router = SmartRouter(enable_cache=False, enable_fallback=True)

        state = {
            'script': {'scenes': []},
            'visual_plan': None,
            'audio_files': None,
            'video_path': None
        }

        decision = router.route(state)
        assert decision == "visual_agent"

    def test_route_with_rules_no_audio(self):
        """Test routing when script and visual exist but no audio"""
        router = SmartRouter(enable_cache=False, enable_fallback=True)

        state = {
            'script': {'scenes': []},
            'visual_plan': {'scenes': []},
            'audio_files': None,
            'video_path': None
        }

        decision = router.route(state)
        assert decision == "audio_agent"

    def test_route_with_rules_no_video(self):
        """Test routing when everything exists but no video"""
        router = SmartRouter(enable_cache=False, enable_fallback=True)

        state = {
            'script': {'scenes': []},
            'visual_plan': {'scenes': []},
            'audio_files': {'final': 'audio.mp3'},
            'video_path': None
        }

        decision = router.route(state)
        assert decision == "editor_agent"

    def test_route_with_rules_finished(self):
        """Test routing when everything is done"""
        router = SmartRouter(enable_cache=False, enable_fallback=True)

        state = {
            'script': {'scenes': []},
            'visual_plan': {'scenes': []},
            'audio_files': {'final': 'audio.mp3'},
            'video_path': '/path/to/video.mp4'
        }

        decision = router.route(state)
        assert decision == "FINISH"

    def test_cache_works(self):
        """Test that cache reduces calls"""
        router = SmartRouter(enable_cache=True, enable_fallback=True)

        state = {
            'script': None,
            'visual_plan': None,
            'audio_files': None,
            'video_path': None
        }

        # First call
        decision1 = router.route(state)
        initial_calls = router.stats['total_decisions']

        # Second call with same state (should hit cache)
        decision2 = router.route(state)

        assert decision1 == decision2
        assert router.stats['cache_hits'] > 0

    def test_stats_tracking(self):
        """Test that stats are tracked correctly"""
        router = SmartRouter(enable_cache=True, enable_fallback=True)

        state = {'script': None, 'visual_plan': None, 'audio_files': None, 'video_path': None}

        router.route(state)

        stats = router.stats
        assert stats['total_decisions'] >= 1
        assert 'cache_hits' in stats
        assert 'fallback_calls' in stats

    def test_clear_cache(self):
        """Test clearing cache"""
        router = SmartRouter(enable_cache=True)

        state = {'script': None, 'visual_plan': None, 'audio_files': None, 'video_path': None}

        # Make call to populate cache
        router.route(state)
        assert len(router.decision_cache) > 0

        # Clear cache
        router.clear_cache()
        assert len(router.decision_cache) == 0
