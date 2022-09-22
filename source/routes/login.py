from datetime import datetime, timedelta
from json import JSONDecodeError

from jwt import api_jwt as jwt
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from starlette.authentication import requires
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.templating import _TemplateResponse

from config import SECRET_KEY, JWT_PREFIX, JWT_ALGORITHM
from templates import templates
from models import User


async def create_token(token_config: dict) -> str:
    exp = datetime.utcnow() + timedelta(minutes=token_config["expiration_minutes"])
    token = {
        "username": token_config["username"],
        "user_id": token_config["user_id"],
        "iat": datetime.utcnow(),
        "exp": exp,
    }

    if "get_expired_token" in token_config:
        token["sub"] = "token"
    else:
        token["sub"] = "refresh_token"

    token = jwt.encode(token, str(SECRET_KEY), algorithm=JWT_ALGORITHM)
    return token  # .decode("UTF-8")


async def login(request: Request) -> JSONResponse | RedirectResponse:
    if not (form := await request.form()):
        return JSONResponse({'message': 'JSON missing!'}, status_code=400)

    username = form["username"]
    password = form["password"]

    if (user := await User.get_user_by_username(username)) is None:
        return JSONResponse({'message': 'User not found!'}, status_code=200)

    if not pbkdf2_sha256.verify(password, user.password):
        return JSONResponse({'message': 'Wrong password!'}, status_code=200)

    # user.last_login_date = datetime.now()
    # await user.save()

    token = await create_token(
        {"username": user.username, "user_id": user.id, "get_expired_token": 1, "expiration_minutes": 30})
    refresh_token = await create_token(
        {"username": user.username, "user_id": user.id, "get_refresh_token": 1, "expiration_minutes": 10080})

    response = JSONResponse({'url': '/'})

    response.set_cookie(
        key="token",
        value=f"{JWT_PREFIX} {token}"
    )
    response.set_cookie(
        key='refresh_token',
        value=f"{JWT_PREFIX} {refresh_token}"
    )

    return response


async def logout(request: Request) -> JSONResponse:
    response = RedirectResponse('/')

    response.delete_cookie(
        key="token"
    )
    response.set_cookie(
        key='refresh_token'
    )

    return response


async def refresh_token(request: Request) -> JSONResponse:
    username = request.user.username
    user_id = request.user.user_id

    token = await create_token(
        {"username": username, "user_id": user_id, "get_expired_token": 1, "expiration_minutes": 30})
    refresh_token = await create_token(
        {"username": username, "user_id": user_id, "get_refresh_token": 1, "expiration_minutes": 10080})

    return JSONResponse({"id": user_id, "username": username, "token": f"{JWT_PREFIX} {token}",
                         "refresh_token": f"{JWT_PREFIX} {refresh_token}", }, status_code=200)
