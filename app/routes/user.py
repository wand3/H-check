import logging
import os
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.encoders import jsonable_encoder
from typing import Annotated, Optional
from sqlmodel import Field, Session
from app.logger import logger
from app.config import Config
from app.schemas.forms import UserImageUpdateForm
from app.schemas.user import UserBase, UserUpdate, UserInDB
from app.dependencies import get_current_active_user, get_current_user
from app.models.user import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_engine import get_session
from app.services.user_services import update_user_in_db, update_user_image_in_db
from uuid import UUID
import aiofiles



router = APIRouter(prefix="/user", tags=["User"])
SessionDep = Annotated[Session, Depends(get_session)]

# curr_user = UserModel(get_db())  # for class injection


@router.get("/me", response_model=None)
async def read_user_me(
    current_user: UserBase = Depends(get_current_active_user),
):
    try:
        # Ensure the current_user is valid and active
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if getattr(current_user, "disabled", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user
    except HTTPException as e:
        # Handle HTTPException and re-raise it
        raise e


@router.put("/{user_id}/me", response_model=UserBase)
async def update_user_endpoint(
    user_id: UUID,  # or `int` if you use integer primary keys
    user_data: UserUpdate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> UserBase:
    """
    Update the current user's record (Postgres / SQLModel).
    - user_id must match current_user.id (unless you want admin override).
    - only fields present in the request are updated.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not logged in")

    # Ensure the logged-in user is updating their own record (or allow admin)
    if getattr(current_user, "id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this user")

    updated_user = await update_user_in_db(db=db, user_id=user_id, user_update=user_data)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # return SQLModel instance — FastAPI will convert to response_model
    return updated_user


# update user image
@router.put("/{user_id}/image", response_model=UserInDB)
async def update_user_image(
    user_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
    image: Optional[UploadFile] = File(None),
):
    """
    Update the current user's profile image.
    - Accepts multipart/form-data with field "image".
    - Only the logged-in user may update their own image (unless you allow admin overrides).
    """
    # Auth check
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

    # Ensure user can only update their own image (adjust if you allow admins)
    if getattr(current_user, "id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this user")

    # Must provide an image file
    if image is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No image file provided")

    # Validate file size
    file_content = await image.read()
    file_size = len(file_content)
    if file_size > Config.MAX_IMAGE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image size exceeds limit")

    # Validate extension
    _, ext = os.path.splitext(image.filename or "")
    ext = ext.lower()
    if ext not in Config.UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format. Allowed: {', '.join(Config.UPLOAD_EXTENSIONS)}"
        )

    # Fetch existing user (so we can remove old image if present)
    existing_user = await get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Build safe filename (UUID prefix so collisions are unlikely)
    safe_filename = f"{uuid4().hex}{ext}"
    os.makedirs(Config.UPLOAD_USER_IMAGE, exist_ok=True)
    image_path = os.path.join(Config.UPLOAD_USER_IMAGE, safe_filename)

    # Save file asynchronously
    try:
        async with aiofiles.open(image_path, "wb") as out_file:
            await out_file.write(file_content)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save image: {e}")

    # Remove old image file if it exists and is not the same as default
    old_pic = getattr(existing_user, "profile_pic", None)
    if old_pic:
        old_path = os.path.join(Config.UPLOAD_USER_IMAGE, old_pic)
        try:
            if os.path.exists(old_path):
                os.remove(old_path)
        except Exception:
            # non-fatal — log if you have logger configured
            pass

    # Persist filename into DB and update timestamp
    updated_user = await update_user_image_in_db(db=db, user_id=user_id, image_filename=safe_filename)
    if not updated_user:
        # rollback: remove written file if DB update failed
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user image")

    # Return the updated user (SQLModel is convertible to Pydantic schema)
    return UserInDB.model_validate(updated_user)  # Pydantic v2; or UserInDB.from_orm(updated_user) if using v1

@router.delete("/{user_id}/me")
async def delete_user(user_id: str, current_user: UserBase = Depends(get_current_active_user)):
    delete_u = await current_user.delete_user(user_id)

    return delete_u
