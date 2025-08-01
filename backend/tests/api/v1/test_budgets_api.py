"""
預算 API v1 集成測試

測試新架構的預算 API 端點：
- POST /api/v1/budgets/ - 創建預算
- GET /api/v1/budgets/ - 獲取預算
- PUT /api/v1/budgets/{id} - 更新預算
- DELETE /api/v1/budgets/ - 刪除預算
- GET /api/v1/budgets/usage - 獲取預算使用情況
- GET /api/v1/budgets/analytics - 獲取預算分析
"""

import pytest
from fastapi import status


class TestBudgetsAPIv1:
    """預算 API v1 測試類"""

    @pytest.mark.integration
    @pytest.mark.api
    class TestCreateBudget:
        """創建預算 API 測試"""

        def test_create_budget_success(self, new_client, auth_headers):
            """測試成功創建預算"""
            payload = {
                "monthly_limit": 1000.0
            }
            
            response = new_client.post(
                "/api/v1/budgets/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "預算創建成功"
            assert data["data"]["monthly_limit"] == 1000.0

        def test_create_budget_validation_error(self, new_client, auth_headers):
            """測試創建預算時數據驗證錯誤"""
            payload = {
                "monthly_limit": -100.0  # 負數預算
            }
            
            response = new_client.post(
                "/api/v1/budgets/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            data = response.json()
            assert data["success"] is False
            assert "errors" in data["detail"]

        def test_create_budget_already_exists(self, new_client, auth_headers, test_budget):
            """測試用戶已有預算時不能重複創建"""
            payload = {
                "monthly_limit": 2000.0
            }
            
            response = new_client.post(
                "/api/v1/budgets/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            data = response.json()
            assert data["success"] is False
            assert "已經有預算設置" in data["detail"]

        def test_create_budget_missing_fields(self, new_client, auth_headers):
            """測試缺少必填字段"""
            payload = {}  # 缺少 monthly_limit
            
            response = new_client.post(
                "/api/v1/budgets/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        def test_create_budget_unauthorized(self, new_client):
            """測試未授權訪問"""
            payload = {
                "monthly_limit": 1000.0
            }
            
            response = new_client.post("/api/v1/budgets/", json=payload)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_create_budget_excessive_amount(self, new_client, auth_headers):
            """測試創建過大金額的預算"""
            payload = {
                "monthly_limit": 2000000.0  # 200萬，超過限制
            }
            
            response = new_client.post(
                "/api/v1/budgets/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            data = response.json()
            assert data["success"] is False
            assert "不能超過1,000,000元" in str(data["detail"])

    @pytest.mark.integration
    @pytest.mark.api
    class TestGetBudget:
        """獲取預算 API 測試"""

        def test_get_budget_success(self, new_client, auth_headers, test_budget):
            """測試成功獲取預算"""
            response = new_client.get("/api/v1/budgets/", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["data"]["monthly_limit"] == test_budget.monthly_limit
            assert data["data"]["user_id"] == test_budget.user_id

        def test_get_budget_not_found(self, new_client, admin_auth_headers):
            """測試獲取不存在的預算"""
            response = new_client.get("/api/v1/budgets/", headers=admin_auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["data"] is None  # 沒有預算

        def test_get_budget_unauthorized(self, new_client):
            """測試未授權訪問"""
            response = new_client.get("/api/v1/budgets/")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestUpdateBudget:
        """更新預算 API 測試"""

        def test_update_budget_success(self, new_client, auth_headers, test_budget):
            """測試成功更新預算"""
            payload = {
                "monthly_limit": 1500.0
            }
            
            response = new_client.put(
                f"/api/v1/budgets/{test_budget.id}",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "預算更新成功"
            assert data["data"]["monthly_limit"] == 1500.0

        def test_update_budget_validation_error(self, new_client, auth_headers, test_budget):
            """測試更新預算時數據驗證錯誤"""
            payload = {
                "monthly_limit": 0.0  # 無效金額
            }
            
            response = new_client.put(
                f"/api/v1/budgets/{test_budget.id}",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            data = response.json()
            assert data["success"] is False

        def test_update_budget_not_found(self, new_client, admin_auth_headers):
            """測試更新不存在的預算"""
            payload = {
                "monthly_limit": 1500.0
            }
            
            response = new_client.put(
                "/api/v1/budgets/99999",
                json=payload,
                headers=admin_auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

        def test_update_budget_permission_denied(self, new_client, admin_auth_headers, test_budget):
            """測試更新其他用戶的預算"""
            payload = {
                "monthly_limit": 1500.0
            }
            
            response = new_client.put(
                f"/api/v1/budgets/{test_budget.id}",
                json=payload,
                headers=admin_auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND  # 因為找不到屬於該用戶的預算

        def test_update_budget_unauthorized(self, new_client, test_budget):
            """測試未授權更新"""
            payload = {
                "monthly_limit": 1500.0
            }
            
            response = new_client.put(f"/api/v1/budgets/{test_budget.id}", json=payload)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestDeleteBudget:
        """刪除預算 API 測試"""

        def test_delete_budget_success(self, new_client, auth_headers, test_budget):
            """測試成功刪除預算"""
            response = new_client.delete("/api/v1/budgets/", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "預算刪除成功"
            
            # 驗證已被刪除
            get_response = new_client.get("/api/v1/budgets/", headers=auth_headers)
            assert get_response.json()["data"] is None

        def test_delete_budget_not_found(self, new_client, admin_auth_headers):
            """測試刪除不存在的預算"""
            response = new_client.delete("/api/v1/budgets/", headers=admin_auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

        def test_delete_budget_unauthorized(self, new_client):
            """測試未授權刪除"""
            response = new_client.delete("/api/v1/budgets/")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestBudgetUsage:
        """預算使用情況 API 測試"""

        def test_get_budget_usage_with_budget(self, new_client, auth_headers, test_budget, multiple_test_subscriptions):
            """測試有預算時獲取使用情況"""
            response = new_client.get("/api/v1/budgets/usage", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            
            usage_data = data["data"]
            assert "budget" in usage_data
            assert "usage_info" in usage_data
            assert "category_usage" in usage_data
            assert "recommendations" in usage_data
            assert "savings_potential" in usage_data
            
            # 驗證預算信息
            assert usage_data["budget"]["monthly_limit"] == test_budget.monthly_limit
            
            # 驗證使用情況信息
            usage_info = usage_data["usage_info"]
            assert "total_budget" in usage_info
            assert "used_amount" in usage_info
            assert "remaining_amount" in usage_info
            assert "usage_percentage" in usage_info
            assert "is_over_budget" in usage_info

        def test_get_budget_usage_without_budget(self, new_client, admin_auth_headers):
            """測試無預算時獲取使用情況"""
            response = new_client.get("/api/v1/budgets/usage", headers=admin_auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            
            usage_data = data["data"]
            assert usage_data["budget"] is None
            assert "建議設置月度預算限制" in str(usage_data["recommendations"])

        def test_get_budget_usage_unauthorized(self, new_client):
            """測試未授權訪問使用情況"""
            response = new_client.get("/api/v1/budgets/usage")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_get_budget_usage_over_budget_scenario(self, new_client, auth_headers, db_session, test_user):
            """測試超出預算的場景"""
            # 創建一個低預算
            from app.models.budget import Budget
            low_budget = Budget(
                user_id=test_user.id,
                monthly_limit=100.0  # 很低的預算
            )
            db_session.add(low_budget)
            db_session.commit()
            
            # 創建一些高價訂閱
            from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency
            expensive_subscription = Subscription(
                name="Expensive Service",
                price=500.0,
                original_price=500.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                is_active=True
            )
            db_session.add(expensive_subscription)
            db_session.commit()
            
            response = new_client.get("/api/v1/budgets/usage", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            usage_info = data["data"]["usage_info"]
            
            # 應該顯示超出預算
            assert usage_info["is_over_budget"] is True
            assert usage_info["over_budget_amount"] > 0
            assert usage_info["usage_percentage"] > 100

    @pytest.mark.integration
    @pytest.mark.api
    class TestBudgetAnalytics:
        """預算分析 API 測試"""

        def test_get_budget_analytics(self, new_client, auth_headers, test_budget, multiple_test_subscriptions):
            """測試獲取預算分析"""
            response = new_client.get("/api/v1/budgets/analytics", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            
            analytics = data["data"]
            assert "current_month" in analytics
            assert "previous_month_comparison" in analytics
            assert "trend_analysis" in analytics
            
            # 驗證趨勢分析
            trend = analytics["trend_analysis"]
            assert "trend" in trend
            assert "change_percentage" in trend
            assert "period" in trend
            
            # 目前的實現應該返回穩定趨勢
            assert trend["trend"] == "stable"

        def test_get_budget_analytics_without_budget(self, new_client, admin_auth_headers):
            """測試無預算時的分析"""
            response = new_client.get("/api/v1/budgets/analytics", headers=admin_auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            
            analytics = data["data"]
            assert analytics["current_month"]["budget"] is None

        def test_get_budget_analytics_unauthorized(self, new_client):
            """測試未授權訪問分析"""
            response = new_client.get("/api/v1/budgets/analytics")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestResponseFormat:
        """響應格式測試"""

        def test_success_response_format(self, new_client, auth_headers, test_budget):
            """測試成功響應的統一格式"""
            response = new_client.get("/api/v1/budgets/", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            # 驗證統一響應格式
            assert "success" in data
            assert "message" in data
            assert "data" in data
            assert "timestamp" in data
            
            assert data["success"] is True
            assert isinstance(data["message"], str)

        def test_error_response_format(self, new_client, admin_auth_headers):
            """測試錯誤響應的統一格式"""
            response = new_client.delete("/api/v1/budgets/", headers=admin_auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            
            data = response.json()
            # 驗證統一錯誤響應格式
            assert "success" in data
            assert "message" in data
            assert "timestamp" in data
            
            assert data["success"] is False
            assert isinstance(data["message"], str)

        def test_validation_error_response_format(self, new_client, auth_headers):
            """測試驗證錯誤響應格式"""
            payload = {
                "monthly_limit": -100.0  # 觸發驗證錯誤
            }
            
            response = new_client.post(
                "/api/v1/budgets/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            data = response.json()
            assert data["success"] is False
            assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.api
    class TestComplexScenarios:
        """複雜場景測試"""

        def test_budget_lifecycle(self, new_client, auth_headers):
            """測試預算的完整生命週期"""
            # 1. 創建預算
            create_payload = {"monthly_limit": 1000.0}
            create_response = new_client.post(
                "/api/v1/budgets/",
                json=create_payload,
                headers=auth_headers
            )
            assert create_response.status_code == status.HTTP_201_CREATED
            budget_id = create_response.json()["data"]["id"]
            
            # 2. 獲取預算
            get_response = new_client.get("/api/v1/budgets/", headers=auth_headers)
            assert get_response.status_code == status.HTTP_200_OK
            assert get_response.json()["data"]["monthly_limit"] == 1000.0
            
            # 3. 更新預算
            update_payload = {"monthly_limit": 1500.0}
            update_response = new_client.put(
                f"/api/v1/budgets/{budget_id}",
                json=update_payload,
                headers=auth_headers
            )
            assert update_response.status_code == status.HTTP_200_OK
            assert update_response.json()["data"]["monthly_limit"] == 1500.0
            
            # 4. 獲取使用情況
            usage_response = new_client.get("/api/v1/budgets/usage", headers=auth_headers)
            assert usage_response.status_code == status.HTTP_200_OK
            assert usage_response.json()["data"]["budget"]["monthly_limit"] == 1500.0
            
            # 5. 獲取分析
            analytics_response = new_client.get("/api/v1/budgets/analytics", headers=auth_headers)
            assert analytics_response.status_code == status.HTTP_200_OK
            
            # 6. 刪除預算
            delete_response = new_client.delete("/api/v1/budgets/", headers=auth_headers)
            assert delete_response.status_code == status.HTTP_200_OK
            
            # 7. 驗證已刪除
            final_get_response = new_client.get("/api/v1/budgets/", headers=auth_headers)
            assert final_get_response.json()["data"] is None

        def test_budget_with_subscriptions_interaction(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試預算與訂閱的交互"""
            # 創建預算
            create_payload = {"monthly_limit": 500.0}  # 相對較低的預算
            create_response = new_client.post(
                "/api/v1/budgets/",
                json=create_payload,
                headers=auth_headers
            )
            assert create_response.status_code == status.HTTP_201_CREATED
            
            # 獲取使用情況，應該反映訂閱對預算的影響
            usage_response = new_client.get("/api/v1/budgets/usage", headers=auth_headers)
            assert usage_response.status_code == status.HTTP_200_OK
            
            usage_data = usage_response.json()["data"]
            
            # 應該有使用金額
            assert usage_data["usage_info"]["used_amount"] > 0
            
            # 應該有類別分解
            assert len(usage_data["category_usage"]["categories"]) > 0
            
            # 應該有建議
            assert len(usage_data["recommendations"]) > 0
            
            # 應該有節省潛力分析
            assert usage_data["savings_potential"]["current_yearly_cost"] > 0