from datetime import datetime, timedelta

from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from models import Lesson, Teacher, Course
from templates import templates


async def root(request: Request):
    if date := request.query_params.get('date'):
        today = datetime.strptime(date, '%Y-%m-%d')
    else:
        today = datetime.today()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    lessons = await Lesson.get_all_lessons_for_day(today)

    teachers = await Teacher.get_teachers()
    courses = await Course.get_courses()

    one_and_half_hours = timedelta(hours=1, minutes=30)
    return templates.TemplateResponse('index.html', {'request': request,
                                                     'lessons': lessons,
                                                     'one_and_half_hours': one_and_half_hours,
                                                     'today': today,
                                                     'teachers': teachers,
                                                     'courses': courses
                                                     })


@requires("authenticated")
async def add_lesson(request: Request):
    form = await request.form()
    lessons = await Lesson.check_if_busy(int(form["teacher"]), datetime.strptime(form['date'], '%Y-%m-%dT%H:%M'))
    if lessons:
        teacher = await Teacher.get_teacher_by_id(int(form['teacher']))
        return JSONResponse(
            {'message': f'{teacher.name} is busy doing {lessons[0].course.name} at this time or resting!'})

    await Lesson.add_lesson(
        int(form['course']),
        int(form['teacher']),
        datetime.strptime(form['date'], '%Y-%m-%dT%H:%M')
    )

    return JSONResponse(
        {'url': f"/?date={datetime.strftime(datetime.strptime(form['date'], '%Y-%m-%dT%H:%M'), '%Y-%m-%d')}"})


@requires("authenticated")
async def delete_lesson(request: Request):
    id = int(request.query_params.get('id'))
    lesson = await Lesson.get_lesson_by_id(id)
    await Lesson.delete_lesson(id)
    return RedirectResponse(f'/?date={lesson.start.strftime("%Y-%m-%d")}')