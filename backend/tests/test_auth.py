import pytest
from fastapi import status


def test_user_registration(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User"
    })
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_duplicate_registration_fails(client, test_user):
    response = client.post("/api/v1/auth/register", json={
        "email": test_user.email,
        "password": "AnotherPassword123!",
        "full_name": "Duplicate User"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_user_login_success(client, test_user):
    response = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "testpassword123"
    })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_user_login_wrong_password(client, test_user):
    response = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "WrongPassword!"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_profile(client, user_token_headers):
    response = client.get("/api/v1/auth/me", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "testuser@example.com"


def test_get_profile_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_flow(client, test_user):
    login_res = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "testpassword123"
    })
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_res.status_code == status.HTTP_200_OK
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_change_password(client, user_token_headers):
    response = client.post("/api/v1/auth/change-password", headers=user_token_headers, json={
        "current_password": "testpassword123",
        "new_password": "BrandNewPassword123!"
    })
    assert response.status_code == status.HTTP_200_OK

    # Re-login with new password
    login_res = client.post("/api/v1/auth/login", data={
        "username": "testuser@example.com",
        "password": "BrandNewPassword123!"
    })
    assert login_res.status_code == status.HTTP_200_OK
