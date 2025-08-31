import pytest


# Register
@pytest.mark.asyncio
async def test_register_user(client, user1_test_data):
    result = await client.post("/auth/register", json=user1_test_data)
    assert result.status_code == 201


@pytest.mark.asyncio
async def test_register_user_already_exist(client, user1_test_data):
    first = await client.post("/auth/register", json=user1_test_data)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=user1_test_data)
    assert second.status_code == 409
    assert second.json()["error"]["message"] == "User already exists"


@pytest.mark.asyncio
async def test_register_user_with_bad_data(client, user3_bad_test_data):
    result = await client.post("/auth/register", json=user3_bad_test_data)
    assert result.status_code == 422


# Login
@pytest.mark.asyncio
async def test_login_user(client, user1_test_data):
    await client.post("/auth/register", json=user1_test_data)

    result = await client.post(
        "/auth/login",
        data={
            "username": user1_test_data["email"],
            "password": user1_test_data["password"]
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    assert "access_token" in result.json()


@pytest.mark.asyncio
async def test_login_user_with_bad_password(client, user1_test_data):
    await client.post("/auth/register", json=user1_test_data)

    result = await client.post(
        "/auth/login",
        data={
            "username": user1_test_data["email"],
            "password": "FastAPI12345",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    assert result.status_code == 401
    assert result.json()["error"]["message"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test_login_user_with_bad_email(client, user1_test_data):
    await client.post("/auth/register", json=user1_test_data)

    result = await client.post(
        "/auth/login",
        data={
            "username": "test@gmail.com",
            "password": user1_test_data["password"],
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    assert result.status_code == 404
    assert result.json()["error"]["message"] == "User not found"


@pytest.mark.asyncio
async def test_login_not_found_user(client):
    result = await client.post(
        "/auth/login",
        data={
            "username": "test@gmail.com",
            "password": "FastAPI12345"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    assert result.status_code == 404
    assert result.json()["error"]["message"] == "User not found"


# Refresh
@pytest.mark.asyncio
async def test_refresh_token(client, user1_test_data):
    await client.post("/auth/register", json=user1_test_data)

    await client.post(
        "/auth/login",
        data={
            "username": user1_test_data["email"],
            "password": user1_test_data["password"]
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    refresh_token = client.cookies.get("refresh_token")
    client.cookies.set("refresh_token", refresh_token)
    result = await client.post("/auth/refresh")
    assert "access_token" in result.json()
