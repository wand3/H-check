import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from app.models.user import UserModel
from app.security import hash_password
from passlib.context import CryptContext
from typing import Optional, Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..schemas.user import UserInDB, UserCreate, UserUpdate, UserBase
from ..schemas.auth import TokenData
from ..config import Config
from jose import jwt, JWTError
from app.database.db_engine import get_session
from ..security import hash_password

async def create_user(db: AsyncSession, user_data: UserCreate) -> UserModel:
    # The validation logic for existing users should ideally be in the API route
    # to provide immediate feedback, but can also be here.

    hashed_pass = hash_password(user_data.password)
    user = UserModel.from_orm(user_data, {"hashed_password": hashed_pass})

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserModel]:
    stmt = select(UserModel).where(UserModel.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserModel]:
    stmt = select(UserModel).where(UserModel.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[UserModel]:
    return await db.get(UserModel, user_id)  # .get() is simpler for primary keys


async def update_user(db: AsyncSession, user: UserModel, user_data: UserUpdate) -> UserModel:
    update_dict = user_data.dict(exclude_unset=True)

    if "password" in update_dict:
        update_dict["hashed_password"] = hash_password(update_dict.pop("password"))

    for field, value in update_dict.items():
        setattr(user, field, value)

    # Note: onupdate handles this automatically now, but if you want to force it:
    # user.updated_at = datetime.utcnow()

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> bool:
    user = await db.get(UserModel, user_id)
    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False
