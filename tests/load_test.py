"""
Load testing with Locust
Run with: locust -f tests/load_test.py --host=http://localhost:7860
"""

from locust import HttpUser, task, between
import random

class OMAUser(HttpUser):
    """Simulated user behavior for load testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when user starts"""
        # Check health before starting
        self.client.get("/health")

    @task(10)  # Weight: 10 (most common)
    def view_homepage(self):
        """User views homepage"""
        self.client.get("/")

    @task(5)
    def check_models(self):
        """User checks available models"""
        self.client.get("/api/models")

    @task(3)
    def browse_videos(self):
        """User browses generated videos"""
        self.client.get("/api/videos/recent")

    @task(1)  # Weight: 1 (least common)
    def generate_video(self):
        """User generates a video"""
        video_titles = [
            "Introduction to AI",
            "Cloud Computing Basics",
            "Machine Learning Tutorial",
            "Docker for Beginners",
            "Kubernetes Overview"
        ]

        payload = {
            "title": random.choice(video_titles),
            "description": f"Educational video about {random.choice(['technology', 'programming', 'DevOps'])}",
            "duration": random.choice([30, 60, 90]),
            "style": random.choice(["modern", "corporate", "educational"])
        }

        with self.client.post(
            "/api/generate",
            json=payload,
            catch_response=True,
            timeout=600
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limited")
            elif response.status_code == 202:
                response.success()  # Queued is OK
            else:
                response.failure(f"Failed with status {response.status_code}")
