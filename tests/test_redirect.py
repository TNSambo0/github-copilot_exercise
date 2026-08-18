import pytest


class TestRedirect:
    """Tests for GET / redirect"""

    def test_redirect_status(self, client):
        """Test that GET / returns redirect status"""
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307  # Temporary redirect

    def test_redirect_location(self, client):
        """Test that redirect points to /static/index.html"""
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert "location" in response.headers
        assert "/static/index.html" in response.headers["location"]

    def test_redirect_follows_to_html(self, client):
        """Test that following redirect works (no 404)"""
        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
