import pytest


class TestUnregisterHappyPath:
    """Happy path unregister tests"""

    def test_unregister_existing_participant(self, client, sample_activity_name):
        """Test successful unregister of existing participant"""
        # Arrange
        activity = sample_activity_name
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_unregister_removes_participant(self, client, sample_activity_name):
        """Test that unregister actually removes the participant"""
        # Arrange
        activity = sample_activity_name
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert - Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity]["participants"]

    def test_unregister_multiple_students(self, client, sample_activity_name):
        """Test unregistering multiple students"""
        # Arrange
        activity = sample_activity_name
        emails = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        for email in emails:
            response = client.delete(
                f"/activities/{activity}/unregister?email={email}"
            )
            assert response.status_code == 200

        # Assert - Verify all were removed
        response = client.get("/activities")
        activities = response.json()
        for email in emails:
            assert email not in activities[activity]["participants"]


class TestUnregisterErrors:
    """Error condition tests for unregister"""

    def test_unregister_activity_not_found(self, client):
        """Test unregister fails with 404 when activity doesn't exist"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_participant_not_signed_up(self, client, sample_activity_name):
        """Test unregister fails with 400 when student not signed up"""
        # Arrange
        activity = sample_activity_name
        email = "not.signed.up@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_already_removed(self, client, sample_activity_name):
        """Test unregister fails when trying to remove twice"""
        # Arrange
        activity = sample_activity_name
        email = "michael@mergington.edu"

        # Act - First unregister should succeed
        response1 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert first attempt
        assert response1.status_code == 200

        # Act - Second unregister should fail
        response2 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert second attempt
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"]
