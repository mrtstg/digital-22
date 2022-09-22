import pytest
from async_asgi_testclient import TestClient
from sqlalchemy import select

from main import app
from models import User


@pytest.mark.anyio
async def test_delete_user(session, authorized):
    async with TestClient(app) as client:
        url = app.url_path_for(name="delete_user")

        session.add(User(username='user',
                         password='$pbkdf2-sha256$29000$4fxfq5UyJiREqPV.j3Eu5Q$5VjtGw6z/1dS77qWe6Bx8S6lzod7XoUGHoxsnktZEQ0'))
        await session.commit()

        response = await client.post(url, form={'id': '2'}, cookies=authorized)
        assert response.status_code == 200

        query = select(User).filter(User.username == 'user')
        results = await session.execute(query)
        user = results.scalars().first()
        assert not user
