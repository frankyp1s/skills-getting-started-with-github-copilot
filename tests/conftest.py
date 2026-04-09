import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities to initial state after each test"""
    # Store original activities
    original_activities = {
        key: {
            **value,
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }

    yield

    # Restore original state
    activities.clear()
    activities.update(original_activities)