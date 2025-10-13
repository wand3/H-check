import uuid
from ..logger import logger
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Optional, Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..schemas.user import UserInDB, UserCreate, UserUpdate, UserBase
from ..schemas.auth import TokenData
from ..config import Config
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db_engine import get_db, Base


# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserModel:
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # query_logs = relationship("QueryLog", back_populates="user")

    @classmethod
    async def create_user(cls, db: AsyncSession, user_data: UserCreate) -> UserInDB:
        try:
            # Check for existing user
            existing_email = await cls.get_user_by_email(db, user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Check username if it exists in user_data
            if hasattr(user_data, 'username') and user_data.username:
                existing_username = await cls.get_user_by_username(db, user_data.username)
                if existing_username:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )

            # Create user
            hashed_password = cls.hash_password(user_data.password)

            user_kwargs = {
                "email": user_data.email,
                "hashed_password": hashed_password,
                "disabled": False
            }

            # Add optional fields
            if hasattr(user_data, 'username') and user_data.username:
                user_kwargs["username"] = user_data.username

            if hasattr(user_data, 'full_name') and user_data.full_name:
                user_kwargs["full_name"] = user_data.full_name

            user = cls(**user_kwargs)

            db.add(user)
            await db.commit()
            await db.refresh(user)

            return UserInDB.from_orm(user)

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create user"
            )
    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str) -> Optional[UserInDB]:
        """Get user by email from PostgreSQL"""
        stmt = select(cls).where(cls.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return UserInDB.from_orm(user) if user else None

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: UUID) -> Optional[UserInDB]:
        """Get user by ID from PostgreSQL"""
        stmt = select(cls).where(cls.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return UserInDB.from_orm(user) if user else None

    @classmethod
    async def get_user_by_username(cls, db: AsyncSession, username: str) -> Optional[UserInDB]:
        """Get user by username from PostgreSQL"""
        stmt = select(cls).where(cls.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return UserInDB.from_orm(user) if user else None

    @classmethod
    async def update_user(cls, db: AsyncSession, user_id: UUID, user_data: UserUpdate) -> Optional[UserInDB]:
        """Update user in PostgreSQL"""
        stmt = select(cls).where(cls.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        update_dict = user_data.dict(exclude_unset=True)
        if "password" in update_dict:
            update_dict["hashed_password"] = cls.hash_password(update_dict.pop("password"))

        for field, value in update_dict.items():
            setattr(user, field, value)

        user.updated_at = func.now()
        await db.commit()
        await db.refresh(user)
        return UserInDB.from_orm(user)

    @classmethod
    async def delete_user(cls, db: AsyncSession, user_id: UUID) -> bool:
        """Delete user from PostgreSQL"""
        stmt = select(cls).where(cls.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    async def authenticate_user(cls, db: AsyncSession, username: str, password: str) -> Optional[UserInDB]:
        """Verify the user's credentials."""
        user = await cls.get_user_by_username(db, username)
        if user and cls.verify_password(password, user.hashed_password):
            return user
        return None

    @staticmethod
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

    @classmethod
    async def get_current_user(
            cls,
            token: str = Depends(oauth2_scheme),
            db: AsyncSession = Depends(get_db())
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
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await cls.get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user

    @classmethod
    async def get_current_active_user(
            cls,
            current_user: UserInDB = Depends(get_current_user)
    ) -> UserInDB:
        """Get current active user"""
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

# active_u = UserModel(db=dep_inj)


class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(String, primary_key=True, default=uuid.uuid4())
    # user_id = Column(String, ForeignKey("users.id"), nullable=False)
    natural_language_query = Column(Text, nullable=False)
    fhir_query = Column(Text, nullable=False)
    fhir_response = Column(JSON)  # Store raw FHIR response
    processed_results = Column(JSON)  # Store processed results
    execution_time = Column(Integer)  # Time in milliseconds
    patient_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    # user = relationship("User", back_populates="query_logs")

async def get_current_active_user(current_user: Annotated[UserBase, Depends(UserModel.get_current_user)]):
    # logger.info(f'User model ---- get current  active user payload error {current_user}')
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
