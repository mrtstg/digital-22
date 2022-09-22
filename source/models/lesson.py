from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship, selectinload, contains_eager
from sqlalchemy import select
from database import async_session

from models import Base, Teacher


class Lesson(Base):
    __tablename__ = "lesson"

    id = Column(Integer, primary_key=True, nullable=False)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=False)
    start = Column(DateTime)

    course = relationship("Course", back_populates="lesson")
    teacher = relationship("Teacher", back_populates="lesson")

    @staticmethod
    async def add_lesson(course_id, teacher_id, start):
        async with async_session() as session:
            lesson = Lesson(course_id=course_id, teacher_id=teacher_id, start=start)
            session.add(lesson)
            await session.commit()

    @staticmethod
    async def delete_lesson(lesson_id):
        lesson = await Lesson.get_lesson_by_id(lesson_id)
        async with async_session() as session:
            await session.delete(lesson)
            await session.commit()

    @staticmethod
    async def get_lesson_by_id(id: int) -> Lesson:
        async with async_session() as session:
            query = select(Lesson).filter(Lesson.id == id)
            result = await session.execute(query)
            return result.scalars().first()

    @staticmethod
    async def get_all_lessons() -> List[Lesson]:
        async with async_session() as session:
            query = select(Lesson).options(selectinload(Lesson.course)).options(selectinload(Lesson.teacher))
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_all_lessons_for_day(date: datetime) -> List[Lesson]:
        async with async_session() as session:
            next_day = date + timedelta(days=1)
            query = select(Lesson).options(selectinload(Lesson.course)).options(selectinload(Lesson.teacher)).filter(
                Lesson.start >= date, Lesson.start < next_day).order_by(Lesson.start)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def check_if_busy(id, date: datetime) -> List[Lesson]:
        async with async_session() as session:
            query = (
                select(Lesson)
                    .options(selectinload(Lesson.course))
                    .options(selectinload(Lesson.teacher))
                    .join(Lesson.teacher)
                    .options(contains_eager(Lesson.teacher))
                    .execution_options(populate_existing=True)
                    .filter(Teacher.id == id)
                    .filter(Lesson.start >= date - timedelta(hours=1, minutes=59),
                            Lesson.start < date + timedelta(hours=2))
            )
            result = await session.execute(query)
            return result.scalars().all()
