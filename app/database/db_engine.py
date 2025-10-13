from typing import AsyncGenerator
from ..config import Config
from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncpg

Base = declarative_base()

# Async engine for FastAPI
async_engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

# Sync engine for Alembic migrations
sync_engine = create_engine(
    Config.SYNC_DATABASE_URL,
    echo=True
)

# Session makers
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize database
async def init_db():
    async with async_engine.begin() as conn:
        # For development - creates all tables
        # In production, use Alembic migrations instead
        # from models import Base
        await conn.run_sync(Base.metadata.create_all)

# Test database connection
async def test_db_connection():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
