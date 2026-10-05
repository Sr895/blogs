from pydantic import BaseModel
from typing import Optional, List

class Blog(BaseModel):
    title: str
    content: str
    is_published: Optional[bool] = True
    user_id: int

class User(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    name: str
    email: str

class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    is_published: bool
    author: Optional[UserResponse] = None

class UserResponseAll(BaseModel):
    name: str
    email: str
    # blogs: List[BlogResponse]

class UserLoginRequest(BaseModel):
    email: str
    password: str