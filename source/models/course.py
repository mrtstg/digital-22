from __future__ import annotations
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy import select
from database import async_session

from models import Base


class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(TEXT)
    description = Column(TEXT)

    lesson = relationship("Lesson", back_populates="course")

    @staticmethod
    async def get_courses() -> Course:
        async with async_session() as session:
            query = select(Course)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_course_by_id(id: int) -> Course:
        async with async_session() as session:
            query = select(Course).filter(Course.id == id).options(selectinload(Course.lesson))
            result = await session.execute(query)
            return result.scalars().first()

    @staticmethod
    async def add_course(name, description):
        async with async_session() as session:
            course = Course(name=name, description=description)
            session.add(course)
            await session.commit()

    @staticmethod
    async def delete_course(id):
        course = await Course.get_course_by_id(id)
        async with async_session() as session:
            await session.delete(course)
            await session.commit()
