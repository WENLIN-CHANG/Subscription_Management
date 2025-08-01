"""
訂閱領域服務測試

測試核心業務邏輯：
- 價格計算 (月度/年度成本)
- 計費日期計算
- 類別分組和成本統計
- 數據驗證
- 匯率轉換
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from app.domain.services.subscription_domain_service import SubscriptionDomainService
from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory
from app.domain.interfaces.services import IExchangeRateService


class TestSubscriptionDomainService:
    """訂閱領域服務測試類"""

    @pytest.fixture
    def mock_exchange_service(self):
        """模擬匯率服務"""
        mock_service = Mock(spec=IExchangeRateService)
        mock_service.convert_currency = AsyncMock(return_value=30.0 * 100)  # 假設 USD to TWD = 30
        mock_service.get_exchange_rate = AsyncMock(return_value=30.0)
        return mock_service

    @pytest.fixture
    def domain_service(self, mock_exchange_service):
        """創建領域服務實例"""
        return SubscriptionDomainService(mock_exchange_service)

    @pytest.fixture
    def sample_monthly_subscription(self, test_user):
        """月度訂閱樣本"""
        return Subscription(
            id=1,
            name="Netflix",
            price=390.0,
            cycle=SubscriptionCycle.MONTHLY,
            category=SubscriptionCategory.ENTERTAINMENT,
            user_id=test_user.id,
            start_date=datetime(2024, 1, 1),
            is_active=True,
            currency="TWD"
        )

    @pytest.fixture
    def sample_yearly_subscription(self, test_user):
        """年度訂閱樣本"""
        return Subscription(
            id=2,
            name="Adobe Creative Cloud",
            price=1680.0,
            cycle=SubscriptionCycle.YEARLY,
            category=SubscriptionCategory.PRODUCTIVITY,
            user_id=test_user.id,
            start_date=datetime(2024, 1, 1),
            is_active=True,
            currency="TWD"
        )

    @pytest.fixture
    def sample_quarterly_subscription(self, test_user):
        """季度訂閱樣本"""
        return Subscription(
            id=3,
            name="Quarterly Service",
            price=600.0,
            cycle=SubscriptionCycle.QUARTERLY,
            category=SubscriptionCategory.PRODUCTIVITY,
            user_id=test_user.id,
            start_date=datetime(2024, 1, 1),
            is_active=True,
            currency="TWD"
        )

    @pytest.mark.unit
    @pytest.mark.domain
    class TestPriceCalculations:
        """價格計算測試"""

        def test_calculate_monthly_cost_monthly_subscription(self, domain_service, sample_monthly_subscription):
            """測試月度訂閱的月度成本計算"""
            cost = domain_service.calculate_monthly_cost(sample_monthly_subscription)
            assert cost == 390.0

        def test_calculate_monthly_cost_yearly_subscription(self, domain_service, sample_yearly_subscription):
            """測試年度訂閱的月度成本計算"""
            cost = domain_service.calculate_monthly_cost(sample_yearly_subscription)
            assert cost == 140.0  # 1680 / 12

        def test_calculate_monthly_cost_quarterly_subscription(self, domain_service, sample_quarterly_subscription):
            """測試季度訂閱的月度成本計算"""
            cost = domain_service.calculate_monthly_cost(sample_quarterly_subscription)
            assert cost == 200.0  # 600 / 3

        def test_calculate_yearly_cost_monthly_subscription(self, domain_service, sample_monthly_subscription):
            """測試月度訂閱的年度成本計算"""
            cost = domain_service.calculate_yearly_cost(sample_monthly_subscription)
            assert cost == 4680.0  # 390 * 12

        def test_calculate_yearly_cost_yearly_subscription(self, domain_service, sample_yearly_subscription):
            """測試年度訂閱的年度成本計算"""
            cost = domain_service.calculate_yearly_cost(sample_yearly_subscription)
            assert cost == 1680.0

        def test_calculate_yearly_cost_quarterly_subscription(self, domain_service, sample_quarterly_subscription):
            """測試季度訂閱的年度成本計算"""
            cost = domain_service.calculate_yearly_cost(sample_quarterly_subscription)
            assert cost == 2400.0  # 600 * 4

        def test_unsupported_cycle_raises_error(self, domain_service, test_user):
            """測試不支持的訂閱週期拋出錯誤"""
            subscription = Subscription(
                name="Invalid Cycle",
                price=100.0,
                cycle="weekly",  # 不支持的週期
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime.now(),
                is_active=True
            )
            
            with pytest.raises(ValueError, match="不支持的訂閱週期"):
                domain_service.calculate_monthly_cost(subscription)
            
            with pytest.raises(ValueError, match="不支持的訂閱週期"):
                domain_service.calculate_yearly_cost(subscription)

    @pytest.mark.unit
    @pytest.mark.domain
    class TestBillingDateCalculations:
        """計費日期計算測試"""

        def test_calculate_next_billing_date_monthly(self, domain_service, sample_monthly_subscription):
            """測試月度訂閱下次計費日期"""
            next_billing = domain_service.calculate_next_billing_date(sample_monthly_subscription)
            expected = datetime(2024, 2, 1)  # 2024-01-01 + 1 month
            assert next_billing == expected

        def test_calculate_next_billing_date_yearly(self, domain_service, sample_yearly_subscription):
            """測試年度訂閱下次計費日期"""
            next_billing = domain_service.calculate_next_billing_date(sample_yearly_subscription)
            expected = datetime(2025, 1, 1)  # 2024-01-01 + 1 year
            assert next_billing == expected

        def test_calculate_next_billing_date_quarterly(self, domain_service, sample_quarterly_subscription):
            """測試季度訂閱下次計費日期"""
            next_billing = domain_service.calculate_next_billing_date(sample_quarterly_subscription)
            expected = datetime(2024, 4, 1)  # 2024-01-01 + 3 months
            assert next_billing == expected

        def test_is_due_soon_true(self, domain_service, test_user):
            """測試即將到期的訂閱"""
            # 創建一個5天後到期的訂閱
            start_date = datetime.now() - relativedelta(months=1) + timedelta(days=5)
            subscription = Subscription(
                name="Due Soon",
                price=100.0,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=start_date,
                is_active=True
            )
            
            assert domain_service.is_due_soon(subscription, days_ahead=7) is True

        def test_is_due_soon_false(self, domain_service, test_user):
            """測試不即將到期的訂閱"""
            # 創建一個20天後到期的訂閱
            start_date = datetime.now() - relativedelta(months=1) + timedelta(days=20)
            subscription = Subscription(
                name="Not Due Soon",
                price=100.0,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=start_date,
                is_active=True
            )
            
            assert domain_service.is_due_soon(subscription, days_ahead=7) is False

    @pytest.mark.unit
    @pytest.mark.domain
    class TestAggregateCalculations:
        """聚合計算測試"""

        def test_calculate_total_monthly_cost(self, domain_service, test_user):
            """測試總月度成本計算"""
            subscriptions = [
                Subscription(
                    name="Service 1",
                    price=100.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                ),
                Subscription(
                    name="Service 2",
                    price=1200.0,
                    cycle=SubscriptionCycle.YEARLY,
                    category=SubscriptionCategory.PRODUCTIVITY,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                )
            ]
            
            total = domain_service.calculate_total_monthly_cost(subscriptions)
            assert total == 200.0  # 100 + (1200/12)

        def test_calculate_total_yearly_cost(self, domain_service, test_user):
            """測試總年度成本計算"""
            subscriptions = [
                Subscription(
                    name="Service 1",
                    price=100.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                ),
                Subscription(
                    name="Service 2",
                    price=1200.0,
                    cycle=SubscriptionCycle.YEARLY,
                    category=SubscriptionCategory.PRODUCTIVITY,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                )
            ]
            
            total = domain_service.calculate_total_yearly_cost(subscriptions)
            assert total == 2400.0  # (100*12) + 1200

        def test_ignore_inactive_subscriptions(self, domain_service, test_user):
            """測試忽略非活躍訂閱"""
            subscriptions = [
                Subscription(
                    name="Active Service",
                    price=100.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                ),
                Subscription(
                    name="Inactive Service",
                    price=200.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.PRODUCTIVITY,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=False
                )
            ]
            
            monthly_total = domain_service.calculate_total_monthly_cost(subscriptions)
            yearly_total = domain_service.calculate_total_yearly_cost(subscriptions)
            
            assert monthly_total == 100.0  # 只計算活躍的
            assert yearly_total == 1200.0   # 只計算活躍的

    @pytest.mark.unit
    @pytest.mark.domain
    class TestCategoryGrouping:
        """類別分組測試"""

        def test_group_by_category(self, domain_service, test_user):
            """測試按類別分組"""
            subscriptions = [
                Subscription(
                    name="Netflix",
                    price=100.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                ),
                Subscription(
                    name="Spotify",
                    price=50.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.MUSIC,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                ),
                Subscription(
                    name="Disney+",
                    price=80.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                )
            ]
            
            grouped = domain_service.group_by_category(subscriptions)
            
            assert "entertainment" in grouped
            assert "music" in grouped
            assert len(grouped["entertainment"]) == 2
            assert len(grouped["music"]) == 1

        def test_calculate_category_costs(self, domain_service, test_user):
            """測試類別成本計算"""
            subscriptions = [
                Subscription(
                    name="Netflix",
                    price=100.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                ),
                Subscription(
                    name="Adobe",
                    price=1200.0,
                    cycle=SubscriptionCycle.YEARLY,
                    category=SubscriptionCategory.PRODUCTIVITY,
                    user_id=test_user.id,
                    start_date=datetime.now(),
                    is_active=True
                )
            ]
            
            category_costs = domain_service.calculate_category_costs(subscriptions)
            
            assert category_costs["entertainment"] == 100.0
            assert category_costs["productivity"] == 100.0  # 1200/12

    @pytest.mark.unit
    @pytest.mark.domain
    class TestCurrencyConversion:
        """匯率轉換測試"""

        @pytest.mark.asyncio
        async def test_calculate_twd_price_twd_currency(self, domain_service):
            """測試台幣價格無需轉換"""
            twd_price = await domain_service.calculate_twd_price(100.0, "TWD")
            assert twd_price == 100.0

        @pytest.mark.asyncio
        async def test_calculate_twd_price_foreign_currency(self, domain_service, mock_exchange_service):
            """測試外幣轉換台幣"""
            mock_exchange_service.convert_currency.return_value = 3000.0  # $100 USD = 3000 TWD
            
            twd_price = await domain_service.calculate_twd_price(100.0, "USD")
            
            assert twd_price == 3000.0
            mock_exchange_service.convert_currency.assert_called_once_with(100.0, "USD", "TWD")

    @pytest.mark.unit
    @pytest.mark.domain
    class TestDataValidation:
        """數據驗證測試"""

        @pytest.mark.asyncio
        async def test_validate_subscription_data_valid(self, domain_service):
            """測試有效訂閱數據驗證"""
            result = await domain_service.validate_subscription_data("Netflix", 390.0, "TWD")
            
            assert result["is_valid"] is True
            assert len(result["errors"]) == 0

        @pytest.mark.asyncio
        async def test_validate_subscription_data_empty_name(self, domain_service):
            """測試空名稱驗證"""
            result = await domain_service.validate_subscription_data("", 390.0, "TWD")
            
            assert result["is_valid"] is False
            assert "訂閱名稱不能為空" in result["errors"]

        @pytest.mark.asyncio
        async def test_validate_subscription_data_invalid_price(self, domain_service):
            """測試無效價格驗證"""
            result = await domain_service.validate_subscription_data("Netflix", 0.0, "TWD")
            
            assert result["is_valid"] is False
            assert "價格必須大於0" in result["errors"]

        @pytest.mark.asyncio
        async def test_validate_subscription_data_unsupported_currency(self, domain_service):
            """測試不支持的貨幣驗證"""
            result = await domain_service.validate_subscription_data("Netflix", 390.0, "XYZ")
            
            assert result["is_valid"] is False
            assert "不支持的貨幣類型" in result["errors"]

        @pytest.mark.asyncio
        async def test_validate_subscription_data_exchange_rate_error(self, domain_service, mock_exchange_service):
            """測試匯率獲取錯誤驗證"""
            mock_exchange_service.get_exchange_rate.side_effect = Exception("API Error")
            
            result = await domain_service.validate_subscription_data("Netflix", 10.0, "USD")
            
            assert result["is_valid"] is False
            assert "無法獲取 USD 到 TWD 的匯率" in result["errors"]

        @pytest.mark.asyncio
        async def test_validate_subscription_data_multiple_errors(self, domain_service):
            """測試多個錯誤同時出現"""
            result = await domain_service.validate_subscription_data("", -10.0, "XYZ")
            
            assert result["is_valid"] is False
            assert len(result["errors"]) == 3  # 空名稱 + 負價格 + 不支持貨幣