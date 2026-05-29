from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_known_activity():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()


def test_signup_adds_participant_and_rejects_duplicate_signup():
    # Arrange
    activity_name = "Chess Club"
    email = "aaa-test.student@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    duplicate_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]
    assert duplicate_response.status_code == 400
    assert duplicate_response.json() == {"detail": "Student already signed up for this activity"}


def test_delete_participant_removes_participant_and_rejects_missing_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "aaa-delete.student@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    missing_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "Participant not found"}


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Robotics Club"
    email = "aaa-unknown.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
