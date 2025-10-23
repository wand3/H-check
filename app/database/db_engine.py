from typing import AsyncGenerator
from ..config import Config
from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncpg
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


# connect_args = {"check_same_thread": False}
engine = create_async_engine(Config.DATABASE_URL,
                             echo=True)

# Create a new async "sessionmaker"
# This is a configurable factory for creating new AsyncSession objects
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def create_db_and_tables():
    """
    Initializes the database tables. Should be called once on application startup.
    """
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # Optional: drop tables first
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """
    FastAPI dependency to get an async database session.
    Ensures the session is always closed, even if errors occur.
    """
    async_session = AsyncSessionLocal()
    try:
        yield async_session
    finally:
        await async_session.close()

# Test database connection
async def test_db_connection():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
