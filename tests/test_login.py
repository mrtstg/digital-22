import pytest
from async_asgi_testclient import TestClient

from main import app
from models import User


@pytest.mark.anyio
async def test_login(session):
    async with TestClient(app) as client:
        url = app.url_path_for(name="login")
        session.add(User(username='admin',
                         password='$pbkdf2-sha256$29000$4fxfq5UyJiREqPV.j3Eu5Q$5VjtGw6z/1dS77qWe6Bx8S6lzod7XoUGHoxsnktZEQ0'))
        await session.commit()

        response = await client.post(url, form={'username': 'admin', 'password': 'P@ssw0rd'})
        assert response.status_code == 200
        assert 'token' in response.cookies.keys()

        response = await client.post(url, form={'username': 'admin', 'password': 'password1'})
        assert response.status_code == 200
        assert response.json()['message'] == 'Wrong password!'
