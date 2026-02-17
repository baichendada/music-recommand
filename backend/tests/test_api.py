"""
Unit tests for backend API
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealth:
    """Health check endpoints"""

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestAuth:
    """Authentication endpoints"""

    def test_register_user(self):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser123",
                "email": "test123@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser123"

    def test_register_duplicate_username(self):
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "email": "dup1@example.com",
                "password": "pass123"
            }
        )
        # Second registration (should fail)
        response = client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "email": "dup2@example.com",
                "password": "pass123"
            }
        )
        assert response.status_code == 400

    def test_login_success(self):
        # Register first
        client.post(
            "/api/auth/login",
            json={
                "username": "logintest",
                "password": "testpass123"
            }
        )
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "username": "logintest",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self):
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "wrongpass"
            }
        )
        assert response.status_code == 401


class TestMusic:
    """Music endpoints"""

    def test_get_music_list(self):
        response = client.get("/api/music")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_music_by_id(self):
        response = client.get("/api/music/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_get_music_not_found(self):
        response = client.get("/api/music/99999")
        assert response.status_code == 404

    def test_search_music(self):
        response = client.get("/api/music/search?q=周杰伦")
        assert response.status_code == 200


class TestEmotion:
    """Emotion endpoints"""

    def test_record_emotion_requires_auth(self):
        response = client.post(
            "/api/emotion",
            json={
                "emotion_type": "happy",
                "intensity": 1.0
            }
        )
        assert response.status_code == 403  # No auth

    def test_record_emotion_with_auth(self):
        # Login first
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "logintest",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]

        # Record emotion
        response = client.post(
            "/api/emotion",
            json={
                "emotion_type": "happy",
                "intensity": 0.8
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201


class TestRecommendation:
    """Recommendation endpoints"""

    def test_get_recommendations_requires_auth(self):
        response = client.get("/api/recommend")
        assert response.status_code == 403

    def test_get_recommendations_with_auth(self):
        # Login first
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "logintest",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]

        # Get recommendations
        response = client.get(
            "/api/recommend",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data

    def test_get_recommendations_by_emotion(self):
        response = client.get("/api/recommend/by-emotion/happy?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAI:
    """AI analysis endpoints"""

    def test_analyze_emotion_with_lyrics(self):
        response = client.post(
            "/api/ai/analyze/emotion",
            json={
                "lyrics": "亲爱的 爱上你 从那天起 甜蜜的很轻易"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "primary_emotion" in data
        assert data["primary_emotion"] == "happy"

    def test_analyze_sad_lyrics(self):
        response = client.post(
            "/api/ai/analyze/emotion",
            json={
                "lyrics": "为你弹奏肖邦的夜曲 纪念我死去的爱情"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["primary_emotion"] == "sad"

    def test_analyze_lyrics_endpoint(self):
        response = client.post(
            "/api/ai/analyze/lyrics",
            json={
                "lyrics": "快乐的心情 幸福的笑容"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
