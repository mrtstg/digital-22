import pytest
from async_asgi_testclient import TestClient
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import select

from main import app
from models import User


@pytest.mark.anyio
async def test_add_user(session, authorized):
    async with TestClient(app) as client:
        url = app.url_path_for(name="add_user")

        response = await client.post(url, form={'username': 'user', 'password': 'P@ssw0rd'}, cookies=authorized)
        assert response.status_code == 200

        query = select(User).filter(User.username == 'user')
        results = await session.execute(query)
        user = results.scalars().first()
        assert user
        assert pbkdf2_sha256.verify('P@ssw0rd', user.password)
