from pydantic import BaseModel, EmailStr
from typing import Optional
from webapp.schemas.user import UserBase

class Token(BaseModel):
    user: UserBase
    access_token: str
    # token_type: str


class TokenData(BaseModel):
    # email: Optional[str] = None
    username: Optional[str] = None
