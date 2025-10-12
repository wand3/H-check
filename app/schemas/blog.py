from datetime import datetime, timedelta, timezone

from fastapi import UploadFile, File
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

from .comment import Comment
from ..schemas import PyObjectId


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}


# post
class BlogPost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    image: Optional[str] = None
    comments: Optional[List[Comment]] = Field(default_factory=list, description="List of comment IDs")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "image": "special.jpg",
                "title": "Lady and the hen with many colors",
                "content": '"Enumerating objects: 36, done Counting objects: 100% (36/36), done. Delta compression '
                           'using up to 4 threads Compressing objects: 100% (22/22), done. iting objects: 100% ('
                           '22/22), 3.57 KiB | 1.78 MiB/s, done."',
                "tags": ["Lady", "and", "the", "hen", "with"]
            }
        }
    )
    # class Config:
    #     form_attributes = True
    #     json_schema_extra = {
    #         "example": {
    #             "image": "special.jpg",
    #             "title": "Lady and the hen with many colors",
    #             "content": '"Enumerating objects: 36, done Counting objects: 100% (36/36), done. Delta compression '
    #                        'using up to 4 threads Compressing objects: 100% (22/22), done. iting objects: 100% ('
    #                        '22/22), 3.57 KiB | 1.78 MiB/s, done."',
    #             "tags": ["Lady", "and", "the", "hen", "with"]
    #         }
    #     }


class BlogPostInDB(BlogPost):
    # id: Optional[PyObjectId] = None
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # Alias _id to id
    created_at: datetime
    updated_at: datetime
