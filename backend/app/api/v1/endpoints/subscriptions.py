from typing import List
from fastapi import APIRouter, Depends, Request, status

from app.domain.interfaces.repositories import IUnitOfWork
from app.domain.services.subscription_domain_service import SubscriptionDomainService
from app.application.services.subscription_application_service import SubscriptionApplicationService
from app.application.dtos.subscription_dtos import (
    CreateSubscriptionCommand,
    UpdateSubscriptionCommand,
    SubscriptionQuery,
    SubscriptionDto,
    SubscriptionSummaryDto,
    BulkSubscriptionOperationCommand
)
from app.common.responses import ApiResponse
from app.models import User
from app.core.auth import get_current_active_user
from app.core.rate_limiter import read_rate_limit, create_rate_limit, general_rate_limit
from app.infrastructure.dependencies import get_subscription_application_service

router = APIRouter()

@router.get("/", response_model=ApiResponse[List[SubscriptionDto]])
@read_rate_limit()
async def get_subscriptions(
    request: Request,
    category: str = None,
    include_inactive: bool = False,
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionApplicationService = Depends(get_subscription_application_service)
):
    """獲取用戶的所有訂閱"""
    query = SubscriptionQuery(
        user_id=current_user.id,
        include_inactive=include_inactive,
        category=category
    )
    
    subscriptions = await service.get_subscriptions(query)
    
    return ApiResponse.success(
        data=subscriptions,
        message=f"成功獲取 {len(subscriptions)} 個訂閱"
    )

@router.post("/", response_model=ApiResponse[SubscriptionDto], status_code=status.HTTP_201_CREATED)
@create_rate_limit()
async def create_subscription(
    request: Request,
    command: CreateSubscriptionCommand,
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionApplicationService = Depends(get_subscription_application_service)
):
    """創建新訂閱"""
    subscription = await service.create_subscription(current_user.id, command)
    
    return ApiResponse.success(
        data=subscription,
        message="訂閱創建成功"
    )

@router.get("/summary", response_model=ApiResponse[SubscriptionSummaryDto])
@read_rate_limit()
async def get_subscription_summary(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionApplicationService = Depends(get_subscription_application_service)
):
    """獲取訂閱摘要"""
    summary = await service.get_subscription_summary(current_user.id)
    
    return ApiResponse.success(
        data=summary,
        message="成功獲取訂閱摘要"
    )

@router.get("/{subscription_id}", response_model=ApiResponse[SubscriptionDto])
@read_rate_limit()
async def get_subscription(
    request: Request,
    subscription_id: int,
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionApplicationService = Depends(get_subscription_application_service)
):
    """獲取特定訂閱"""
    subscription = await service.get_subscription(current_user.id, subscription_id)
    
    return ApiResponse.success(
        data=subscription,
        message="成功獲取訂閱詳情"
    )

@router.put("/{subscription_id}", response_model=ApiResponse[SubscriptionDto])
@general_rate_limit()
async def update_subscription(
    request: Request,
    subscription_id: int,
    command: UpdateSubscriptionCommand,
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionApplicationService = Depends(get_subscription_application_service)
):
    """更新訂閱"""
    command.subscription_id = subscription_id
    subscription = await service.update_subscription(current_user.id, command)
    
    return ApiResponse.success(
        data=subscription,
        message="訂閱更新成功"
    )

@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
@general_rate_limit()
async def delete_subscription(
    request: Request,
    subscription_id: int,
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionApplicationService = Depends(get_subscription_application_service)
):
    """刪除訂閱"""
    await service.delete_subscription(current_user.id, subscription_id)

@router.post("/bulk-operation", response_model=ApiResponse[bool])
@general_rate_limit()
async def bulk_subscription_operation(
    request: Request,
    command: BulkSubscriptionOperationCommand,
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionApplicationService = Depends(get_subscription_application_service)
):
    """批量操作訂閱"""
    result = await service.bulk_operation(current_user.id, command)
    
    return ApiResponse.success(
        data=result,
        message=f"批量{command.operation}操作完成"
    )