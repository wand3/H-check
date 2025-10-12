from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr
from typing import Optional, List
from ..schemas import PyObjectId


# class CommentAuthor(BaseModel):
#     id: Optional[PyObjectId] = Field(..., alias="_id")
#     username: str
#     email: EmailStr

class Reply(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # Alias _id to id
    parent_comment_id: str  # References the parent comment's _id
    user_id: str
    content: Optional[str] = Field(None, description="Detailed comment")
    images: Optional[List[str]] = Field(None, description="List of URLs to project screenshots/images")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Comment(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "_id": "64b8e349887754f76789abcd",
                "post_id": "ObjectId('64b8e349887754f76789abcd')",
                "author": [
                    {
                        "_id": "ObjectId('64b8e349887754f76789abcd')",
                        "username": "Jane Smith",
                        "email": "JaneSmith@kwanks.com"
                    }
                ],
                "content": "Great post!",
                "images": ["image1.png", "image11.mp4"],
                "replies": ['ObjectId("678bdb92cb995ba6da6ba9cc")',
                            'ObjectId("678bdbbecb995ba6da6ba9ce")']
            }
        })

    post_id: str
    user_id: str
    content: Optional[str] = Field(..., description="Detailed comment")
    images: Optional[List[str]] = Field(None, description="List of URLs to project screenshots/images")
    replies: Optional[List[Reply]] = Field(default_factory=list)  # Nested replies


class CommentInDB(Comment):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # Alias _id to id
    created_at: datetime

# class CommentWithReplies(Comment):
#     replies: List[Reply] = Field(default_factory=list)
#
