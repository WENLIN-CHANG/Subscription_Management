from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionCycle, SubscriptionCategory, Currency

class SubscriptionBase(BaseModel):
    name: str
    original_price: float  # 原始價格
    currency: Currency  # 原始貨幣
    cycle: SubscriptionCycle
    category: SubscriptionCategory
    start_date: datetime

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

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    price: float  # 台幣價格 (轉換後)
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True