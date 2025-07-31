import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.user import User


@pytest.mark.api
class TestSubscriptionsAPI:
    """訂閱 API 測試"""

    def test_create_subscription_success(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """測試成功創建訂閱"""
        subscription_data = {
            "name": "Netflix",
            "price": 390.0,
            "cycle": "monthly",
            "category": "entertainment",
            "start_date": "2024-01-01"
        }
        
        response = client.post("/subscriptions/", json=subscription_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == subscription_data["name"]
        assert data["price"] == subscription_data["price"]
        assert data["cycle"] == subscription_data["cycle"]
        assert data["category"] == subscription_data["category"]
        assert data["user_id"] == test_user.id
        
        # 驗證訂閱已保存到資料庫
        subscription = db_session.query(Subscription).filter(Subscription.name == subscription_data["name"]).first()
        assert subscription is not None
        assert subscription.user_id == test_user.id

    def test_create_subscription_unauthorized(self, client: TestClient):
        """測試未授權創建訂閱"""
        subscription_data = {
            "name": "Netflix",
            "price": 390.0,
            "cycle": "monthly",
            "category": "entertainment",
            "start_date": "2024-01-01"
        }
        
        response = client.post("/subscriptions/", json=subscription_data)
        
        assert response.status_code == 401

    def test_create_subscription_invalid_data(self, client: TestClient, auth_headers: dict):
        """測試無效數據創建訂閱"""
        subscription_data = {
            "name": "",  # 空名稱
            "price": -100,  # 負價格
            "cycle": "invalid",  # 無效週期
            "category": "entertainment"
        }
        
        response = client.post("/subscriptions/", json=subscription_data, headers=auth_headers)
        
        assert response.status_code == 422

    def test_get_subscriptions_success(self, client: TestClient, auth_headers: dict, multiple_test_subscriptions: list):
        """測試成功獲取訂閱列表"""
        response = client.get("/subscriptions/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(multiple_test_subscriptions)
        
        # 驗證返回的數據結構
        for subscription in data:
            assert "id" in subscription
            assert "name" in subscription
            assert "price" in subscription
            assert "cycle" in subscription
            assert "category" in subscription
            assert "user_id" in subscription

    def test_get_subscriptions_unauthorized(self, client: TestClient):
        """測試未授權獲取訂閱列表"""
        response = client.get("/subscriptions/")
        
        assert response.status_code == 401

    def test_get_subscriptions_empty(self, client: TestClient, auth_headers: dict):
        """測試獲取空訂閱列表"""
        response = client.get("/subscriptions/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_subscription_by_id_success(self, client: TestClient, auth_headers: dict, test_subscription: Subscription):
        """測試成功根據 ID 獲取訂閱"""
        response = client.get(f"/subscriptions/{test_subscription.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_subscription.id
        assert data["name"] == test_subscription.name
        assert data["price"] == test_subscription.price

    def test_get_subscription_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """測試獲取不存在的訂閱"""
        response = client.get("/subscriptions/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_get_subscription_by_id_unauthorized(self, client: TestClient, test_subscription: Subscription):
        """測試未授權獲取訂閱"""
        response = client.get(f"/subscriptions/{test_subscription.id}")
        
        assert response.status_code == 401

    def test_update_subscription_success(self, client: TestClient, auth_headers: dict, test_subscription: Subscription, db_session: Session):
        """測試成功更新訂閱"""
        update_data = {
            "name": "Updated Netflix",
            "price": 450.0,
            "cycle": "yearly",
            "category": "streaming"
        }
        
        response = client.put(f"/subscriptions/{test_subscription.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
        assert data["cycle"] == update_data["cycle"]
        assert data["category"] == update_data["category"]
        
        # 驗證資料庫中的數據已更新
        db_session.refresh(test_subscription)
        assert test_subscription.name == update_data["name"]
        assert test_subscription.price == update_data["price"]

    def test_update_subscription_not_found(self, client: TestClient, auth_headers: dict):
        """測試更新不存在的訂閱"""
        update_data = {
            "name": "Updated Netflix",
            "price": 450.0
        }
        
        response = client.put("/subscriptions/999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_subscription_unauthorized(self, client: TestClient, test_subscription: Subscription):
        """測試未授權更新訂閱"""
        update_data = {
            "name": "Updated Netflix",
            "price": 450.0
        }
        
        response = client.put(f"/subscriptions/{test_subscription.id}", json=update_data)
        
        assert response.status_code == 401

    def test_delete_subscription_success(self, client: TestClient, auth_headers: dict, test_subscription: Subscription, db_session: Session):
        """測試成功刪除訂閱"""
        subscription_id = test_subscription.id
        
        response = client.delete(f"/subscriptions/{subscription_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "成功刪除" in response.json()["message"]
        
        # 驗證訂閱已從資料庫中刪除
        deleted_subscription = db_session.query(Subscription).filter(Subscription.id == subscription_id).first()
        assert deleted_subscription is None

    def test_delete_subscription_not_found(self, client: TestClient, auth_headers: dict):
        """測試刪除不存在的訂閱"""
        response = client.delete("/subscriptions/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_delete_subscription_unauthorized(self, client: TestClient, test_subscription: Subscription):
        """測試未授權刪除訂閱"""
        response = client.delete(f"/subscriptions/{test_subscription.id}")
        
        assert response.status_code == 401

    def test_get_subscription_statistics(self, client: TestClient, auth_headers: dict, multiple_test_subscriptions: list):
        """測試獲取訂閱統計"""
        response = client.get("/subscriptions/statistics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # 驗證統計數據結構
        assert "total_count" in data
        assert "total_monthly_cost" in data
        assert "categories" in data
        assert "cycles" in data
        
        assert data["total_count"] == len(multiple_test_subscriptions)
        assert data["total_monthly_cost"] > 0

    def test_get_subscription_statistics_empty(self, client: TestClient, auth_headers: dict):
        """測試獲取空訂閱統計"""
        response = client.get("/subscriptions/statistics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_count"] == 0
        assert data["total_monthly_cost"] == 0
        assert data["categories"] == {}
        assert data["cycles"] == {}

    def test_subscription_categories_filter(self, client: TestClient, auth_headers: dict, multiple_test_subscriptions: list):
        """測試按分類篩選訂閱"""
        response = client.get("/subscriptions/?category=entertainment", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # 驗證只返回 entertainment 分類的訂閱
        for subscription in data:
            assert subscription["category"] == "entertainment"

    def test_subscription_cycle_filter(self, client: TestClient, auth_headers: dict, multiple_test_subscriptions: list):
        """測試按週期篩選訂閱"""
        response = client.get("/subscriptions/?cycle=monthly", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # 驗證只返回 monthly 週期的訂閱
        for subscription in data:
            assert subscription["cycle"] == "monthly"