from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from .config import Config
from app.schemas.user import UserInDB
from app.schemas.auth import TokenData
from app.database.db_engine import get_session # Your DB session dependency
from app.models.user import UserModel
from app.services.user_services import get_user_by_username
from app.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_session)
) -> UserInDB:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=[Config.ALGORITHM]
        )
        logger.info(f"past payload {payload}")
        username: str = payload.get("sub")
        if username is None:
            logger.info("no username")

            raise credentials_exception
    except JWTError:
        logger.info("JWT error")

        raise credentials_exception

    user = await get_user_by_username(db, username)
    logger.info(f"User {user}")

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: UserModel = Depends(get_current_user)
) -> UserInDB:
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

