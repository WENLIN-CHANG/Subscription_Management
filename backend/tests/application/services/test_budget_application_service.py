"""
預算應用服務測試

測試應用層業務流程：
- 創建預算流程
- 查詢預算邏輯
- 更新預算邏輯
- 刪除預算邏輯
- 預算使用情況分析
- 預算分析和建議
- 異常處理和事務管理
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException

from app.application.services.budget_application_service import BudgetApplicationService
from app.domain.services.budget_domain_service import BudgetDomainService
from app.domain.interfaces.repositories import IUnitOfWork, IBudgetRepository, ISubscriptionRepository
from app.application.dtos.budget_dtos import (
    CreateBudgetCommand,
    UpdateBudgetCommand
)
from app.models.budget import Budget
from app.models.subscription import Subscription, SubscriptionCategory


class TestBudgetApplicationService:
    """預算應用服務測試類"""

    @pytest.fixture
    def mock_uow(self):
        """模擬 Unit of Work"""
        mock_uow = Mock(spec=IUnitOfWork)
        mock_uow.budgets = Mock(spec=IBudgetRepository)
        mock_uow.subscriptions = Mock(spec=ISubscriptionRepository)
        mock_uow.begin = Mock()
        mock_uow.commit = Mock()
        mock_uow.rollback = Mock()
        mock_uow.close = Mock()
        return mock_uow

    @pytest.fixture
    def mock_domain_service(self):
        """模擬預算領域服務"""
        mock_service = Mock(spec=BudgetDomainService)
        mock_service.validate_budget_data = Mock()
        mock_service.calculate_budget_usage = Mock()
        mock_service.calculate_category_budget_usage = Mock()
        mock_service.get_budget_recommendations = Mock()
        mock_service.calculate_savings_potential = Mock()
        return mock_service

    @pytest.fixture
    def app_service(self, mock_uow, mock_domain_service):
        """創建應用服務實例"""
        return BudgetApplicationService(mock_uow, mock_domain_service)

    @pytest.fixture
    def sample_budget(self, test_user):
        """預算樣本"""
        return Budget(
            id=1,
            user_id=test_user.id,
            monthly_limit=1000.0
        )

    @pytest.fixture
    def sample_subscriptions(self, test_user):
        """訂閱樣本列表"""
        return [
            Subscription(
                id=1,
                name="Netflix",
                price=390.0,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                is_active=True
            ),
            Subscription(
                id=2,
                name="Spotify",
                price=149.0,
                category=SubscriptionCategory.MUSIC,
                user_id=test_user.id,
                is_active=True
            )
        ]

    @pytest.mark.unit
    @pytest.mark.application
    class TestCreateBudget:
        """創建預算測試"""

        @pytest.mark.asyncio
        async def test_create_budget_success(self, app_service, mock_uow, mock_domain_service, test_user, sample_budget):
            """測試成功創建預算"""
            command = CreateBudgetCommand(monthly_limit=1000.0)
            
            # 模擬驗證成功
            mock_domain_service.validate_budget_data.return_value = {
                "is_valid": True,
                "errors": []
            }
            mock_uow.budgets.get_by_user_id.return_value = None  # 沒有現有預算
            mock_uow.budgets.create.return_value = sample_budget
            
            result = await app_service.create_budget(test_user.id, command)
            
            assert result.monthly_limit == 1000.0
            assert result.user_id == test_user.id
            
            # 驗證調用
            mock_domain_service.validate_budget_data.assert_called_once_with(1000.0)
            mock_uow.budgets.get_by_user_id.assert_called_once_with(test_user.id)
            mock_uow.begin.assert_called_once()
            mock_uow.budgets.create.assert_called_once()
            mock_uow.commit.assert_called_once()
            mock_uow.close.assert_called_once()

        @pytest.mark.asyncio
        async def test_create_budget_validation_error(self, app_service, mock_domain_service, test_user):
            """測試創建預算時數據驗證失敗"""
            command = CreateBudgetCommand(monthly_limit=-100.0)
            
            # 模擬驗證失敗
            mock_domain_service.validate_budget_data.return_value = {
                "is_valid": False,
                "errors": ["月度預算限制必須大於0"]
            }
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.create_budget(test_user.id, command)
            
            assert exc_info.value.status_code == 400
            assert "errors" in exc_info.value.detail

        @pytest.mark.asyncio
        async def test_create_budget_already_exists(self, app_service, mock_uow, mock_domain_service, test_user, sample_budget):
            """測試用戶已經有預算時不允許重複創建"""
            command = CreateBudgetCommand(monthly_limit=1000.0)
            
            mock_domain_service.validate_budget_data.return_value = {"is_valid": True, "errors": []}
            mock_uow.budgets.get_by_user_id.return_value = sample_budget  # 已存在預算
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.create_budget(test_user.id, command)
            
            assert exc_info.value.status_code == 400
            assert "已經有預算設置" in exc_info.value.detail

        @pytest.mark.asyncio
        async def test_create_budget_database_error(self, app_service, mock_uow, mock_domain_service, test_user):
            """測試創建預算時數據庫錯誤"""
            command = CreateBudgetCommand(monthly_limit=1000.0)
            
            mock_domain_service.validate_budget_data.return_value = {"is_valid": True, "errors": []}
            mock_uow.budgets.get_by_user_id.return_value = None
            mock_uow.budgets.create.side_effect = Exception("數據庫錯誤")
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.create_budget(test_user.id, command)
            
            assert exc_info.value.status_code == 500
            assert "創建預算失敗" in exc_info.value.detail
            
            # 驗證事務回滾和資源清理
            mock_uow.rollback.assert_called_once()
            mock_uow.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.application
    class TestGetBudget:
        """獲取預算測試"""

        @pytest.mark.asyncio
        async def test_get_budget_success(self, app_service, mock_uow, test_user, sample_budget):
            """測試成功獲取預算"""
            mock_uow.budgets.get_by_user_id.return_value = sample_budget
            
            result = await app_service.get_budget(test_user.id)
            
            assert result is not None
            assert result.monthly_limit == 1000.0
            mock_uow.budgets.get_by_user_id.assert_called_once_with(test_user.id)

        @pytest.mark.asyncio
        async def test_get_budget_not_found(self, app_service, mock_uow, test_user):
            """測試預算不存在"""
            mock_uow.budgets.get_by_user_id.return_value = None
            
            result = await app_service.get_budget(test_user.id)
            
            assert result is None

    @pytest.mark.unit
    @pytest.mark.application
    class TestUpdateBudget:
        """更新預算測試"""

        @pytest.mark.asyncio
        async def test_update_budget_success(self, app_service, mock_uow, mock_domain_service, test_user, sample_budget):
            """測試成功更新預算"""
            command = UpdateBudgetCommand(budget_id=1, monthly_limit=1500.0)
            
            mock_uow.budgets.get_by_user_id.return_value = sample_budget
            mock_domain_service.validate_budget_data.return_value = {"is_valid": True, "errors": []}
            mock_uow.budgets.update.return_value = sample_budget
            
            result = await app_service.update_budget(test_user.id, command)
            
            assert result is not None
            mock_uow.begin.assert_called_once()
            mock_uow.budgets.update.assert_called_once()
            mock_uow.commit.assert_called_once()
            mock_uow.close.assert_called_once()

        @pytest.mark.asyncio
        async def test_update_budget_not_found(self, app_service, mock_uow, test_user):
            """測試更新不存在的預算"""
            command = UpdateBudgetCommand(budget_id=999, monthly_limit=1500.0)
            
            mock_uow.budgets.get_by_user_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.update_budget(test_user.id, command)
            
            assert exc_info.value.status_code == 404
            assert "預算不存在" in exc_info.value.detail

        @pytest.mark.asyncio
        async def test_update_budget_permission_denied(self, app_service, mock_uow, test_user):
            """測試更新其他用戶的預算"""
            command = UpdateBudgetCommand(budget_id=999, monthly_limit=1500.0)  # 不同的ID
            
            sample_budget = Budget(id=1, user_id=test_user.id, monthly_limit=1000.0)  # ID為1，但命令要求更新999
            mock_uow.budgets.get_by_user_id.return_value = sample_budget
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.update_budget(test_user.id, command)
            
            assert exc_info.value.status_code == 403
            assert "無權限修改此預算" in exc_info.value.detail

        @pytest.mark.asyncio
        async def test_update_budget_validation_error(self, app_service, mock_uow, mock_domain_service, test_user, sample_budget):
            """測試更新預算時數據驗證失敗"""
            command = UpdateBudgetCommand(budget_id=1, monthly_limit=-100.0)
            
            mock_uow.budgets.get_by_user_id.return_value = sample_budget
            mock_domain_service.validate_budget_data.return_value = {
                "is_valid": False,
                "errors": ["月度預算限制必須大於0"]
            }
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.update_budget(test_user.id, command)
            
            assert exc_info.value.status_code == 400

    @pytest.mark.unit
    @pytest.mark.application
    class TestDeleteBudget:
        """刪除預算測試"""

        @pytest.mark.asyncio
        async def test_delete_budget_success(self, app_service, mock_uow, test_user, sample_budget):
            """測試成功刪除預算"""
            mock_uow.budgets.get_by_user_id.return_value = sample_budget
            mock_uow.budgets.delete.return_value = True
            
            result = await app_service.delete_budget(test_user.id)
            
            assert result is True
            mock_uow.begin.assert_called_once()
            mock_uow.budgets.delete.assert_called_once_with(1)
            mock_uow.commit.assert_called_once()
            mock_uow.close.assert_called_once()

        @pytest.mark.asyncio
        async def test_delete_budget_not_found(self, app_service, mock_uow, test_user):
            """測試刪除不存在的預算"""
            mock_uow.budgets.get_by_user_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.delete_budget(test_user.id)
            
            assert exc_info.value.status_code == 404

    @pytest.mark.unit
    @pytest.mark.application
    class TestGetBudgetUsage:
        """獲取預算使用情況測試"""

        @pytest.mark.asyncio
        async def test_get_budget_usage_with_budget(self, app_service, mock_uow, mock_domain_service, test_user, sample_budget, sample_subscriptions):
            """測試有預算時獲取使用情況"""
            mock_uow.budgets.get_by_user_id.return_value = sample_budget
            mock_uow.subscriptions.get_active_by_user_id.return_value = sample_subscriptions
            
            # 模擬領域服務返回值
            mock_domain_service.calculate_budget_usage.return_value = {
                "total_budget": 1000.0,
                "used_amount": 539.0,
                "remaining_amount": 461.0,
                "usage_percentage": 53.9,
                "is_over_budget": False,
                "over_budget_amount": 0
            }
            
            mock_domain_service.calculate_category_budget_usage.return_value = {
                "total_budget": 1000.0,
                "total_used": 539.0,
                "categories": {
                    "entertainment": {"cost": 390.0, "percentage_of_total": 72.4, "percentage_of_budget": 39.0},
                    "music": {"cost": 149.0, "percentage_of_total": 27.6, "percentage_of_budget": 14.9}
                }
            }
            
            mock_domain_service.get_budget_recommendations.return_value = [
                "預算使用率正常"
            ]
            
            mock_domain_service.calculate_savings_potential.return_value = {
                "current_yearly_cost": 6468.0,
                "potential_yearly_cost": 5821.2,
                "potential_annual_savings": 646.8,
                "savings_percentage": 10.0
            }
            
            result = await app_service.get_budget_usage(test_user.id)
            
            assert result.budget is not None
            assert result.budget.monthly_limit == 1000.0
            assert result.usage_info["total_budget"] == 1000.0
            assert result.usage_info["used_amount"] == 539.0
            assert len(result.categories) == 2
            assert len(result.recommendations) == 1
            assert result.savings_potential["potential_annual_savings"] == 646.8

        @pytest.mark.asyncio
        async def test_get_budget_usage_without_budget(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscriptions):
            """測試無預算時獲取使用情況"""
            mock_uow.budgets.get_by_user_id.return_value = None
            mock_uow.subscriptions.get_active_by_user_id.return_value = sample_subscriptions
            
            # 模擬無預算的情況
            mock_domain_service.calculate_budget_usage.return_value = {
                "total_budget": 0,
                "used_amount": 0,
                "remaining_amount": 0,
                "usage_percentage": 0,
                "is_over_budget": False,
                "over_budget_amount": 0
            }
            
            mock_domain_service.calculate_category_budget_usage.return_value = {
                "total_budget": 0,
                "total_used": 539.0,
                "categories": {}
            }
            
            mock_domain_service.get_budget_recommendations.return_value = [
                "建議設置月度預算限制以更好地管理訂閱支出"
            ]
            
            mock_domain_service.calculate_savings_potential.return_value = {
                "current_yearly_cost": 6468.0,
                "potential_yearly_cost": 5821.2,
                "potential_annual_savings": 646.8,
                "savings_percentage": 10.0
            }
            
            result = await app_service.get_budget_usage(test_user.id)
            
            assert result.budget is None
            assert result.usage_info["total_budget"] == 0
            assert "建議設置月度預算限制" in result.recommendations[0]

    @pytest.mark.unit
    @pytest.mark.application
    class TestGetBudgetAnalytics:
        """獲取預算分析測試"""

        @pytest.mark.asyncio
        async def test_get_budget_analytics(self, app_service, mock_uow, mock_domain_service, test_user, sample_budget, sample_subscriptions):
            """測試獲取預算分析數據"""
            # 首先需要模擬 get_budget_usage 的依賴
            mock_uow.budgets.get_by_user_id.return_value = sample_budget
            mock_uow.subscriptions.get_active_by_user_id.return_value = sample_subscriptions
            
            # 模擬領域服務返回值
            mock_domain_service.calculate_budget_usage.return_value = {
                "total_budget": 1000.0,
                "used_amount": 539.0,
                "remaining_amount": 461.0,
                "usage_percentage": 53.9,
                "is_over_budget": False,
                "over_budget_amount": 0
            }
            
            mock_domain_service.calculate_category_budget_usage.return_value = {
                "total_budget": 1000.0,
                "total_used": 539.0,
                "categories": {}
            }
            
            mock_domain_service.get_budget_recommendations.return_value = []
            mock_domain_service.calculate_savings_potential.return_value = {
                "current_yearly_cost": 6468.0,
                "potential_yearly_cost": 5821.2,
                "potential_annual_savings": 646.8,
                "savings_percentage": 10.0
            }
            
            result = await app_service.get_budget_analytics(test_user.id)
            
            assert result.current_month is not None
            assert result.current_month.budget is not None
            assert result.previous_month_comparison is None  # 暫時未實現
            assert result.trend_analysis["trend"] == "stable"
            assert result.trend_analysis["change_percentage"] == 0

        @pytest.mark.asyncio
        async def test_get_budget_analytics_no_budget(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscriptions):
            """測試無預算時的分析數據"""
            mock_uow.budgets.get_by_user_id.return_value = None
            mock_uow.subscriptions.get_active_by_user_id.return_value = sample_subscriptions
            
            # 模擬無預算的返回值
            mock_domain_service.calculate_budget_usage.return_value = {
                "total_budget": 0,
                "used_amount": 0,
                "remaining_amount": 0,
                "usage_percentage": 0,
                "is_over_budget": False,
                "over_budget_amount": 0
            }
            
            mock_domain_service.calculate_category_budget_usage.return_value = {
                "total_budget": 0,
                "total_used": 539.0,
                "categories": {}
            }
            
            mock_domain_service.get_budget_recommendations.return_value = [
                "建議設置月度預算限制"
            ]
            
            mock_domain_service.calculate_savings_potential.return_value = {
                "current_yearly_cost": 6468.0,
                "potential_yearly_cost": 5821.2,
                "potential_annual_savings": 646.8,
                "savings_percentage": 10.0
            }
            
            result = await app_service.get_budget_analytics(test_user.id)
            
            assert result.current_month is not None
            assert result.current_month.budget is None
            assert result.trend_analysis["trend"] == "stable"