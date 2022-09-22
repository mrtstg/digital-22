import uvicorn
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import select
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from auth.auth import JWTAuthenticationBackend
from auth.middleware import AuthenticationMiddleware
from config import SECRET_KEY, JWT_ALGORITHM, JWT_PREFIX, DATABASE_URL_SYNC
from models import User
from routes.courses import courses, add_course, delete_course
from routes.lessons import root, add_lesson, delete_lesson
from routes.login import login, refresh_token, logout
from routes.teachers import teachers, add_teacher, delete_teacher
from routes.users import users, add_user, delete_user, change_password

routes = [
    Route('/', endpoint=root, methods=["GET", "POST"]),
    Route('/login', endpoint=login, methods=["POST"], name='login'),
    Route('/logout', endpoint=logout, methods=["GET"], name='logout'),
    Route('/refresh_token', endpoint=refresh_token, methods=["POST"]),
    Mount('/static', app=StaticFiles(directory='static'), name="static"),
    Route('/lesson/add', endpoint=add_lesson, methods=["POST"]),
    Route('/lesson/delete', endpoint=delete_lesson, methods=["GET"]),
    Route('/teachers', endpoint=teachers, methods=["GET", "POST"]),
    Route('/teacher/add', endpoint=add_teacher, methods=["POST"]),
    Route('/teacher/delete', endpoint=delete_teacher, methods=["POST"]),
    Route('/courses', endpoint=courses, methods=["GET", "POST"]),
    Route('/course/add', endpoint=add_course, methods=["POST"]),
    Route('/course/delete', endpoint=delete_course, methods=["POST"]),
    Route('/users', endpoint=users, methods=["GET", "POST"]),
    Route('/user/add', endpoint=add_user, methods=["POST"], name='add_user'),
    Route('/user/delete', endpoint=delete_user, methods=["POST"]),
    Route('/user/change', endpoint=change_password, methods=["POST"]),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    ),
    Middleware(
        AuthenticationMiddleware,
        backend=JWTAuthenticationBackend(
            secret_key=str(SECRET_KEY),
            algorithm=JWT_ALGORITHM,
            prefix=JWT_PREFIX
        )
    ),
    Middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY
    )
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0')
