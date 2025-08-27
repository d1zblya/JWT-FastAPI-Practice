import pytest


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
async def test_register_user_with_bad_data(client, user1_test_data):
    user1_test_data["first_name"] = "123Bob123"
    result = await client.post("/auth/register", json=user1_test_data)
    assert result.status_code == 422
