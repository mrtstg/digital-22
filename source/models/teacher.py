from __future__ import annotations
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy import select
from database import async_session

from models import Base


class Teacher(Base):
    __tablename__ = "teacher"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(TEXT)
    phone = Column(TEXT)
    email = Column(TEXT)

    lesson = relationship("Lesson", back_populates="teacher")

    @staticmethod
    async def get_teachers() -> Teacher:
        async with async_session() as session:
            query = select(Teacher)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_teacher_by_id(id: int) -> Teacher:
        async with async_session() as session:
            query = select(Teacher).filter(Teacher.id == id).options(selectinload(Teacher.lesson))
            result = await session.execute(query)
            return result.scalars().first()

    @staticmethod
    async def add_teacher(name, phone, email):
        async with async_session() as session:
            teacher = Teacher(name=name, phone=phone, email=email)
            session.add(teacher)
            await session.commit()

    @staticmethod
    async def delete_teacher(id):
        teacher = await Teacher.get_teacher_by_id(id)
        async with async_session() as session:
            await session.delete(teacher)
            await session.commit()
