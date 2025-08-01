from typing import Optional
from fastapi import APIRouter, Depends, Request, status

from app.application.services.budget_application_service import BudgetApplicationService
from app.application.dtos.budget_dtos import (
    CreateBudgetCommand,
    UpdateBudgetCommand,
    BudgetDto,
    BudgetUsageDto,
    BudgetAnalyticsDto
)
from app.common.responses import ApiResponse
from app.models import User
from app.core.auth import get_current_active_user
from app.core.rate_limiter import read_rate_limit, create_rate_limit, general_rate_limit
from app.infrastructure.dependencies import get_budget_application_service

router = APIRouter()

@router.get("/", response_model=ApiResponse[Optional[BudgetDto]])
@read_rate_limit()
async def get_budget(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    service: BudgetApplicationService = Depends(get_budget_application_service)
):
    """獲取用戶預算"""
    budget = await service.get_budget(current_user.id)
    
    return ApiResponse.success(
        data=budget,
        message="成功獲取預算信息" if budget else "尚未設置預算"
    )

@router.post("/", response_model=ApiResponse[BudgetDto], status_code=status.HTTP_201_CREATED)
@create_rate_limit()
async def create_budget(
    request: Request,
    command: CreateBudgetCommand,
    current_user: User = Depends(get_current_active_user),
    service: BudgetApplicationService = Depends(get_budget_application_service)
):
    """創建預算"""
    budget = await service.create_budget(current_user.id, command)
    
    return ApiResponse.success(
        data=budget,
        message="預算創建成功"
    )

@router.put("/{budget_id}", response_model=ApiResponse[BudgetDto])
@general_rate_limit()
async def update_budget(
    request: Request,
    budget_id: int,
    command: UpdateBudgetCommand,
    current_user: User = Depends(get_current_active_user),
    service: BudgetApplicationService = Depends(get_budget_application_service)
):
    """更新預算"""
    command.budget_id = budget_id
    budget = await service.update_budget(current_user.id, command)
    
    return ApiResponse.success(
        data=budget,
        message="預算更新成功"
    )

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
@general_rate_limit()
async def delete_budget(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    service: BudgetApplicationService = Depends(get_budget_application_service)
):
    """刪除預算"""
    await service.delete_budget(current_user.id)

@router.get("/usage", response_model=ApiResponse[BudgetUsageDto])
@read_rate_limit()
async def get_budget_usage(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    service: BudgetApplicationService = Depends(get_budget_application_service)
):
    """獲取預算使用情況"""
    usage = await service.get_budget_usage(current_user.id)
    
    return ApiResponse.success(
        data=usage,
        message="成功獲取預算使用情況"
    )

@router.get("/analytics", response_model=ApiResponse[BudgetAnalyticsDto])
@read_rate_limit()
async def get_budget_analytics(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    service: BudgetApplicationService = Depends(get_budget_application_service)
):
    """獲取預算分析數據"""
    analytics = await service.get_budget_analytics(current_user.id)
    
    return ApiResponse.success(
        data=analytics,
        message="成功獲取預算分析數據"
    )