from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from models import Teacher
from templates import templates


@requires("authenticated")
async def teachers(request: Request):
    teachers = await Teacher.get_teachers()
    return templates.TemplateResponse('teachers.html', {'request': request,
                                                        'teachers': teachers,
                                                        })


@requires("authenticated")
async def add_teacher(request: Request):
    form = await request.form()
    await Teacher.add_teacher(
        form['name'],
        form['phone'],
        form['email']
    )
    return RedirectResponse('/teachers')


@requires("authenticated")
async def delete_teacher(request: Request):
    form = await request.form()
    id = int(form['id'])
    teacher = await Teacher.get_teacher_by_id(id)
    if teacher.lesson:
        return JSONResponse({'message': f'{teacher.name} still got some lessons to give!'})

    await Teacher.delete_teacher(id)
    return JSONResponse({'url': '/teachers'})
