from typing import Optional, List
from fastapi import UploadFile, File, Body
from pydantic import BaseModel, Field, HttpUrl, EmailStr


class UserImageUpdateForm(BaseModel):
    image: Optional[UploadFile] = None