from sqlalchemy.sql.sqltypes import String
from pydantic import BaseModel
from pydantic.networks import EmailStr
from pydantic.types import conint
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr #requires email-validator library to be installed
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr #requires email-validator library to be installed
    created_timestamp: datetime
    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    user: UserResponse #we have configured this to return another Pydantic model type, UserReponse
    created_timestamp: datetime
    #this allows sqlalchemy to decode non-dictionary items, which I believe is the UserResponse class
    class Config:
        orm_mode = True

class Vote(BaseModel):
    post_id: int
    direction: conint(le=1) #ensures that entry is <= 1, ideally this would be adjusted to only accept -1, 0, 1

class PostWithVote(BaseModel):
    Post: PostResponse
    votes: int