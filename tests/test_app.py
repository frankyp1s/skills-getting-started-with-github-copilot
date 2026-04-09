from fastapi.testclient import TestClient
import pytest
from src.app import app, activities


class TestRootEndpoint:
    """Test suite for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """
        Arrange: A test client is ready
        Act: Make a GET request to root
        Assert: Verify redirect to /static/index.html
        """
        # Arrange
        expected_redirect = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect


class TestGetActivities:
    """Test suite for getting all activities"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: Activities database is populated
        Act: Make a GET request to /activities
        Assert: Verify all activities are returned
        """
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_returns_activity_details(self, client, reset_activities):
        """
        Arrange: Activities database exists
        Act: Retrieve activities and check one activity
        Assert: Verify activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data.get("Chess Club")

        # Assert
        assert response.status_code == 200
        assert chess_club is not None
        assert all(field in chess_club for field in required_fields)
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Test suite for activity signup functionality"""

    def test_signup_new_student_for_activity(self, client, reset_activities):
        """
        Arrange: Student not yet signed up for an activity
        Act: Sign up the student for the activity
        Assert: Verify signup was successful
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_participants = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert len(activities[activity_name]["participants"]) == initial_participants + 1
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_fails(self, client, reset_activities):
        """
        Arrange: Student already signed up for an activity
        Act: Attempt to sign up the same student again
        Assert: Verify signup fails with 400 status
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_for_nonexistent_activity_fails(self, client, reset_activities):
        """
        Arrange: Activity does not exist
        Act: Attempt to sign up for the non-existent activity
        Assert: Verify signup fails with 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_for_full_activity_fails(self, client, reset_activities):
        """
        Arrange: Activity is at max capacity
        Act: Attempt to sign up a new student when activity is full
        Assert: Verify signup fails with 400 status
        """
        # Arrange
        activity_name = "Tennis Club"
        # Tennis Club has max 10 participants
        # Fill it completely
        for i in range(10 - len(activities[activity_name]["participants"])):
            activities[activity_name]["participants"].append(f"filler{i}@mergington.edu")

        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"]

    def test_signup_updates_participant_list(self, client, reset_activities):
        """
        Arrange: Activity has existing participants
        Act: Sign up a new student
        Assert: Verify participant list is updated correctly
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]