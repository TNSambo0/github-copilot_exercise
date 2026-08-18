import pytest


class TestActivitiesListHappyPath:
    """Happy path tests for GET /activities"""

    def test_get_all_activities(self, client):
        """Test getting all activities returns success"""
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that /activities returns a dictionary"""
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_fields(self, client, sample_activity_name):
        """Test that activities contain expected fields"""
        # Act
        response = client.get("/activities")
        activities = response.json()
        activity = activities[sample_activity_name]

        # Assert
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_is_list(self, client, sample_activity_name):
        """Test that participants field is a list"""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert isinstance(activities[sample_activity_name]["participants"], list)

    def test_get_activities_count(self, client):
        """Test that we get expected number of activities"""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert len(activities) == 9  # 9 activities in the dataset

    def test_get_activities_specific_activity(self, client, sample_activity_name):
        """Test specific activity exists and has correct name"""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert sample_activity_name in activities


class TestActivitiesDataIntegrity:
    """Tests for data integrity in activities list"""

    def test_activities_have_max_participants(self, client):
        """Test all activities have max_participants as int"""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for name, activity in activities.items():
            assert isinstance(activity["max_participants"], int)
            assert activity["max_participants"] > 0

    def test_activities_participants_are_strings(self, client):
        """Test all participants are email strings"""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for name, activity in activities.items():
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Simple email validation

    def test_activities_participant_count_valid(self, client):
        """Test participant count doesn't exceed max"""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for name, activity in activities.items():
            assert len(activity["participants"]) <= activity["max_participants"]
