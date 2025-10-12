from datetime import datetime
from bson import ObjectId # type: ignore
from pydantic import BaseModel, EmailStr, constr, Field, field_validator # type: ignore
from typing import Optional
from ..schemas import PyObjectId


class UserBase(BaseModel):
    email: EmailStr
    username: str
    disabled: Optional[bool] = None
    profile_pic: Optional[str] = None

    class Config:
        from_attributes = True
        # json_encoders = {
        #     ObjectId: str
        # }
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john_doe@example.com",
                "disabled": "false",
                "profile_pic": "image.jpg"

            }
        }


class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # Alias _id to id
    # hashed_password: str
    created_at: datetime
    updated_at: datetime

    @field_validator("id")
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)

    class Config:
        json_encoders = {
            ObjectId: str
        }


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    password: Optional[constr(min_length=6)] = None
