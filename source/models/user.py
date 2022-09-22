from __future__ import annotations
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship
from sqlalchemy import select
from database import async_session

from models import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(TEXT, nullable=False, unique=True)
    password = Column(TEXT, nullable=False)

    @staticmethod
    async def get_user_by_id(id: int) -> User:
        async with async_session() as session:
            query = select(User).filter(User.id == id)
            result = await session.execute(query)
            return result.scalars().first()

    @staticmethod
    async def get_user_by_username(username: str) -> User:
        async with async_session() as session:
            query = select(User).filter(User.username == username)
            result = await session.execute(query)
            return result.scalars().first()

    @staticmethod
    async def get_users() -> User:
        async with async_session() as session:
            query = select(User)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def add_user(username, password):
        async with async_session() as session:
            user = User(username=username, password=password)
            session.add(user)
            await session.commit()

    @staticmethod
    async def delete_user(id):
        user = await User.get_user_by_id(id)
        async with async_session() as session:
            await session.delete(user)
            await session.commit()
