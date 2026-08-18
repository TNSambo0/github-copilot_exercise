import pytest


class TestStateTransitions:
    """Tests for state transitions and data consistency"""

    def test_signup_then_unregister_then_signup_again(self, client):
        """Test lifecycle: signup -> unregister -> signup again"""
        # Arrange
        activity = "Tennis Club"
        email = "cycle.test@mergington.edu"

        # Act & Assert - Initial signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Assert - Verify added
        resp_check1 = client.get("/activities")
        assert email in resp_check1.json()[activity]["participants"]

        # Act - Unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response2.status_code == 200

        # Assert - Verify removed
        resp_check2 = client.get("/activities")
        assert email not in resp_check2.json()[activity]["participants"]

        # Act - Signup again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response3.status_code == 200

        # Assert - Verify added again
        resp_check3 = client.get("/activities")
        assert email in resp_check3.json()[activity]["participants"]

    def test_multiple_concurrent_operations(self, client):
        """Test multiple operations on same activity"""
        # Arrange
        activity = "Art Studio"
        emails = [f"concurrent{i}@mergington.edu" for i in range(5)]

        # Act - Add all participants
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

        # Act - Remove some
        for email in emails[:2]:
            response = client.delete(f"/activities/{activity}/unregister?email={email}")
            assert response.status_code == 200

        # Assert - Verify final state
        resp = client.get("/activities")
        final_participants = resp.json()[activity]["participants"]

        for email in emails[:2]:
            assert email not in final_participants
        for email in emails[2:]:
            assert email in final_participants

    def test_availability_increases_after_unregister(self, client):
        """Test that available spots increase after unregistering"""
        # Arrange
        activity = "Drama Club"
        email = "drama.test@mergington.edu"

        # Act & Assert - Get initial participant count
        resp1 = client.get("/activities")
        initial_participants = len(resp1.json()[activity]["participants"])

        # Act - Add a participant
        client.post(f"/activities/{activity}/signup?email={email}")

        # Assert - Verify participant was added
        resp2 = client.get("/activities")
        after_signup = len(resp2.json()[activity]["participants"])
        assert after_signup == initial_participants + 1

        # Act - Remove the participant
        client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert - Verify participant count returned to original
        resp3 = client.get("/activities")
        after_unregister = len(resp3.json()[activity]["participants"])
        assert after_unregister == initial_participants

    def test_data_isolation_between_activities(self, client):
        """Test that operations on one activity don't affect others"""
        # Arrange
        email = "isolation@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act - Sign up for first activity
        client.post(f"/activities/{activity1}/signup?email={email}")

        # Assert - Verify only in first activity
        resp = client.get("/activities")
        assert email in resp.json()[activity1]["participants"]
        assert email not in resp.json()[activity2]["participants"]

        # Act - Sign up for second activity
        client.post(f"/activities/{activity2}/signup?email={email}")

        # Assert - Verify in both
        resp = client.get("/activities")
        assert email in resp.json()[activity1]["participants"]
        assert email in resp.json()[activity2]["participants"]

        # Act - Unregister from first
        client.delete(f"/activities/{activity1}/unregister?email={email}")

        # Assert - Verify only in second
        resp = client.get("/activities")
        assert email not in resp.json()[activity1]["participants"]
        assert email in resp.json()[activity2]["participants"]
