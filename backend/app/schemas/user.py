from pydantic import BaseModel, validator, EmailStr
from typing import Optional
from datetime import datetime
from app.core.security import (
    validate_username_field,
    validate_email_field,
    SecurityValidator
)

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        return validate_username_field(v)
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            return validate_email_field(v)
        return v

class UserCreate(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        return validate_username_field(v)
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v.strip()) < 6:
            raise ValueError('密碼長度至少需要 6 個字符')
        
        if len(v) > 128:
            raise ValueError('密碼長度不能超過 128 個字符')
        
        # 檢查可疑模式
        if SecurityValidator.is_suspicious_input(v):
            raise ValueError('密碼包含不允許的字符')
        
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        return validate_username_field(v)
    
    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('密碼不能為空')
        return SecurityValidator.sanitize_text(v, max_length=128)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('current_password')
    def validate_current_password(cls, v):
        if not v:
            raise ValueError('當前密碼不能為空')
        return SecurityValidator.sanitize_text(v, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not v or len(v.strip()) < 6:
            raise ValueError('新密碼長度至少需要 6 個字符')
        
        if len(v) > 128:
            raise ValueError('新密碼長度不能超過 128 個字符')
        
        # 檢查可疑模式
        if SecurityValidator.is_suspicious_input(v):
            raise ValueError('新密碼包含不允許的字符')
        
        return v