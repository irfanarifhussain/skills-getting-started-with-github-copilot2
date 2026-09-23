from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    activities_response = response.json()
    assert response.status_code == 200
    assert "Chess Club" in activities_response
    assert "participants" in activities_response["Chess Club"]
    assert "max_participants" in activities_response["Chess Club"]


def test_signup_adds_student_to_activity(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_email(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_rejects_unknown_activity(client):
    activity_name = "Unknown Activity"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_full_activity(client):
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"
    activities[activity_name]["participants"] = [
        f"student{index}@mergington.edu"
        for index in range(activities[activity_name]["max_participants"])
    ]

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_requires_email(client):
    activity_name = "Chess Club"

    response = client.post(f"/activities/{activity_name}/signup")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_unregister_participant_removes_email(client):
    activity_name = "Programming Class"
    email = "teststudent@mergington.edu"
    activities[activity_name]["participants"].append(email)

    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}"
    }
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_unknown_activity(client):
    activity_name = "Unknown Activity"
    email = "teststudent@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_absent_participant(client):
    activity_name = "Programming Class"
    email = "missingstudent@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
