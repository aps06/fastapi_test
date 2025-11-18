from unittest.mock import MagicMock
from src.web13hm.database.models import User


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.web13hm.routes.auth.send_email", mock_send_email)

    response = client.post("/api/auth/signup", json=user)

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == user["username"]
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409
    assert response.json()["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user["username"], "password": user["password"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user["username"]).first()
    current_user.confirmed = True
    session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user["username"], "password": user["password"]},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user["username"], "password": "password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password"


def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": "email", "password": user["password"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email"
