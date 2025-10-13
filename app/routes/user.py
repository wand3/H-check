import logging
import os
import shutil
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.encoders import jsonable_encoder
from typing import Annotated, Optional

from app.logger import logger
from app.config import Config
from app.routes.auth import get_user_model
from app.schemas.forms import UserImageUpdateForm
from app.schemas.user import UserBase, UserUpdate, UserInDB
from app.models.user import get_current_active_user, UserModel

from app.database.db_engine import get_db


router = APIRouter(prefix="/user", tags=["User"])

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
async def update_user(
        user_id: str, user_data: UserUpdate, current_user: UserBase = Depends(get_current_active_user)
):
    if not current_user:
        raise HTTPException(status_code=400, detail="User is not logged in")

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    updated_user = await curr_user.update_user(user_id, user_data)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user


# update user image
@router.put("/{user_id}/add/image", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def update_user_image(
        user_id: str,
        user_model: Annotated[UserModel, Depends(get_db())],
        user_data: Annotated[UserImageUpdateForm, Form()]
):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format.")

        existing_user = await user_model.db.find_one({"_id": ObjectId(user_id)})
        # logger.info(existing_user)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found.")

        image = None
        if user_data.image is not None:  # Check if image is provided
            file_content = await user_data.image.read()
            file_size = len(file_content)
            if file_size > Config.MAX_IMAGE_SIZE:
                raise HTTPException(status_code=400, detail="Image size exceeds limit.")

            file_ext = os.path.splitext(user_data.image.filename)[1]
            if file_ext not in Config.UPLOAD_EXTENSIONS:
                raise HTTPException(status_code=400,
                                    detail=f"Unsupported image format. Allowed: {', '.join(Config.UPLOAD_EXTENSIONS)}.")

            image_filename = f"{ObjectId()}_{user_data.image.filename}"
            os.makedirs(Config.UPLOAD_USER_IMAGE, exist_ok=True)
            image_path = os.path.join(Config.UPLOAD_USER_IMAGE, image_filename)

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(user_data.image.file, buffer)

                if existing_user.get("profile_pic"):
                    old_image_path = os.path.join(Config.UPLOAD_USER_IMAGE, existing_user["profile_pic"])
                    try:
                        os.remove(old_image_path)
                    except FileNotFoundError:
                        pass

            existing_user["image"] = image_filename
            logger.error(image_filename)

        existing_user["updated_at"] = datetime.utcnow()
        image = existing_user["image"]
        logger.error(image)
        await user_model.db.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_pic": image}}
        )

        # update time of modification
        await user_model.db.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        updated_user = await user_model.db.find_one({"_id": ObjectId(user_id)})
        if updated_user:
            return UserInDB(**updated_user)  # Use the Project model to parse the result
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to retrieve updated user")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/me")
async def delete_user(user_id: str, current_user: UserBase = Depends(get_current_active_user)):
    delete_u = await current_user.delete_user(user_id)

    return delete_u
