from starlette.authentication import requires
from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from models import Course
from templates import templates


@requires("authenticated")
async def courses(request: Request):
    courses = await Course.get_courses()
    return templates.TemplateResponse('courses.html', {'request': request,
                                                       'courses': courses
                                                       })


@requires("authenticated")
async def add_course(request: Request):
    form = await request.form()
    await Course.add_course(
        form['name'],
        form['description']
    )
    return RedirectResponse('/courses')


@requires("authenticated")
async def delete_course(request: Request):
    form = await request.form()
    id = int(form['id'])
    course = await Course.get_course_by_id(id)
    if course.lesson:
        return JSONResponse({'message': f'{course.name} is used in schedule!'})

    await Course.delete_course(id)
    return JSONResponse({'url': '/courses'})
