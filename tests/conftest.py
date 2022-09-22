import pytest
from async_asgi_testclient import TestClient
from asyncpg import ObjectInUseError
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine

from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE
from database import engine, async_session
from main import app
from models import Base, User

DATABASE_URL = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE
)

DATABASE_URL_SYNC = "postgresql://{}:{}@{}:{}/{}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE
)


@pytest.fixture(scope="session")
def anyio_backend():
    """Session fixture specifying asynchronous backend in session scope"""
    return "asyncio"


async def create_test_db():
    """
    Connects to 'postgres' of specified in config PostgreSQL server with inner async engine,
    checks if there is already existing test database, drops it if exists and creates a new one.
    """
    _engine = create_async_engine("postgresql+asyncpg://{}:{}@{}:{}/postgres".format(
        POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
    ))
    print("Dropping old test database...")
    async with _engine.begin() as conn:
        try:
            conn = await conn.execution_options(autocommit=False)
            await conn.execute(text("ROLLBACK"))
            await conn.execute(text(f"DROP DATABASE {POSTGRES_DATABASE}"))
        except (ProgrammingError, DBAPIError):
            print("Could not drop the database, probably does not exist.")
            await conn.execute(text("ROLLBACK"))
        except ObjectInUseError:
            print("Could not drop database because it's being accessed by other users (psql prompt open?)")
            await conn.execute(text("ROLLBACK"))
        print(f"Old test database dropped! About to create {POSTGRES_DATABASE}.")
        await conn.execute(text(f"CREATE DATABASE {POSTGRES_DATABASE}"))
        await conn.close()
        print("Test database created.")


async def drop_test_db():
    """
    Connects to 'postgres' of specified in config PostgreSQL server with inner async engine,
    disposes all existing connections of service engine (dunno why, but there is some connections after tests
    execution even tho I'm using context managers to access db from service) and drops test database.
    """
    _engine = create_async_engine(
        "postgresql+asyncpg://{}:{}@{}:{}/postgres".format(
            POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
        )
    )
    await engine.dispose()
    print("Dropping old test database...")
    async with _engine.begin() as conn:
        conn = await conn.execution_options(autocommit=False)
        await conn.execute(text("ROLLBACK"))
        await conn.execute(text(f"DROP DATABASE {POSTGRES_DATABASE}"))


@pytest.fixture(scope="session", autouse=True)
async def create_and_drop_database():
    """
    Creates test database before any tests are executed and drops it when all tests are done.
    """
    await create_test_db()
    yield
    await drop_test_db()


@pytest.fixture(scope="function", autouse=True)
async def fill_and_clear_database():
    """
    Prepares database for test execution, creates all tables before and drops them after.

    Because of that approach, we can isolate every test from each other
    and always have predictable ID's of inserted rows.
    But if you can pass session as an argument to some function, and you don't care about PK value,
    you can roll back session instead of dropping and creating schema.
    """
    async with engine.connect() as connection:
        await connection.begin()
        await connection.run_sync(Base.metadata.create_all)
        await connection.execute(text("COMMIT"))
        yield
        await connection.run_sync(Base.metadata.drop_all)
        await connection.execute(text("COMMIT"))
        await connection.close()


@pytest.fixture(scope="function")
async def session():
    """
    Session fixture, if you need to work with database directly.
    You can use context manager here too, tho.
    """
    session = async_session()
    await session.begin()
    yield session
    await session.close()


@pytest.fixture(scope="function")
async def authorized(session):
    async with TestClient(app) as client:
        url = app.url_path_for(name="login")
        session.add(User(username='admin', password='$pbkdf2-sha256$29000$4fxfq5UyJiREqPV.j3Eu5Q$5VjtGw6z/1dS77qWe6Bx8S6lzod7XoUGHoxsnktZEQ0'))
        await session.commit()

        response = await client.post(url, form={'username': 'admin', 'password': 'P@ssw0rd'})
        return response.cookies
