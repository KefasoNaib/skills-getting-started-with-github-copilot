import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: save a deep copy of the original activities before a test
    and restore it afterward to avoid cross-test pollution.
    """
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_root_redirect():
    # Arrange: client already defined
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code in (307, 200)
    # 307 redirect should send location header to /static/index.html
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange
    expected = copy.deepcopy(activities)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_successful():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity]["participants"]
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_nonexistent_activity():
    # Arrange
    activity = "Nonexistent"
    email = "foo@bar.com"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404


def test_signup_already_registered():
    # Arrange
    activity = "Chess Club"
    # pick an existing participant
    email = activities[activity]["participants"][0]
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400


def test_unregister_successful():
    # Arrange
    activity = "Chess Club"
    # ensure a specific email is present
    email = activities[activity]["participants"][0]
    assert email in activities[activity]["participants"]
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_activity():
    # Arrange
    activity = "Nonexistent"
    email = "foo@bar.com"
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 404


def test_unregister_not_registered():
    # Arrange
    activity = "Chess Club"
    email = "absent@mergington.edu"
    assert email not in activities[activity]["participants"]
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 400
