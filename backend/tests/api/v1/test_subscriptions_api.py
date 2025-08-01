"""
訂閱 API v1 集成測試

測試新架構的 API 端點：
- POST /api/v1/subscriptions/ - 創建訂閱
- GET /api/v1/subscriptions/ - 獲取訂閱列表
- GET /api/v1/subscriptions/{id} - 獲取單個訂閱
- PUT /api/v1/subscriptions/{id} - 更新訂閱
- DELETE /api/v1/subscriptions/{id} - 刪除訂閱
- GET /api/v1/subscriptions/summary - 獲取訂閱摘要
- POST /api/v1/subscriptions/bulk-operation - 批量操作
"""

import pytest
import json
from datetime import datetime
from fastapi import status

from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency


class TestSubscriptionsAPIv1:
    """訂閱 API v1 測試類"""

    @pytest.mark.integration
    @pytest.mark.api
    class TestCreateSubscription:
        """創建訂閱 API 測試"""

        def test_create_subscription_success(self, new_client, auth_headers):
            """測試成功創建訂閱"""
            payload = {
                "name": "Netflix",
                "original_price": 390.0,
                "currency": "TWD",
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01T00:00:00"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "訂閱創建成功"
            assert data["data"]["name"] == "Netflix"
            assert data["data"]["price"] == 390.0
            assert data["data"]["monthly_cost"] == 390.0
            assert "next_billing_date" in data["data"]

        def test_create_subscription_validation_error(self, new_client, auth_headers):
            """測試創建訂閱時數據驗證錯誤"""
            payload = {
                "name": "",  # 空名稱
                "original_price": -100.0,  # 負價格
                "currency": "INVALID",  # 無效貨幣
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01T00:00:00"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            data = response.json()
            assert data["success"] is False
            assert "errors" in data["detail"]

        def test_create_subscription_missing_fields(self, new_client, auth_headers):
            """測試缺少必填字段"""
            payload = {
                "name": "Netflix"
                # 缺少其他必填字段
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        def test_create_subscription_unauthorized(self, new_client):
            """測試未授權訪問"""
            payload = {
                "name": "Netflix",
                "original_price": 390.0,
                "currency": "TWD",
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01T00:00:00"
            }
            
            response = new_client.post("/api/v1/subscriptions/", json=payload)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_create_subscription_foreign_currency(self, new_client, auth_headers):
            """測試創建外幣訂閱"""
            payload = {
                "name": "Adobe Creative Cloud",
                "original_price": 20.99,
                "currency": "USD",
                "cycle": "monthly",
                "category": "productivity",
                "start_date": "2024-01-01T00:00:00"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/",
                json=payload,
                headers=auth_headers
            )
            
            # 假設匯率服務正常工作
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
            
            if response.status_code == status.HTTP_201_CREATED:
                data = response.json()
                assert data["data"]["original_price"] == 20.99
                assert data["data"]["currency"] == "USD"
                assert data["data"]["price"] > 20.99  # 台幣價格應該更高

    @pytest.mark.integration
    @pytest.mark.api
    class TestGetSubscriptions:
        """獲取訂閱列表 API 測試"""

        def test_get_subscriptions_success(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試成功獲取訂閱列表"""
            response = new_client.get("/api/v1/subscriptions/", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 3  # 所有訂閱（包括非活躍的）

        def test_get_subscriptions_active_only(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試只獲取活躍訂閱"""
            response = new_client.get(
                "/api/v1/subscriptions/?include_inactive=false",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            # 過濾掉非活躍訂閱
            active_count = sum(1 for sub in data["data"] if sub.get("is_active", True))
            assert active_count >= 2

        def test_get_subscriptions_filter_by_category(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試按類別過濾訂閱"""
            response = new_client.get(
                "/api/v1/subscriptions/?category=entertainment",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            # 應該只返回娛樂類別的訂閱
            for subscription in data["data"]:
                assert subscription["category"] == "entertainment"

        def test_get_subscriptions_empty_list(self, new_client, admin_auth_headers):
            """測試獲取空訂閱列表"""
            response = new_client.get("/api/v1/subscriptions/", headers=admin_auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 0

        def test_get_subscriptions_unauthorized(self, new_client):
            """測試未授權訪問"""
            response = new_client.get("/api/v1/subscriptions/")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestGetSingleSubscription:
        """獲取單個訂閱 API 測試"""

        def test_get_subscription_success(self, new_client, auth_headers, test_subscription):
            """測試成功獲取單個訂閱"""
            response = new_client.get(
                f"/api/v1/subscriptions/{test_subscription.id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["data"]["id"] == test_subscription.id
            assert data["data"]["name"] == test_subscription.name
            assert "monthly_cost" in data["data"]
            assert "yearly_cost" in data["data"]
            assert "next_billing_date" in data["data"]

        def test_get_subscription_not_found(self, new_client, auth_headers):
            """測試獲取不存在的訂閱"""
            response = new_client.get("/api/v1/subscriptions/99999", headers=auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            
            data = response.json()
            assert data["success"] is False
            assert "訂閱不存在" in data["message"]

        def test_get_subscription_other_user(self, new_client, admin_auth_headers, test_subscription):
            """測試獲取其他用戶的訂閱"""
            response = new_client.get(
                f"/api/v1/subscriptions/{test_subscription.id}",
                headers=admin_auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

        def test_get_subscription_unauthorized(self, new_client, test_subscription):
            """測試未授權訪問"""
            response = new_client.get(f"/api/v1/subscriptions/{test_subscription.id}")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestUpdateSubscription:
        """更新訂閱 API 測試"""

        def test_update_subscription_success(self, new_client, auth_headers, test_subscription):
            """測試成功更新訂閱"""
            payload = {
                "name": "Netflix Premium",
                "original_price": 490.0
            }
            
            response = new_client.put(
                f"/api/v1/subscriptions/{test_subscription.id}",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "訂閱更新成功"
            assert data["data"]["name"] == "Netflix Premium"
            assert data["data"]["price"] == 490.0

        def test_update_subscription_partial(self, new_client, auth_headers, test_subscription):
            """測試部分更新訂閱"""
            payload = {
                "is_active": False
            }
            
            response = new_client.put(
                f"/api/v1/subscriptions/{test_subscription.id}",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["data"]["is_active"] is False

        def test_update_subscription_not_found(self, new_client, auth_headers):
            """測試更新不存在的訂閱"""
            payload = {"name": "New Name"}
            
            response = new_client.put(
                "/api/v1/subscriptions/99999",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

        def test_update_subscription_other_user(self, new_client, admin_auth_headers, test_subscription):
            """測試更新其他用戶的訂閱"""
            payload = {"name": "Hacked Name"}
            
            response = new_client.put(
                f"/api/v1/subscriptions/{test_subscription.id}",
                json=payload,
                headers=admin_auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

        def test_update_subscription_currency_recalculation(self, new_client, auth_headers, test_subscription):
            """測試更新貨幣時重新計算價格"""
            payload = {
                "original_price": 10.0,
                "currency": "USD"
            }
            
            response = new_client.put(
                f"/api/v1/subscriptions/{test_subscription.id}",
                json=payload,
                headers=auth_headers
            )
            
            # 根據匯率服務是否可用來判斷
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    @pytest.mark.integration
    @pytest.mark.api
    class TestDeleteSubscription:
        """刪除訂閱 API 測試"""

        def test_delete_subscription_success(self, new_client, auth_headers, test_subscription):
            """測試成功刪除訂閱"""
            response = new_client.delete(
                f"/api/v1/subscriptions/{test_subscription.id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "訂閱刪除成功"
            
            # 驗證已被刪除
            get_response = new_client.get(
                f"/api/v1/subscriptions/{test_subscription.id}",
                headers=auth_headers
            )
            assert get_response.status_code == status.HTTP_404_NOT_FOUND

        def test_delete_subscription_not_found(self, new_client, auth_headers):
            """測試刪除不存在的訂閱"""
            response = new_client.delete("/api/v1/subscriptions/99999", headers=auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

        def test_delete_subscription_other_user(self, new_client, admin_auth_headers, test_subscription):
            """測試刪除其他用戶的訂閱"""
            response = new_client.delete(
                f"/api/v1/subscriptions/{test_subscription.id}",
                headers=admin_auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

        def test_delete_subscription_unauthorized(self, new_client, test_subscription):
            """測試未授權刪除"""
            response = new_client.delete(f"/api/v1/subscriptions/{test_subscription.id}")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestSubscriptionSummary:
        """訂閱摘要 API 測試"""

        def test_get_subscription_summary(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試獲取訂閱摘要"""
            response = new_client.get("/api/v1/subscriptions/summary", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            
            summary = data["data"]
            assert "total_subscriptions" in summary
            assert "active_subscriptions" in summary
            assert "total_monthly_cost" in summary
            assert "total_yearly_cost" in summary
            assert "categories" in summary
            assert "upcoming_renewals" in summary
            
            assert summary["total_subscriptions"] >= 3
            assert summary["active_subscriptions"] >= 2
            assert summary["total_monthly_cost"] > 0
            assert summary["total_yearly_cost"] > 0

        def test_get_subscription_summary_empty(self, new_client, admin_auth_headers):
            """測試無訂閱用戶的摘要"""
            response = new_client.get("/api/v1/subscriptions/summary", headers=admin_auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            
            summary = data["data"]
            assert summary["total_subscriptions"] == 0
            assert summary["active_subscriptions"] == 0
            assert summary["total_monthly_cost"] == 0
            assert summary["total_yearly_cost"] == 0

        def test_get_subscription_summary_unauthorized(self, new_client):
            """測試未授權訪問摘要"""
            response = new_client.get("/api/v1/subscriptions/summary")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestBulkOperations:
        """批量操作 API 測試"""

        def test_bulk_activate_subscriptions(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試批量啟用訂閱"""
            subscription_ids = [sub.id for sub in multiple_test_subscriptions[:2]]
            
            payload = {
                "subscription_ids": subscription_ids,
                "operation": "activate"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/bulk-operation",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "批量操作完成"

        def test_bulk_deactivate_subscriptions(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試批量停用訂閱"""
            subscription_ids = [sub.id for sub in multiple_test_subscriptions[:2]]
            
            payload = {
                "subscription_ids": subscription_ids,
                "operation": "deactivate"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/bulk-operation",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True

        def test_bulk_delete_subscriptions(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試批量刪除訂閱"""
            subscription_ids = [sub.id for sub in multiple_test_subscriptions[:1]]  # 只刪除一個
            
            payload = {
                "subscription_ids": subscription_ids,
                "operation": "delete"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/bulk-operation",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            # 驗證被刪除
            get_response = new_client.get(
                f"/api/v1/subscriptions/{subscription_ids[0]}",
                headers=auth_headers
            )
            assert get_response.status_code == status.HTTP_404_NOT_FOUND

        def test_bulk_operation_invalid_operation(self, new_client, auth_headers, multiple_test_subscriptions):
            """測試無效的批量操作"""
            subscription_ids = [sub.id for sub in multiple_test_subscriptions[:2]]
            
            payload = {
                "subscription_ids": subscription_ids,
                "operation": "invalid_operation"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/bulk-operation",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        def test_bulk_operation_empty_ids(self, new_client, auth_headers):
            """測試空的訂閱 ID 列表"""
            payload = {
                "subscription_ids": [],
                "operation": "activate"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/bulk-operation",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK  # 空操作仍然成功

        def test_bulk_operation_unauthorized(self, new_client):
            """測試未授權的批量操作"""
            payload = {
                "subscription_ids": [1, 2],
                "operation": "delete"
            }
            
            response = new_client.post("/api/v1/subscriptions/bulk-operation", json=payload)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.api
    class TestResponseFormat:
        """響應格式測試"""

        def test_success_response_format(self, new_client, auth_headers, test_subscription):
            """測試成功響應的統一格式"""
            response = new_client.get(
                f"/api/v1/subscriptions/{test_subscription.id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            # 驗證統一響應格式
            assert "success" in data
            assert "message" in data
            assert "data" in data
            assert "timestamp" in data
            
            assert data["success"] is True
            assert isinstance(data["message"], str)
            assert data["data"] is not None

        def test_error_response_format(self, new_client, auth_headers):
            """測試錯誤響應的統一格式"""
            response = new_client.get("/api/v1/subscriptions/99999", headers=auth_headers)
            
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
                "name": "",  # 空名稱觸發驗證錯誤
                "original_price": 390.0,
                "currency": "TWD",
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01T00:00:00"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            data = response.json()
            assert data["success"] is False
            assert "detail" in data
            assert "errors" in data["detail"]