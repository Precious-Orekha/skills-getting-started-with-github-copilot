"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create test client
client = TestClient(app)


class TestActivities:
    """Tests for getting activities"""
    
    def test_get_activities(self):
        """Test that we can retrieve all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        
        # Check for expected activities
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Studio",
            "Music Band",
            "Debate Team",
            "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in activities
    
    def test_activity_structure(self):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        # Test the first activity
        first_activity = activities["Chess Club"]
        
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        
        assert isinstance(first_activity["participants"], list)
        assert isinstance(first_activity["max_participants"], int)
    
    def test_chess_club_initial_participants(self):
        """Test that Chess Club has the expected initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_success(self):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]
    
    def test_signup_updates_participants(self):
        """Test that signup actually adds the participant"""
        # Get initial count
        response = client.get("/activities")
        initial_participants = len(response.json()["Programming Class"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Programming Class/signup?email=test1@mergington.edu"
        )
        
        # Check updated count
        response = client.get("/activities")
        updated_participants = len(response.json()["Programming Class"]["participants"])
        
        assert updated_participants == initial_participants + 1
        assert "test1@mergington.edu" in response.json()["Programming Class"]["participants"]
    
    def test_signup_duplicate_fails(self):
        """Test that signing up twice fails"""
        email = "duplicate@mergington.edu"
        activity = "Soccer Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 400
        
        result = response2.json()
        assert "already signed up" in result["detail"]
    
    def test_signup_invalid_activity(self):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_success(self):
        """Test successfully unregistering from an activity"""
        email = "unregister_test@mergington.edu"
        activity = "Art Studio"
        
        # First sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity in result["message"]
    
    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "removal_test@mergington.edu"
        activity = "Music Band"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify they're registered
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Verify they're not registered
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_unregister_not_registered_fails(self):
        """Test that unregistering someone not signed up fails"""
        response = client.post(
            "/activities/Debate Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "not signed up" in result["detail"]
    
    def test_unregister_invalid_activity(self):
        """Test unregistering from non-existent activity"""
        response = client.post(
            "/activities/Fake Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
