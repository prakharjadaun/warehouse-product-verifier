import pytest


@pytest.mark.asyncio
async def test_create_user_and_login(authed_client):
    create_res = await authed_client.post(
        "/auth/users",
        json={"email": "newop@wms.com", "password": "secret123", "full_name": "New Operator", "role": "operator"},
    )
    assert create_res.status_code in [201, 400]  # 400 if email already exists from a prior run

    login_res = await authed_client.post(
        "/auth/login",
        data={"username": "newop@wms.com", "password": "secret123"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
    assert login_res.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/auth/login",
        data={"username": "nobody@wms.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_requires_auth(client):
    response = await client.post(
        "/auth/users",
        json={"email": "noauth@wms.com", "password": "pass", "full_name": "No Auth", "role": "operator"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_requires_auth(client):
    response = await client.get("/auth/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_with_admin_token(authed_client):
    response = await authed_client.get("/auth/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
