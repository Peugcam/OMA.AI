"""
Integration tests for OMA.AI
Tests full video generation pipeline
"""

import pytest
import requests
import time
from redis import Redis

# Test configuration
API_BASE_URL = "http://localhost:7860"
REDIS_URL = "redis://localhost:6379"

class TestHealthChecks:
    """Test system health and readiness"""

    def test_dashboard_health(self):
        """Dashboard should be healthy"""
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        assert response.status_code == 200

    def test_redis_connection(self):
        """Redis should be accessible"""
        redis = Redis.from_url(REDIS_URL)
        assert redis.ping()

class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_enforced(self):
        """Rate limit should block excessive requests"""
        # Make 101 requests (limit is 100/hour)
        responses = []
        for i in range(101):
            resp = requests.post(
                f"{API_BASE_URL}/api/generate",
                json={"title": f"Test {i}"},
                timeout=2
            )
            responses.append(resp.status_code)

        # Last request should be rate limited
        assert 429 in responses

class TestVideoGeneration:
    """Test video generation pipeline"""

    @pytest.mark.slow
    def test_basic_video_generation(self):
        """Should generate a simple video"""
        payload = {
            "title": "Test Video",
            "description": "A test video about technology",
            "duration": 30,
            "style": "modern"
        }

        response = requests.post(
            f"{API_BASE_URL}/api/generate",
            json=payload,
            timeout=600  # 10 minutes
        )

        assert response.status_code == 200
        data = response.json()
        assert "video_url" in data
        assert data["status"] == "completed"

    @pytest.mark.slow
    def test_concurrent_generation(self):
        """Should handle multiple concurrent requests"""
        import concurrent.futures

        def generate_video(index):
            payload = {
                "title": f"Concurrent Test {index}",
                "description": "Testing concurrent generation",
                "duration": 15
            }
            resp = requests.post(
                f"{API_BASE_URL}/api/generate",
                json=payload,
                timeout=600
            )
            return resp.status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(generate_video, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed or be queued
        assert all(status in [200, 202] for status in results)

class TestCaching:
    """Test caching functionality"""

    def test_cache_hit(self):
        """Repeated requests should hit cache"""
        endpoint = f"{API_BASE_URL}/api/models"

        # First request
        resp1 = requests.get(endpoint)
        time1 = resp1.elapsed.total_seconds()

        # Second request (should be cached)
        resp2 = requests.get(endpoint)
        time2 = resp2.elapsed.total_seconds()

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert time2 < time1  # Cached should be faster

class TestSecurity:
    """Test security measures"""

    def test_sql_injection_blocked(self):
        """SQL injection attempts should be blocked"""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin'--",
        ]

        for payload in malicious_payloads:
            resp = requests.post(
                f"{API_BASE_URL}/api/generate",
                json={"title": payload},
                timeout=5
            )
            # Should either reject or sanitize
            assert resp.status_code in [400, 403, 422]

    def test_xss_sanitized(self):
        """XSS attempts should be sanitized"""
        xss_payload = "<script>alert('XSS')</script>"
        resp = requests.post(
            f"{API_BASE_URL}/api/generate",
            json={"title": xss_payload},
            timeout=5
        )

        # Should not execute script
        if resp.status_code == 200:
            assert "<script>" not in resp.text

class TestLoadAndPerformance:
    """Performance and load tests"""

    @pytest.mark.slow
    @pytest.mark.load
    def test_sustained_load(self):
        """System should handle sustained load"""
        duration_seconds = 60
        requests_per_second = 5
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0

        while time.time() - start_time < duration_seconds:
            try:
                resp = requests.get(f"{API_BASE_URL}/health", timeout=2)
                if resp.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
            except:
                failed_requests += 1

            time.sleep(1 / requests_per_second)

        success_rate = successful_requests / (successful_requests + failed_requests)
        assert success_rate > 0.95  # 95% success rate minimum

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
