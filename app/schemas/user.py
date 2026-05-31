from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    photo_url: Optional[str] = None

class LoginSchema(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    photo_url: Optional[str] = None
    role: str
    onboarding_completed: bool 

    class Config:
        orm_mode = True

class VerifyOTPSchema(BaseModel):
    email: EmailStr
    otp: str
    remember_me: bool = False

    
class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str
