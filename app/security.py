from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserInDB
from jose import jwt, JWTError
from passlib.context import CryptContext
from pwdlib import PasswordHash
import bcrypt
from .config import Config
from app.logger import logger

# from app.services.user_services import get_user_by_username, get_user_by_id, get_user_by_email, create_user

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # return pwd_context.hash(password)
    return password_hash.hash(password)

    # # ensure UTF-8 bytes

    # pwd_bytes = password.encode("utf-8")
    #
    # # if too long, pre-hash with sha256
    # if len(pwd_bytes) > 72:
    #     pwd_bytes = hashlib.sha256(pwd_bytes).digest()
    #
    # salt = bcrypt.gensalt()
    # hashed = bcrypt.hashpw(pwd_bytes, salt)
    # return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # return pwd_context.verify(plain_password, hashed_password)
    return password_hash.verify(plain_password, hashed_password)


async def authenticate_user( db: AsyncSession, username: str, password: str) -> Optional[UserInDB]:
    """Verify the user's credentials."""
    from app.services.user_services import get_user_by_username
    user = await get_user_by_username(db, username)
    logger.info(user)

    if user and verify_password(password, user.hashed_password):
        return user
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        Config.SECRET_KEY,
        algorithm=Config.ALGORITHM
    )
    return encoded_jwt

