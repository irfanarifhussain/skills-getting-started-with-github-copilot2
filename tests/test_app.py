from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]
    assert "max_participants" in response.json()["Chess Club"]


def test_signup_rejects_duplicate_email():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    duplicate_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert duplicate_response.status_code == 400
    assert "already signed up" in duplicate_response.json()["detail"].lower()

    activities[activity_name]["participants"] = [
        participant for participant in activities[activity_name]["participants"] if participant != email
    ]


def test_unregister_participant_removes_email():
    activity_name = "Programming Class"
    email = "teststudent@mergington.edu"

    client.post(f"/activities/{activity_name}/signup?email={email}")
    delete_response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert delete_response.status_code == 200
    assert email not in activities[activity_name]["participants"]
