from typing import Optional
from fastapi import HTTPException, status

from app.domain.interfaces.repositories import IUnitOfWork
from app.domain.services.budget_domain_service import BudgetDomainService
from app.application.dtos.budget_dtos import (
    CreateBudgetCommand,
    UpdateBudgetCommand,
    BudgetQuery,
    BudgetDto,
    BudgetUsageDto,
    BudgetAnalyticsDto
)
from app.models.budget import Budget

class BudgetApplicationService:
    """預算應用服務"""
    
    def __init__(self, uow: IUnitOfWork, domain_service: BudgetDomainService):
        self._uow = uow
        self._domain_service = domain_service
    
    async def create_budget(self, user_id: int, command: CreateBudgetCommand) -> BudgetDto:
        """創建預算"""
        try:
            # 驗證數據
            validation = self._domain_service.validate_budget_data(command.monthly_limit)
            
            if not validation["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"errors": validation["errors"]}
                )
            
            # 檢查用戶是否已經有預算
            existing_budget = self._uow.budgets.get_by_user_id(user_id)
            if existing_budget:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用戶已經有預算設置，請使用更新功能"
                )
            
            # 創建預算實體
            budget = Budget(
                user_id=user_id,
                monthly_limit=command.monthly_limit
            )
            
            # 保存到資料庫
            self._uow.begin()
            created_budget = self._uow.budgets.create(budget)
            self._uow.commit()
            
            return BudgetDto.model_validate(created_budget)
            
        except Exception as e:
            self._uow.rollback()
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="創建預算失敗"
            )
        finally:
            self._uow.close()
    
    async def get_budget(self, user_id: int) -> Optional[BudgetDto]:
        """獲取用戶預算"""
        budget = self._uow.budgets.get_by_user_id(user_id)
        
        if not budget:
            return None
        
        return BudgetDto.model_validate(budget)
    
    async def update_budget(self, user_id: int, command: UpdateBudgetCommand) -> BudgetDto:
        """更新預算"""
        try:
            budget = self._uow.budgets.get_by_user_id(user_id)
            
            if not budget:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="預算不存在"
                )
            
            if budget.id != command.budget_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="無權限修改此預算"
                )
            
            # 驗證數據
            if command.monthly_limit is not None:
                validation = self._domain_service.validate_budget_data(command.monthly_limit)
                if not validation["is_valid"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"errors": validation["errors"]}
                    )
            
            self._uow.begin()
            
            # 更新字段
            if command.monthly_limit is not None:
                budget.monthly_limit = command.monthly_limit
            
            updated_budget = self._uow.budgets.update(budget)
            self._uow.commit()
            
            return BudgetDto.model_validate(updated_budget)
            
        except Exception as e:
            self._uow.rollback()
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新預算失敗"
            )
        finally:
            self._uow.close()
    
    async def delete_budget(self, user_id: int) -> bool:
        """刪除預算"""
        try:
            budget = self._uow.budgets.get_by_user_id(user_id)
            
            if not budget:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="預算不存在"
                )
            
            self._uow.begin()
            result = self._uow.budgets.delete(budget.id)
            self._uow.commit()
            
            return result
            
        except Exception as e:
            self._uow.rollback()
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="刪除預算失敗"
            )
        finally:
            self._uow.close()
    
    async def get_budget_usage(self, user_id: int) -> BudgetUsageDto:
        """獲取預算使用情況"""
        budget = self._uow.budgets.get_by_user_id(user_id)
        subscriptions = self._uow.subscriptions.get_active_by_user_id(user_id)
        
        usage_info = self._domain_service.calculate_budget_usage(budget, subscriptions)
        category_usage = self._domain_service.calculate_category_budget_usage(budget, subscriptions)
        recommendations = self._domain_service.get_budget_recommendations(budget, subscriptions)
        savings_potential = self._domain_service.calculate_savings_potential(subscriptions)
        
        budget_dto = BudgetDto.model_validate(budget) if budget else None
        
        return BudgetUsageDto(
            budget=budget_dto,
            usage_info=usage_info,
            category_usage=category_usage,
            recommendations=recommendations,
            savings_potential=savings_potential
        )
    
    async def get_budget_analytics(self, user_id: int) -> BudgetAnalyticsDto:
        """獲取預算分析數據"""
        current_usage = await self.get_budget_usage(user_id)
        
        # 這裡可以添加歷史數據比較和趨勢分析的邏輯
        # 暫時返回基本的分析數據
        trend_analysis = {
            "trend": "stable",  # 可以是 'increasing', 'decreasing', 'stable'
            "change_percentage": 0,
            "period": "month"
        }
        
        return BudgetAnalyticsDto(
            current_month=current_usage,
            previous_month_comparison=None,  # 需要實現歷史數據追蹤
            trend_analysis=trend_analysis
        )