"""
訂閱應用服務測試

測試應用層業務流程：
- 創建訂閱流程
- 查詢訂閱邏輯
- 更新訂閱邏輯
- 刪除訂閱邏輯
- 批量操作邏輯
- 摘要統計邏輯
- 異常處理和事務管理
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from datetime import datetime

from app.application.services.subscription_application_service import SubscriptionApplicationService
from app.domain.services.subscription_domain_service import SubscriptionDomainService
from app.domain.interfaces.repositories import IUnitOfWork, ISubscriptionRepository
from app.application.dtos.subscription_dtos import (
    CreateSubscriptionCommand,
    UpdateSubscriptionCommand,
    SubscriptionQuery,
    BulkSubscriptionOperationCommand
)
from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency


class TestSubscriptionApplicationService:
    """訂閱應用服務測試類"""

    @pytest.fixture
    def mock_uow(self):
        """模擬 Unit of Work"""
        mock_uow = Mock(spec=IUnitOfWork)
        mock_uow.subscriptions = Mock(spec=ISubscriptionRepository)
        mock_uow.begin = Mock()
        mock_uow.commit = Mock()
        mock_uow.rollback = Mock()
        mock_uow.close = Mock()
        return mock_uow

    @pytest.fixture
    def mock_domain_service(self):
        """模擬領域服務"""
        mock_service = Mock(spec=SubscriptionDomainService)
        mock_service.validate_subscription_data = AsyncMock()
        mock_service.calculate_twd_price = AsyncMock()
        mock_service.calculate_monthly_cost = Mock()
        mock_service.calculate_yearly_cost = Mock()
        mock_service.calculate_next_billing_date = Mock()
        mock_service.calculate_total_monthly_cost = Mock()
        mock_service.calculate_total_yearly_cost = Mock()
        mock_service.calculate_category_costs = Mock()
        mock_service.is_due_soon = Mock()
        return mock_service

    @pytest.fixture
    def app_service(self, mock_uow, mock_domain_service):
        """創建應用服務實例"""
        return SubscriptionApplicationService(mock_uow, mock_domain_service)

    @pytest.fixture
    def sample_subscription(self, test_user):
        """訂閱樣本"""
        return Subscription(
            id=1,
            name="Netflix",
            price=390.0,
            original_price=390.0,
            currency=Currency.TWD,
            cycle=SubscriptionCycle.MONTHLY,
            category=SubscriptionCategory.ENTERTAINMENT,
            user_id=test_user.id,
            start_date=datetime(2024, 1, 1),
            is_active=True
        )

    @pytest.mark.unit
    @pytest.mark.application
    class TestCreateSubscription:
        """創建訂閱測試"""

        @pytest.mark.asyncio
        async def test_create_subscription_success(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscription):
            """測試成功創建訂閱"""
            # 準備數據
            command = CreateSubscriptionCommand(
                name="Netflix",
                original_price=390.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                start_date=datetime(2024, 1, 1)
            )
            
            # 模擬驗證成功
            mock_domain_service.validate_subscription_data.return_value = {
                "is_valid": True,
                "errors": []
            }
            mock_domain_service.calculate_twd_price.return_value = 390.0
            mock_uow.subscriptions.create.return_value = sample_subscription
            
            # 模擬 DTO 轉換所需的計算
            mock_domain_service.calculate_monthly_cost.return_value = 390.0
            mock_domain_service.calculate_yearly_cost.return_value = 4680.0
            mock_domain_service.calculate_next_billing_date.return_value = datetime(2024, 2, 1)
            
            # 執行測試
            result = await app_service.create_subscription(test_user.id, command)
            
            # 驗證結果
            assert result.name == "Netflix"
            assert result.price == 390.0
            assert result.monthly_cost == 390.0
            
            # 驗證調用
            mock_domain_service.validate_subscription_data.assert_called_once()
            mock_domain_service.calculate_twd_price.assert_called_once_with(390.0, "TWD")
            mock_uow.begin.assert_called_once()
            mock_uow.subscriptions.create.assert_called_once()
            mock_uow.commit.assert_called_once()
            mock_uow.close.assert_called_once()

        @pytest.mark.asyncio
        async def test_create_subscription_validation_error(self, app_service, mock_domain_service, test_user):
            """測試創建訂閱時數據驗證失敗"""
            command = CreateSubscriptionCommand(
                name="",  # 空名稱
                original_price=0.0,  # 無效價格
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                start_date=datetime(2024, 1, 1)
            )
            
            # 模擬驗證失敗
            mock_domain_service.validate_subscription_data.return_value = {
                "is_valid": False,
                "errors": ["訂閱名稱不能為空", "價格必須大於0"]
            }
            
            # 執行測試並期望異常
            with pytest.raises(HTTPException) as exc_info:
                await app_service.create_subscription(test_user.id, command)
            
            assert exc_info.value.status_code == 400
            assert "errors" in exc_info.value.detail

        @pytest.mark.asyncio
        async def test_create_subscription_database_error(self, app_service, mock_uow, mock_domain_service, test_user):
            """測試創建訂閱時數據庫錯誤"""
            command = CreateSubscriptionCommand(
                name="Netflix",
                original_price=390.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                start_date=datetime(2024, 1, 1)
            )
            
            # 模擬驗證成功但數據庫操作失敗
            mock_domain_service.validate_subscription_data.return_value = {"is_valid": True, "errors": []}
            mock_domain_service.calculate_twd_price.return_value = 390.0
            mock_uow.subscriptions.create.side_effect = Exception("數據庫錯誤")
            
            # 執行測試並期望異常
            with pytest.raises(HTTPException) as exc_info:
                await app_service.create_subscription(test_user.id, command)
            
            assert exc_info.value.status_code == 500
            assert "創建訂閱失敗" in exc_info.value.detail
            
            # 驗證事務回滾和資源清理
            mock_uow.rollback.assert_called_once()
            mock_uow.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.application
    class TestGetSubscriptions:
        """獲取訂閱列表測試"""

        @pytest.mark.asyncio
        async def test_get_subscriptions_active_only(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscription):
            """測試獲取僅活躍訂閱"""
            query = SubscriptionQuery(user_id=test_user.id, include_inactive=False)
            
            mock_uow.subscriptions.get_active_by_user_id.return_value = [sample_subscription]
            mock_domain_service.calculate_monthly_cost.return_value = 390.0
            mock_domain_service.calculate_yearly_cost.return_value = 4680.0
            mock_domain_service.calculate_next_billing_date.return_value = datetime(2024, 2, 1)
            
            result = await app_service.get_subscriptions(query)
            
            assert len(result) == 1
            assert result[0].name == "Netflix"
            mock_uow.subscriptions.get_active_by_user_id.assert_called_once_with(test_user.id)

        @pytest.mark.asyncio
        async def test_get_subscriptions_include_inactive(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscription):
            """測試獲取包含非活躍訂閱"""
            query = SubscriptionQuery(user_id=test_user.id, include_inactive=True)
            
            mock_uow.subscriptions.get_by_user_id.return_value = [sample_subscription]
            mock_domain_service.calculate_monthly_cost.return_value = 390.0
            mock_domain_service.calculate_yearly_cost.return_value = 4680.0
            mock_domain_service.calculate_next_billing_date.return_value = datetime(2024, 2, 1)
            
            result = await app_service.get_subscriptions(query)
            
            assert len(result) == 1
            mock_uow.subscriptions.get_by_user_id.assert_called_once_with(test_user.id)

        @pytest.mark.asyncio
        async def test_get_subscriptions_filter_by_category(self, app_service, mock_uow, mock_domain_service, test_user):
            """測試按類別過濾訂閱"""
            # 創建不同類別的訂閱
            entertainment_sub = Subscription(
                id=1,
                name="Netflix",
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                is_active=True
            )
            
            productivity_sub = Subscription(
                id=2,
                name="Adobe",
                category=SubscriptionCategory.PRODUCTIVITY,
                user_id=test_user.id,
                is_active=True
            )
            
            query = SubscriptionQuery(
                user_id=test_user.id,
                category=SubscriptionCategory.ENTERTAINMENT,
                include_inactive=False
            )
            
            mock_uow.subscriptions.get_active_by_user_id.return_value = [entertainment_sub, productivity_sub]
            mock_domain_service.calculate_monthly_cost.return_value = 390.0
            mock_domain_service.calculate_yearly_cost.return_value = 4680.0
            mock_domain_service.calculate_next_billing_date.return_value = datetime(2024, 2, 1)
            
            result = await app_service.get_subscriptions(query)
            
            # 應該只返回娛樂類別的訂閱
            assert len(result) == 1
            assert result[0].name == "Netflix"

    @pytest.mark.unit
    @pytest.mark.application
    class TestGetSubscription:
        """獲取單個訂閱測試"""

        @pytest.mark.asyncio
        async def test_get_subscription_success(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscription):
            """測試成功獲取單個訂閱"""
            mock_uow.subscriptions.get_by_user_and_id.return_value = sample_subscription
            mock_domain_service.calculate_monthly_cost.return_value = 390.0
            mock_domain_service.calculate_yearly_cost.return_value = 4680.0
            mock_domain_service.calculate_next_billing_date.return_value = datetime(2024, 2, 1)
            
            result = await app_service.get_subscription(test_user.id, 1)
            
            assert result.name == "Netflix"
            mock_uow.subscriptions.get_by_user_and_id.assert_called_once_with(test_user.id, 1)

        @pytest.mark.asyncio
        async def test_get_subscription_not_found(self, app_service, mock_uow, test_user):
            """測試訂閱不存在"""
            mock_uow.subscriptions.get_by_user_and_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.get_subscription(test_user.id, 999)
            
            assert exc_info.value.status_code == 404
            assert "訂閱不存在" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.application
    class TestUpdateSubscription:
        """更新訂閱測試"""

        @pytest.mark.asyncio
        async def test_update_subscription_success(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscription):
            """測試成功更新訂閱"""
            command = UpdateSubscriptionCommand(
                subscription_id=1,
                name="Netflix Premium",
                original_price=490.0
            )
            
            mock_uow.subscriptions.get_by_user_and_id.return_value = sample_subscription
            mock_domain_service.calculate_twd_price.return_value = 490.0
            mock_uow.subscriptions.update.return_value = sample_subscription
            mock_domain_service.calculate_monthly_cost.return_value = 490.0
            mock_domain_service.calculate_yearly_cost.return_value = 5880.0
            mock_domain_service.calculate_next_billing_date.return_value = datetime(2024, 2, 1)
            
            result = await app_service.update_subscription(test_user.id, command)
            
            assert result is not None
            mock_uow.begin.assert_called_once()
            mock_uow.subscriptions.update.assert_called_once()
            mock_uow.commit.assert_called_once()
            mock_uow.close.assert_called_once()

        @pytest.mark.asyncio
        async def test_update_subscription_not_found(self, app_service, mock_uow, test_user):
            """測試更新不存在的訂閱"""
            command = UpdateSubscriptionCommand(subscription_id=999, name="New Name")
            
            mock_uow.subscriptions.get_by_user_and_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.update_subscription(test_user.id, command)
            
            assert exc_info.value.status_code == 404

        @pytest.mark.asyncio
        async def test_update_subscription_recalculate_price(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscription):
            """測試更新價格時重新計算台幣價格"""
            command = UpdateSubscriptionCommand(
                subscription_id=1,
                original_price=10.0,
                currency=Currency.USD
            )
            
            mock_uow.subscriptions.get_by_user_and_id.return_value = sample_subscription
            mock_domain_service.calculate_twd_price.return_value = 300.0  # 假設匯率轉換結果
            mock_uow.subscriptions.update.return_value = sample_subscription
            mock_domain_service.calculate_monthly_cost.return_value = 300.0
            mock_domain_service.calculate_yearly_cost.return_value = 3600.0
            mock_domain_service.calculate_next_billing_date.return_value = datetime(2024, 2, 1)
            
            await app_service.update_subscription(test_user.id, command)
            
            # 驗證重新計算了台幣價格
            mock_domain_service.calculate_twd_price.assert_called_once_with(10.0, "USD")

    @pytest.mark.unit
    @pytest.mark.application
    class TestDeleteSubscription:
        """刪除訂閱測試"""

        @pytest.mark.asyncio
        async def test_delete_subscription_success(self, app_service, mock_uow, test_user, sample_subscription):
            """測試成功刪除訂閱"""
            mock_uow.subscriptions.get_by_user_and_id.return_value = sample_subscription
            mock_uow.subscriptions.delete.return_value = True
            
            result = await app_service.delete_subscription(test_user.id, 1)
            
            assert result is True
            mock_uow.begin.assert_called_once()
            mock_uow.subscriptions.delete.assert_called_once_with(1)
            mock_uow.commit.assert_called_once()
            mock_uow.close.assert_called_once()

        @pytest.mark.asyncio
        async def test_delete_subscription_not_found(self, app_service, mock_uow, test_user):
            """測試刪除不存在的訂閱"""
            mock_uow.subscriptions.get_by_user_and_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.delete_subscription(test_user.id, 999)
            
            assert exc_info.value.status_code == 404

    @pytest.mark.unit
    @pytest.mark.application
    class TestGetSubscriptionSummary:
        """獲取訂閱摘要測試"""

        @pytest.mark.asyncio
        async def test_get_subscription_summary(self, app_service, mock_uow, mock_domain_service, test_user, sample_subscription):
            """測試獲取訂閱摘要"""
            inactive_subscription = Subscription(
                id=2,
                name="Inactive Service",
                is_active=False,
                user_id=test_user.id
            )
            
            subscriptions = [sample_subscription, inactive_subscription]
            
            mock_uow.subscriptions.get_by_user_id.return_value = subscriptions
            mock_domain_service.calculate_total_monthly_cost.return_value = 390.0
            mock_domain_service.calculate_total_yearly_cost.return_value = 4680.0
            mock_domain_service.calculate_category_costs.return_value = {"entertainment": 390.0}
            mock_domain_service.is_due_soon.return_value = True
            mock_domain_service.calculate_monthly_cost.return_value = 390.0
            mock_domain_service.calculate_yearly_cost.return_value = 4680.0
            mock_domain_service.calculate_next_billing_date.return_value = datetime(2024, 2, 1)
            
            result = await app_service.get_subscription_summary(test_user.id)
            
            assert result.total_subscriptions == 2
            assert result.active_subscriptions == 1
            assert result.total_monthly_cost == 390.0
            assert result.total_yearly_cost == 4680.0
            assert len(result.upcoming_renewals) == 1

    @pytest.mark.unit
    @pytest.mark.application
    class TestBulkOperation:
        """批量操作測試"""

        @pytest.mark.asyncio
        async def test_bulk_activate(self, app_service, mock_uow, test_user, sample_subscription):
            """測試批量啟用"""
            command = BulkSubscriptionOperationCommand(
                subscription_ids=[1, 2],
                operation="activate"
            )
            
            mock_uow.subscriptions.get_by_user_and_id.return_value = sample_subscription
            
            result = await app_service.bulk_operation(test_user.id, command)
            
            assert result is True
            mock_uow.begin.assert_called_once()
            mock_uow.commit.assert_called_once()
            mock_uow.close.assert_called_once()

        @pytest.mark.asyncio
        async def test_bulk_delete(self, app_service, mock_uow, test_user, sample_subscription):
            """測試批量刪除"""
            command = BulkSubscriptionOperationCommand(
                subscription_ids=[1, 2],
                operation="delete"
            )
            
            mock_uow.subscriptions.get_by_user_and_id.return_value = sample_subscription
            
            result = await app_service.bulk_operation(test_user.id, command)
            
            assert result is True
            # 應該調用刪除操作
            assert mock_uow.subscriptions.delete.call_count == 2

        @pytest.mark.asyncio
        async def test_bulk_operation_error_rollback(self, app_service, mock_uow, test_user):
            """測試批量操作錯誤時回滾"""
            command = BulkSubscriptionOperationCommand(
                subscription_ids=[1],
                operation="activate"
            )
            
            mock_uow.subscriptions.get_by_user_and_id.side_effect = Exception("數據庫錯誤")
            
            with pytest.raises(HTTPException) as exc_info:
                await app_service.bulk_operation(test_user.id, command)
            
            assert exc_info.value.status_code == 500
            mock_uow.rollback.assert_called_once()
            mock_uow.close.assert_called_once()