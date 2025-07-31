from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionCycle, SubscriptionCategory, Currency
from app.core.security import (
    validate_subscription_name_field,
    validate_price_field,
    SecurityValidator
)

class SubscriptionBase(BaseModel):
    name: str
    original_price: float  # 原始價格
    currency: Currency  # 原始貨幣
    cycle: SubscriptionCycle
    category: SubscriptionCategory
    start_date: datetime
    
    @validator('name')
    def validate_name(cls, v):
        return validate_subscription_name_field(v)
    
    @validator('original_price')
    def validate_original_price(cls, v):
        return validate_price_field(v)
    
    @validator('start_date', pre=True)
    def validate_start_date(cls, v):
        if isinstance(v, str):
            # 如果是字符串，進行額外驗證
            v = SecurityValidator.validate_date_string(v)
            from datetime import datetime
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    currency: Optional[Currency] = None
    cycle: Optional[SubscriptionCycle] = None
    category: Optional[SubscriptionCategory] = None
    start_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            return validate_subscription_name_field(v)
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None:
            return validate_price_field(v)
        return v
    
    @validator('original_price')
    def validate_original_price(cls, v):
        if v is not None:
            return validate_price_field(v)
        return v
    
    @validator('start_date', pre=True)
    def validate_start_date(cls, v):
        if v is not None and isinstance(v, str):
            v = SecurityValidator.validate_date_string(v)
            from datetime import datetime
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    price: float  # 台幣價格 (轉換後)
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True