from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import timedelta
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from app.schemas.auth import Token
from app.schemas.user import UserBase, UserCreate, UserInDB
from app.models.user import UserModel
from app.database.db_engine import get_session
from app.logger import logger
from ..config import Config

auth = APIRouter(tags=["Auth"])


def get_user_model() -> UserModel:
    """Dependency to inject a `UserModel` instance."""
    return UserModel(get_session)


@auth.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_model: Annotated[UserModel, Depends(get_user_model)],  # Inject the UserModel instance
) -> Token:
    """Authenticate user and issue a JWT access token."""
    # Call the instance method using the injected user_model
    user = await user_model.authenticate_user(self=user_model, username=form_data.username, password=form_data.password)
    # logger.info(user)
    # user = UserInDB(user)
    # user_list = [us for us in user]
    # logger.info(user_list)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_model.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(user=user, access_token=access_token)  # , token_type="bearer"


# Register route
@auth.post("/auth/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserCreate,
        user_model: Annotated[UserModel, Depends(get_user_model)],
) -> UserBase:
    if not user_data.email or not user_data.password or not user_data.username:
        raise HTTPException(status_code=400, detail="Missing required fields")
    existing_user = await user_model.get_user_by_email(email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    new_user = await user_model.create_user(user_data=user_data)

    return UserBase(**new_user.dict())


# Login route
@auth.post("/auth/login", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_model: Annotated[UserModel, Depends(get_user_model)],
) -> Token:
    user = await user_model.authenticate_user(self=user_model, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_model.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# check if username already exists in database
@auth.get("/auth/check-username", status_code=status.HTTP_200_OK)
async def check_username(
        user_model: Annotated[UserModel, Depends(get_user_model)],
        username: str = Query(None)
):
    """
    Checks if a username already exists in the database.
    """
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")

    existing_user = await user_model.db.find_one({"username": username})
    return {"exists": existing_user is not None}


# check if email already exists in database
@auth.get("/auth/check-email", status_code=status.HTTP_200_OK)
async def check_email(
        user_model: Annotated[UserModel, Depends(get_user_model)],
        email: str = Query(None)
):
    """
    Checks if an email already exists in the database.
    """
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")

    existing_user = await user_model.db.find_one({"email": email})
    return {"exists": existing_user is not None}
