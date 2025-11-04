import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus


@pytest.mark.asyncio
async def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user(client, db_session):
    """Test user login"""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()
    
    # Test login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token(client, db_session):
    """Test token refresh"""
    # Create and login user
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
