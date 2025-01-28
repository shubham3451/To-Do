from pydantic import BaseModel, EmailStr
from typing import  Optional

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    done: Optional[bool] = False

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr 

class UserCreate(UserBase):
    password: str

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    email: str

    class Config:
        from_attributes = True

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    reset_token: str
    new_password: str
