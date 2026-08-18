import pytest


class TestSignupHappyPath:
    """Happy path signup tests"""

    def test_signup_new_student(self, client, sample_activity_name, sample_email):
        """Test successful signup for a new student"""
        # Arrange
        activity = sample_activity_name
        email = sample_email

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_adds_participant(self, client, sample_activity_name, sample_email):
        """Test that signup actually adds the participant to the activity"""
        # Arrange
        activity = sample_activity_name
        email = sample_email

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")

        # Assert - Verify participant was added by fetching activities
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]

    def test_signup_multiple_students(self, client, sample_activity_name):
        """Test multiple students can sign up for same activity"""
        # Arrange
        activity = sample_activity_name
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]

        # Act
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

        # Assert - Verify all were added
        response = client.get("/activities")
        activities = response.json()
        for email in emails:
            assert email in activities[activity]["participants"]


class TestSignupErrors:
    """Error condition tests for signup"""

    def test_signup_activity_not_found(self, client, sample_email):
        """Test signup fails with 404 when activity doesn't exist"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = sample_email

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student(self, client, sample_activity_name):
        """Test signup fails with 400 when student already signed up"""
        # Arrange
        activity = sample_activity_name
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_full(self, client):
        """Test signup fails with 400 when activity is at capacity"""
        # Arrange - Tennis Club has max 16 participants, currently has 1
        activity = "Tennis Club"
        emails_to_add = [f"student{i}@mergington.edu" for i in range(15)]
        over_capacity_email = "overflow@mergington.edu"

        # Act - Fill the activity to capacity
        for email in emails_to_add:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

        # Act - Try to add one more (should fail)
        response = client.post(
            f"/activities/{activity}/signup?email={over_capacity_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "Activity is full" in response.json()["detail"]


class TestSignupEdgeCases:
    """Edge case tests for signup"""

    def test_signup_email_with_special_chars(self, client, sample_activity_name):
        """Test signup works with special character emails"""
        # Arrange
        activity = sample_activity_name
        email = "test+special@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_signup_email_with_uppercase(self, client, sample_activity_name):
        """Test signup works with uppercase email"""
        # Arrange
        activity = sample_activity_name
        email = "Test@MERGINGTON.EDU"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_signup_response_format(self, client, sample_activity_name, sample_email):
        """Test signup response has correct format"""
        # Arrange
        activity = sample_activity_name
        email = sample_email

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
