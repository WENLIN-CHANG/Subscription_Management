from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionCycle, SubscriptionCategory

class SubscriptionBase(BaseModel):
    name: str
    price: float
    cycle: SubscriptionCycle
    category: SubscriptionCategory
    start_date: datetime

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    cycle: Optional[SubscriptionCycle] = None
    category: Optional[SubscriptionCategory] = None
    start_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True