from starlette.authentication import requires
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import JSONResponse

from database import async_session
from models import User
from templates import templates


@requires("authenticated")
async def users(request: Request):
    users = await User.get_users()
    return templates.TemplateResponse('users.html', {'request': request,
                                                     'users': users,
                                                     })


@requires("authenticated")
async def add_user(request: Request):
    form = await request.form()
    if await User.get_user_by_username(form['username']):
        return JSONResponse({'message': f'User already exists!'})

    await User.add_user(
        form['username'],
        pbkdf2_sha256.hash(form['password'])
    )
    return JSONResponse({'url': '/users'})


@requires("authenticated")
async def delete_user(request: Request):
    form = await request.form()
    id = int(form['id'])
    if request.user.user_id == id:
        return JSONResponse({'message': 'You can\'t delete yourself, mate!'})

    if id == 1:
        return JSONResponse({'message': 'You can\'t delete admin, mate!'})

    users = await User.get_users()
    if len(users) == 1:
        return JSONResponse({'message': 'This is the last user!'})

    await User.delete_user(id)
    return JSONResponse({'url': '/users'})


@requires("authenticated")
async def change_password(request: Request):
    form = await request.form()
    async with async_session() as session:
        if user := await User.get_user_by_id(int(form['username'])):
            user.password = pbkdf2_sha256.hash(form["password"])
            session.add(user)
            await session.commit()

    return JSONResponse({'url': '/users'})
