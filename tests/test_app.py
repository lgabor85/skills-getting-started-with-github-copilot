"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities GET endpoint"""

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that /activities returns expected activities"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Basketball Team",
            "Drama Club",
        ]
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_duplicate_participant_returns_error(self):
        """Test that signing up twice for same activity returns error"""
        email = "duplicate@mergington.edu"
        # First signup
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup (duplicate)
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds the participant"""
        email = "verify@mergington.edu"
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis Club"]["participants"]


class TestUnregisterEndpoint:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        email = "remove@mergington.edu"
        # First signup
        client.post(f"/activities/Drama%20Club/signup?email={email}")
        # Then unregister
        response = client.delete(
            f"/activities/Drama%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "remove2@mergington.edu"
        # Signup
        client.post(f"/activities/Visual%20Arts/signup?email={email}")
        # Unregister
        client.delete(f"/activities/Visual%20Arts/unregister?email={email}")
        # Verify removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Visual Arts"]["participants"]

    def test_unregister_nonexistent_participant_returns_error(self):
        """Test that unregistering non-existent participant returns error"""
        response = client.delete(
            "/activities/Debate%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirects_to_index(self):
        """Test that / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
