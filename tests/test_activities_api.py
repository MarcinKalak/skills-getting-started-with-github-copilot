import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Chess Club"
EXISTING_EMAIL = "student@example.com"


@pytest.fixture
def client(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client):
    # Arrange
    expected_participants = [EXISTING_EMAIL]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[ACTIVITY_NAME]["participants"] == expected_participants


def test_signup_adds_participant(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {ACTIVITY_NAME}"}
    assert app_module.activities[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL, email]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert app_module.activities[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "new-student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {ACTIVITY_NAME}"}
    assert app_module.activities[ACTIVITY_NAME]["participants"] == []


def test_unregister_returns_not_found_for_missing_participant(client):
    # Arrange
    email = "not-signed-up@example.com"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert app_module.activities[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": EXISTING_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
