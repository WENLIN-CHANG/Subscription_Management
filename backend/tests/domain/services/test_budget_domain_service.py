"""
預算領域服務測試

測試核心業務邏輯：
- 預算使用情況計算
- 類別預算分析
- 預算建議生成
- 節省潛力計算
- 數據驗證
"""

import pytest
from unittest.mock import Mock

from app.domain.services.budget_domain_service import BudgetDomainService
from app.domain.services.subscription_domain_service import SubscriptionDomainService
from app.models.budget import Budget
from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory


class TestBudgetDomainService:
    """預算領域服務測試類"""

    @pytest.fixture
    def mock_subscription_service(self):
        """模擬訂閱領域服務"""
        mock_service = Mock(spec=SubscriptionDomainService)
        return mock_service

    @pytest.fixture
    def budget_service(self, mock_subscription_service):
        """創建預算領域服務實例"""
        return BudgetDomainService(mock_subscription_service)

    @pytest.fixture
    def sample_budget(self, test_user):
        """預算樣本"""
        return Budget(
            id=1,
            category="entertainment",
            amount=1000.0,
            period="monthly",
            monthly_limit=1000.0,
            user_id=test_user.id
        )

    @pytest.fixture
    def sample_subscriptions(self, test_user):
        """訂閱樣本列表"""
        return [
            Subscription(
                id=1,
                name="Netflix",
                price=390.0,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                is_active=True
            ),
            Subscription(
                id=2,
                name="Spotify",
                price=149.0,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.MUSIC,
                user_id=test_user.id,
                is_active=True
            ),
            Subscription(
                id=3,
                name="Adobe",
                price=1680.0,
                cycle=SubscriptionCycle.YEARLY,
                category=SubscriptionCategory.PRODUCTIVITY,
                user_id=test_user.id,
                is_active=True
            )
        ]

    @pytest.mark.unit
    @pytest.mark.domain
    class TestBudgetUsageCalculation:
        """預算使用情況計算測試"""

        def test_calculate_budget_usage_normal(self, budget_service, sample_budget, sample_subscriptions, mock_subscription_service):
            """測試正常預算使用情況計算"""
            # 模擬總月度成本為800元
            mock_subscription_service.calculate_total_monthly_cost.return_value = 800.0
            
            result = budget_service.calculate_budget_usage(sample_budget, sample_subscriptions)
            
            assert result["total_budget"] == 1000.0
            assert result["used_amount"] == 800.0
            assert result["remaining_amount"] == 200.0
            assert result["usage_percentage"] == 80.0
            assert result["is_over_budget"] is False
            assert result["over_budget_amount"] == 0

        def test_calculate_budget_usage_over_budget(self, budget_service, sample_budget, sample_subscriptions, mock_subscription_service):
            """測試超出預算情況"""
            # 模擬總月度成本為1200元，超出預算
            mock_subscription_service.calculate_total_monthly_cost.return_value = 1200.0
            
            result = budget_service.calculate_budget_usage(sample_budget, sample_subscriptions)
            
            assert result["total_budget"] == 1000.0
            assert result["used_amount"] == 1200.0
            assert result["remaining_amount"] == -200.0
            assert result["usage_percentage"] == 120.0
            assert result["is_over_budget"] is True
            assert result["over_budget_amount"] == 200.0

        def test_calculate_budget_usage_no_budget(self, budget_service, sample_subscriptions, mock_subscription_service):
            """測試無預算情況"""
            result = budget_service.calculate_budget_usage(None, sample_subscriptions)
            
            assert result["total_budget"] == 0
            assert result["used_amount"] == 0
            assert result["remaining_amount"] == 0
            assert result["usage_percentage"] == 0
            assert result["is_over_budget"] is False
            assert result["over_budget_amount"] == 0

        def test_calculate_budget_usage_zero_budget(self, budget_service, sample_subscriptions, mock_subscription_service, test_user):
            """測試零預算情況"""
            zero_budget = Budget(
                category="entertainment",
                amount=0.0,
                period="monthly",
                monthly_limit=0.0,
                user_id=test_user.id
            )
            
            mock_subscription_service.calculate_total_monthly_cost.return_value = 500.0
            
            result = budget_service.calculate_budget_usage(zero_budget, sample_subscriptions)
            
            assert result["total_budget"] == 0.0
            assert result["used_amount"] == 500.0
            assert result["usage_percentage"] == 0  # 避免除零錯誤

    @pytest.mark.unit
    @pytest.mark.domain
    class TestCategoryBudgetAnalysis:
        """類別預算分析測試"""

        def test_calculate_category_budget_usage(self, budget_service, sample_budget, sample_subscriptions, mock_subscription_service):
            """測試類別預算使用情況計算"""
            # 模擬類別成本
            mock_subscription_service.calculate_category_costs.return_value = {
                "entertainment": 390.0,
                "music": 149.0,
                "productivity": 140.0  # 1680/12
            }
            
            result = budget_service.calculate_category_budget_usage(sample_budget, sample_subscriptions)
            
            assert result["total_budget"] == 1000.0
            assert result["total_used"] == 679.0  # 390 + 149 + 140
            
            # 檢查各類別數據
            entertainment = result["categories"]["entertainment"]
            assert entertainment["cost"] == 390.0
            assert entertainment["percentage_of_total"] == 57.4  # 390/679*100, rounded
            assert entertainment["percentage_of_budget"] == 39.0  # 390/1000*100

        def test_calculate_category_budget_usage_no_budget(self, budget_service, sample_subscriptions, mock_subscription_service):
            """測試無預算的類別分析"""
            mock_subscription_service.calculate_category_costs.return_value = {
                "entertainment": 390.0,
                "music": 149.0
            }
            
            result = budget_service.calculate_category_budget_usage(None, sample_subscriptions)
            
            assert result["total_budget"] == 0
            # 應該仍能計算類別相對比例
            entertainment = result["categories"]["entertainment"]
            assert entertainment["percentage_of_budget"] == 0  # 無預算時為0

    @pytest.mark.unit
    @pytest.mark.domain
    class TestBudgetRecommendations:
        """預算建議測試"""

        def test_get_budget_recommendations_no_budget(self, budget_service, sample_subscriptions):
            """測試無預算時的建議"""
            recommendations = budget_service.get_budget_recommendations(None, sample_subscriptions)
            
            assert len(recommendations) == 1
            assert "建議設置月度預算限制" in recommendations[0]

        def test_get_budget_recommendations_over_budget(self, budget_service, sample_budget, sample_subscriptions, mock_subscription_service):
            """測試超出預算時的建議"""
            mock_subscription_service.calculate_total_monthly_cost.return_value = 1200.0
            
            recommendations = budget_service.get_budget_recommendations(sample_budget, sample_subscriptions)
            
            over_budget_recommendation = next((r for r in recommendations if "超出預算" in r), None)
            assert over_budget_recommendation is not None
            assert "200.00" in over_budget_recommendation

        def test_get_budget_recommendations_high_usage(self, budget_service, sample_budget, sample_subscriptions, mock_subscription_service):
            """測試高使用率時的建議"""
            # 模擬95%使用率
            mock_subscription_service.calculate_total_monthly_cost.return_value = 950.0
            
            recommendations = budget_service.get_budget_recommendations(sample_budget, sample_subscriptions)
            
            high_usage_recommendation = next((r for r in recommendations if "超過90%" in r), None)
            assert high_usage_recommendation is not None

        def test_get_budget_recommendations_category_dominance(self, budget_service, sample_budget, sample_subscriptions, mock_subscription_service):
            """測試某類別佔比過高時的建議"""
            mock_subscription_service.calculate_total_monthly_cost.return_value = 800.0
            
            # 模擬娛樂類別佔60%預算
            mock_subscription_service.calculate_category_costs.return_value = {
                "entertainment": 600.0,  # 60%的預算
                "music": 200.0
            }
            
            recommendations = budget_service.get_budget_recommendations(sample_budget, sample_subscriptions)
            
            category_recommendation = next((r for r in recommendations if "entertainment" in r and "60.0%" in r), None)
            assert category_recommendation is not None

    @pytest.mark.unit
    @pytest.mark.domain
    class TestSavingsCalculation:
        """節省潛力計算測試"""

        def test_calculate_savings_potential(self, budget_service, sample_subscriptions, mock_subscription_service):
            """測試節省潛力計算"""
            # 模擬各項成本
            mock_subscription_service.calculate_yearly_cost.side_effect = [
                4680.0,  # Netflix: 390*12
                1788.0,  # Spotify: 149*12
                1680.0   # Adobe: 1680 (already yearly)
            ]
            
            mock_subscription_service.calculate_monthly_cost.side_effect = [
                390.0,   # Netflix
                149.0,   # Spotify
                140.0    # Adobe: 1680/12
            ]
            
            result = budget_service.calculate_savings_potential(sample_subscriptions)
            
            # 當前年度成本: (390+149+140)*12 = 8148
            # 潛在年度成本: (4680+1788+1680)*0.9 = 7329.2
            # 節省: 8148 - 7329.2 = 818.8
            
            assert result["current_yearly_cost"] == 8148.0
            assert result["potential_yearly_cost"] == 7329.2
            assert abs(result["potential_annual_savings"] - 818.8) < 0.1
            assert abs(result["savings_percentage"] - 10.05) < 0.1

        def test_calculate_savings_potential_no_active_subscriptions(self, budget_service, mock_subscription_service, test_user):
            """測試無活躍訂閱時的節省計算"""
            inactive_subscriptions = [
                Subscription(
                    name="Inactive Service",
                    price=100.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    is_active=False
                )
            ]
            
            result = budget_service.calculate_savings_potential(inactive_subscriptions)
            
            assert result["current_yearly_cost"] == 0
            assert result["potential_yearly_cost"] == 0
            assert result["potential_annual_savings"] == 0
            assert result["savings_percentage"] == 0

    @pytest.mark.unit
    @pytest.mark.domain
    class TestDataValidation:
        """數據驗證測試"""

        def test_validate_budget_data_valid(self, budget_service):
            """測試有效預算數據驗證"""
            result = budget_service.validate_budget_data(1000.0)
            
            assert result["is_valid"] is True
            assert len(result["errors"]) == 0

        def test_validate_budget_data_negative_amount(self, budget_service):
            """測試負數預算驗證"""
            result = budget_service.validate_budget_data(-100.0)
            
            assert result["is_valid"] is False
            assert "月度預算限制必須大於0" in result["errors"]

        def test_validate_budget_data_zero_amount(self, budget_service):
            """測試零預算驗證"""
            result = budget_service.validate_budget_data(0.0)
            
            assert result["is_valid"] is False
            assert "月度預算限制必須大於0" in result["errors"]

        def test_validate_budget_data_excessive_amount(self, budget_service):
            """測試過大預算驗證"""
            result = budget_service.validate_budget_data(2000000.0)  # 200萬
            
            assert result["is_valid"] is False
            assert "不能超過1,000,000元" in result["errors"]

        def test_validate_budget_data_edge_case_valid(self, budget_service):
            """測試邊界值有效案例"""
            result = budget_service.validate_budget_data(1000000.0)  # 正好100萬
            
            assert result["is_valid"] is True
            assert len(result["errors"]) == 0