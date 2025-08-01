from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class CreateBudgetCommand(BaseModel):
    """創建預算命令"""
    monthly_limit: float = Field(..., gt=0, le=1000000)

class UpdateBudgetCommand(BaseModel):
    """更新預算命令"""
    budget_id: int
    monthly_limit: Optional[float] = Field(None, gt=0, le=1000000)

class BudgetQuery(BaseModel):
    """預算查詢"""
    user_id: int

class BudgetDto(BaseModel):
    """預算數據傳輸對象"""
    id: int
    user_id: int
    monthly_limit: float
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BudgetUsageDto(BaseModel):
    """預算使用情況數據傳輸對象"""
    budget: Optional[BudgetDto]
    usage_info: Dict[str, Any]
    category_usage: Dict[str, Any]
    recommendations: List[str]
    savings_potential: Dict[str, Any]

class BudgetAnalyticsDto(BaseModel):
    """預算分析數據傳輸對象"""
    current_month: BudgetUsageDto
    previous_month_comparison: Optional[Dict[str, Any]]
    trend_analysis: Dict[str, Any]