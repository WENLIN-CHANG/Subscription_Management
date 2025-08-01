from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.subscription import SubscriptionCycle, SubscriptionCategory, Currency

class CreateSubscriptionCommand(BaseModel):
    """創建訂閱命令"""
    name: str = Field(..., min_length=1, max_length=100)
    original_price: float = Field(..., gt=0)
    currency: Currency
    cycle: SubscriptionCycle
    category: SubscriptionCategory
    start_date: datetime

class UpdateSubscriptionCommand(BaseModel):
    """更新訂閱命令"""
    subscription_id: int
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    original_price: Optional[float] = Field(None, gt=0)
    currency: Optional[Currency] = None
    cycle: Optional[SubscriptionCycle] = None
    category: Optional[SubscriptionCategory] = None
    start_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class SubscriptionQuery(BaseModel):
    """訂閱查詢"""
    user_id: int
    include_inactive: bool = False
    category: Optional[SubscriptionCategory] = None

class SubscriptionDto(BaseModel):
    """訂閱數據傳輸對象"""
    id: int
    user_id: int
    name: str
    price: float  # 台幣價格
    original_price: float  # 原始價格
    currency: Currency
    cycle: SubscriptionCycle
    category: SubscriptionCategory
    start_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # 計算字段
    monthly_cost: Optional[float] = None
    yearly_cost: Optional[float] = None
    next_billing_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SubscriptionSummaryDto(BaseModel):
    """訂閱摘要數據傳輸對象"""
    total_subscriptions: int
    active_subscriptions: int
    total_monthly_cost: float
    total_yearly_cost: float
    categories: dict
    upcoming_renewals: List[SubscriptionDto]

class BulkSubscriptionOperationCommand(BaseModel):
    """批量訂閱操作命令"""
    subscription_ids: List[int]
    operation: str  # 'activate', 'deactivate', 'delete'