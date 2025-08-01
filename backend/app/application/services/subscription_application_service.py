from typing import List, Optional
from fastapi import HTTPException, status

from app.domain.interfaces.repositories import IUnitOfWork
from app.domain.services.subscription_domain_service import SubscriptionDomainService
from app.application.dtos.subscription_dtos import (
    CreateSubscriptionCommand,
    UpdateSubscriptionCommand,
    SubscriptionQuery,
    SubscriptionDto,
    SubscriptionSummaryDto,
    BulkSubscriptionOperationCommand
)
from app.models.subscription import Subscription

class SubscriptionApplicationService:
    """訂閱應用服務 - 協調領域服務和基礎設施"""
    
    def __init__(self, uow: IUnitOfWork, domain_service: SubscriptionDomainService):
        self._uow = uow
        self._domain_service = domain_service
    
    async def create_subscription(self, user_id: int, command: CreateSubscriptionCommand) -> SubscriptionDto:
        """創建訂閱"""
        try:
            # 驗證數據
            validation = await self._domain_service.validate_subscription_data(
                command.name, command.original_price, command.currency.value
            )
            
            if not validation["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"errors": validation["errors"]}
                )
            
            # 計算台幣價格
            twd_price = await self._domain_service.calculate_twd_price(
                command.original_price, command.currency.value
            )
            
            # 創建訂閱實體
            subscription = Subscription(
                user_id=user_id,
                name=command.name,
                price=twd_price,
                original_price=command.original_price,
                currency=command.currency,
                cycle=command.cycle,
                category=command.category,
                start_date=command.start_date
            )
            
            # 保存到資料庫
            self._uow.begin()
            created_subscription = self._uow.subscriptions.create(subscription)
            self._uow.commit()
            
            # 轉換為 DTO 返回
            return await self._to_subscription_dto(created_subscription)
            
        except Exception as e:
            self._uow.rollback()
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="創建訂閱失敗"
            )
        finally:
            self._uow.close()
    
    async def get_subscriptions(self, query: SubscriptionQuery) -> List[SubscriptionDto]:
        """獲取訂閱列表"""
        try:
            if query.include_inactive:
                subscriptions = self._uow.subscriptions.get_by_user_id(query.user_id)
            else:
                subscriptions = self._uow.subscriptions.get_active_by_user_id(query.user_id)
            
            # 按類別過濾
            if query.category:
                subscriptions = [s for s in subscriptions if s.category == query.category]
            
            # 轉換為 DTO
            result = []
            for subscription in subscriptions:
                dto = await self._to_subscription_dto(subscription)
                result.append(dto)
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取訂閱列表失敗"
            )
    
    async def get_subscription(self, user_id: int, subscription_id: int) -> SubscriptionDto:
        """獲取單個訂閱"""
        subscription = self._uow.subscriptions.get_by_user_and_id(user_id, subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="訂閱不存在"
            )
        
        return await self._to_subscription_dto(subscription)
    
    async def update_subscription(self, user_id: int, command: UpdateSubscriptionCommand) -> SubscriptionDto:
        """更新訂閱"""
        try:
            subscription = self._uow.subscriptions.get_by_user_and_id(user_id, command.subscription_id)
            
            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="訂閱不存在"
                )
            
            self._uow.begin()
            
            # 更新字段
            if command.name is not None:
                subscription.name = command.name
            if command.original_price is not None:
                subscription.original_price = command.original_price
            if command.currency is not None:
                subscription.currency = command.currency
            if command.cycle is not None:
                subscription.cycle = command.cycle
            if command.category is not None:
                subscription.category = command.category
            if command.start_date is not None:
                subscription.start_date = command.start_date
            if command.is_active is not None:
                subscription.is_active = command.is_active
            
            # 如果價格或貨幣有變化，重新計算台幣價格
            if command.original_price is not None or command.currency is not None:
                current_currency = command.currency.value if command.currency else subscription.currency.value
                current_price = command.original_price if command.original_price is not None else subscription.original_price
                
                subscription.price = await self._domain_service.calculate_twd_price(
                    current_price, current_currency
                )
            
            updated_subscription = self._uow.subscriptions.update(subscription)
            self._uow.commit()
            
            return await self._to_subscription_dto(updated_subscription)
            
        except Exception as e:
            self._uow.rollback()
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新訂閱失敗"
            )
        finally:
            self._uow.close()
    
    async def delete_subscription(self, user_id: int, subscription_id: int) -> bool:
        """刪除訂閱"""
        try:
            subscription = self._uow.subscriptions.get_by_user_and_id(user_id, subscription_id)
            
            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="訂閱不存在"
                )
            
            self._uow.begin()
            result = self._uow.subscriptions.delete(subscription_id)
            self._uow.commit()
            
            return result
            
        except Exception as e:
            self._uow.rollback()
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="刪除訂閱失敗"
            )
        finally:
            self._uow.close()
    
    async def get_subscription_summary(self, user_id: int) -> SubscriptionSummaryDto:
        """獲取訂閱摘要"""
        subscriptions = self._uow.subscriptions.get_by_user_id(user_id)
        active_subscriptions = [s for s in subscriptions if s.is_active]
        
        total_monthly_cost = self._domain_service.calculate_total_monthly_cost(subscriptions)
        total_yearly_cost = self._domain_service.calculate_total_yearly_cost(subscriptions)
        category_costs = self._domain_service.calculate_category_costs(subscriptions)
        
        # 找出即將續費的訂閱
        upcoming_renewals = []
        for subscription in active_subscriptions:
            if self._domain_service.is_due_soon(subscription, days_ahead=7):
                dto = await self._to_subscription_dto(subscription)
                upcoming_renewals.append(dto)
        
        return SubscriptionSummaryDto(
            total_subscriptions=len(subscriptions),
            active_subscriptions=len(active_subscriptions),
            total_monthly_cost=total_monthly_cost,
            total_yearly_cost=total_yearly_cost,
            categories=category_costs,
            upcoming_renewals=upcoming_renewals
        )
    
    async def bulk_operation(self, user_id: int, command: BulkSubscriptionOperationCommand) -> bool:
        """批量操作訂閱"""
        try:
            self._uow.begin()
            
            for subscription_id in command.subscription_ids:
                subscription = self._uow.subscriptions.get_by_user_and_id(user_id, subscription_id)
                
                if subscription:
                    if command.operation == "activate":
                        subscription.is_active = True
                        self._uow.subscriptions.update(subscription)
                    elif command.operation == "deactivate":
                        subscription.is_active = False
                        self._uow.subscriptions.update(subscription)
                    elif command.operation == "delete":
                        self._uow.subscriptions.delete(subscription_id)
            
            self._uow.commit()
            return True
            
        except Exception as e:
            self._uow.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="批量操作失敗"
            )
        finally:
            self._uow.close()
    
    async def _to_subscription_dto(self, subscription: Subscription) -> SubscriptionDto:
        """轉換為 DTO"""
        dto = SubscriptionDto.model_validate(subscription)
        dto.monthly_cost = self._domain_service.calculate_monthly_cost(subscription)
        dto.yearly_cost = self._domain_service.calculate_yearly_cost(subscription)
        dto.next_billing_date = self._domain_service.calculate_next_billing_date(subscription)
        return dto