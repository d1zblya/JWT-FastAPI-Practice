import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool

from src.core.config import settings
from src.database import session as database_session_module
from src.database.session import Base
from src.main import app


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        settings.db.TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(test_engine):
    TestAsyncSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
def override_get_db(session):
    async def _override_get_db():
        yield session

    return _override_get_db


@pytest_asyncio.fixture(scope="function")
async def app_with_db(override_get_db):
    app.dependency_overrides[database_session_module.get_session] = override_get_db  # type: ignore
    yield app
    app.dependency_overrides.clear()  # type: ignore


@pytest_asyncio.fixture(scope="function")
async def client(app_with_db):
    async with AsyncClient(
            transport=ASGITransport(app=app_with_db),
            base_url="http://test/api",
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
def user1_test_data():
    user = {
        "email": "test1@gmail.com",
        "first_name": "Ivan-first-name",
        "last_name": "Ivan-last-name",
        "phone": "+79999999999",
        "role": "user",
        "password": "Test1Password123"
    }
    return user


@pytest.fixture(scope="session")
def user1_test_update_data():
    new_user = {
        "email": "UPDATEtest1@gmail.com",
        "first_name": "UPDATE-Ivan-first-name",
        "last_name": "UPDATE-Ivan-last-name",
        "phone": "+71111111111",
        "role": "user",
        "password": "Test1Password123"
    }
    return new_user


@pytest.fixture(scope="session")
def user2_test_data():
    user = {
        "email": "test2@gmail.com",
        "first_name": "Oleg-first-name",
        "last_name": "Oleg-last-name",
        "phone": "+78888888888",
        "role": "business",
        "password": "Test2Password123"
    }
    return user


@pytest.fixture(scope="session")
def user3_bad_test_data():
    user = {
        "email": "test2@gmail.com",
        "first_name": "123Bob123",
        "last_name": "Oleg-last-name",
        "phone": "+78888888888",
        "role": "business",
        "password": "Test2Password123"
    }
    return user


@pytest_asyncio.fixture(scope="function")
async def get_access_token(client, user1_test_data):
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
    return result.json()["access_token"]
