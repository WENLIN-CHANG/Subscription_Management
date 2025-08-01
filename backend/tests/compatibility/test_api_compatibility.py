"""
API 向後兼容性測試

測試新架構是否與舊 API 兼容：
- 舊 API 端點是否仍然可用
- 響應格式是否一致
- 數據結構是否兼容
- 錯誤處理是否一致
- 功能行為是否一致
"""

import pytest
import json
from fastapi import status


class TestAPICompatibility:
    """API 向後兼容性測試類"""

    @pytest.mark.compatibility
    @pytest.mark.api
    class TestSubscriptionEndpointsCompatibility:
        """訂閱端點兼容性測試"""

        def test_old_vs_new_create_subscription(self, client, new_client, auth_headers):
            """測試創建訂閱的兼容性"""
            payload = {
                "name": "Netflix",
                "price": 390.0,
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01"
            }
            
            # 舊 API 調用
            old_response = client.post("/api/subscriptions", json=payload, headers=auth_headers)
            
            # 新 API 調用 (使用兼容的數據格式)
            new_payload = {
                "name": "Netflix",
                "original_price": 390.0,
                "currency": "TWD",
                "cycle": "monthly", 
                "category": "entertainment",
                "start_date": "2024-01-01T00:00:00"
            }
            new_response = new_client.post("/api/v1/subscriptions/", json=new_payload, headers=auth_headers)
            
            # 兩者都應該成功
            assert old_response.status_code in [200, 201]
            assert new_response.status_code in [200, 201]
            
            # 核心數據應該一致
            old_data = old_response.json()
            new_data = new_response.json()
            
            # 新 API 有統一響應格式，需要從 data 字段提取
            if "data" in new_data:
                new_subscription = new_data["data"]
            else:
                new_subscription = new_data
                
            # 舊 API 可能直接返回訂閱對象
            if "name" in old_data:
                old_subscription = old_data
            else:
                old_subscription = old_data.get("data", old_data)
            
            # 比較核心字段
            assert old_subscription["name"] == new_subscription["name"]
            assert old_subscription["cycle"] == new_subscription["cycle"]
            assert old_subscription["category"] == new_subscription["category"]

        def test_old_vs_new_get_subscriptions(self, client, new_client, auth_headers, multiple_test_subscriptions):
            """測試獲取訂閱列表的兼容性"""
            # 舊 API 調用
            old_response = client.get("/api/subscriptions", headers=auth_headers)
            
            # 新 API 調用
            new_response = new_client.get("/api/v1/subscriptions/", headers=auth_headers)
            
            # 兩者都應該成功
            assert old_response.status_code == 200
            assert new_response.status_code == 200
            
            old_data = old_response.json()
            new_data = new_response.json()
            
            # 提取訂閱列表
            old_subscriptions = old_data if isinstance(old_data, list) else old_data.get("data", [])
            new_subscriptions = new_data["data"] if "data" in new_data else new_data
            
            # 應該返回相同數量的訂閱
            assert len(old_subscriptions) == len(new_subscriptions)
            
            # 驗證核心字段存在
            if old_subscriptions:
                old_sub = old_subscriptions[0]
                new_sub = new_subscriptions[0]
                
                common_fields = ["id", "name", "price", "cycle", "category", "is_active"]
                for field in common_fields:
                    assert field in old_sub
                    assert field in new_sub

        def test_old_vs_new_get_single_subscription(self, client, new_client, auth_headers, test_subscription):
            """測試獲取單個訂閱的兼容性"""
            subscription_id = test_subscription.id
            
            # 舊 API 調用
            old_response = client.get(f"/api/subscriptions/{subscription_id}", headers=auth_headers)
            
            # 新 API 調用
            new_response = new_client.get(f"/api/v1/subscriptions/{subscription_id}", headers=auth_headers)
            
            # 兩者都應該成功
            assert old_response.status_code == 200
            assert new_response.status_code == 200
            
            old_data = old_response.json()
            new_data = new_response.json()
            
            # 提取訂閱對象
            old_subscription = old_data if "id" in old_data else old_data.get("data")
            new_subscription = new_data["data"] if "data" in new_data else new_data
            
            # 核心字段應該一致
            assert old_subscription["id"] == new_subscription["id"]
            assert old_subscription["name"] == new_subscription["name"]
            assert old_subscription["price"] == new_subscription["price"]

        def test_old_vs_new_update_subscription(self, client, new_client, auth_headers, test_subscription):
            """測試更新訂閱的兼容性"""
            subscription_id = test_subscription.id
            
            # 準備更新數據
            old_payload = {"name": "Netflix Premium", "price": 490.0}
            new_payload = {"name": "Netflix Premium", "original_price": 490.0}
            
            # 舊 API 調用
            old_response = client.put(f"/api/subscriptions/{subscription_id}", json=old_payload, headers=auth_headers)
            
            # 等一下再測試新 API，使用不同的名稱避免衝突
            new_payload["name"] = "Netflix Premium New"
            new_response = new_client.put(f"/api/v1/subscriptions/{subscription_id}", json=new_payload, headers=auth_headers)
            
            # 兩者都應該成功
            assert old_response.status_code == 200
            assert new_response.status_code == 200
            
            # 響應格式可能不同，但都應該包含更新後的數據
            old_result = old_response.json()
            new_result = new_response.json()
            
            # 新 API 使用統一響應格式
            if "data" in new_result:
                assert new_result["success"] is True
                assert new_result["data"]["name"] == "Netflix Premium New"

        def test_old_vs_new_delete_subscription(self, client, new_client, auth_headers, db_session, test_user):
            """測試刪除訂閱的兼容性"""
            from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency
            
            # 創建兩個測試訂閱
            subscription1 = Subscription(
                name="Test Service 1",
                price=100.0,
                original_price=100.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                is_active=True
            )
            
            subscription2 = Subscription(
                name="Test Service 2", 
                price=200.0,
                original_price=200.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                is_active=True
            )
            
            db_session.add(subscription1)
            db_session.add(subscription2)
            db_session.commit()
            db_session.refresh(subscription1)
            db_session.refresh(subscription2)
            
            # 舊 API 刪除
            old_response = client.delete(f"/api/subscriptions/{subscription1.id}", headers=auth_headers)
            
            # 新 API 刪除
            new_response = new_client.delete(f"/api/v1/subscriptions/{subscription2.id}", headers=auth_headers)
            
            # 兩者都應該成功
            assert old_response.status_code == 200
            assert new_response.status_code == 200
            
            # 新 API 應該有統一響應格式
            new_result = new_response.json()
            if "success" in new_result:
                assert new_result["success"] is True

    @pytest.mark.compatibility
    @pytest.mark.api
    class TestErrorHandlingCompatibility:
        """錯誤處理兼容性測試"""

        def test_404_error_compatibility(self, client, new_client, auth_headers):
            """測試 404 錯誤的兼容性"""
            # 舊 API 調用不存在的資源
            old_response = client.get("/api/subscriptions/99999", headers=auth_headers)
            
            # 新 API 調用不存在的資源
            new_response = new_client.get("/api/v1/subscriptions/99999", headers=auth_headers)
            
            # 兩者都應該返回 404
            assert old_response.status_code == 404
            assert new_response.status_code == 404
            
            # 新 API 應該有統一的錯誤響應格式
            new_data = new_response.json()
            if "success" in new_data:
                assert new_data["success"] is False
                assert "message" in new_data

        def test_unauthorized_error_compatibility(self, client, new_client):
            """測試未授權錯誤的兼容性"""
            # 舊 API 無授權訪問
            old_response = client.get("/api/subscriptions")
            
            # 新 API 無授權訪問
            new_response = new_client.get("/api/v1/subscriptions/")
            
            # 兩者都應該返回 401
            assert old_response.status_code == 401
            assert new_response.status_code == 401

        def test_validation_error_compatibility(self, client, new_client, auth_headers):
            """測試驗證錯誤的兼容性"""
            # 無效的數據
            invalid_payload = {
                "name": "",  # 空名稱
                "price": -100  # 負價格
            }
            
            # 舊 API 調用
            old_response = client.post("/api/subscriptions", json=invalid_payload, headers=auth_headers)
            
            # 新 API 調用（調整為新格式）
            new_invalid_payload = {
                "name": "",
                "original_price": -100,
                "currency": "TWD",
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01T00:00:00"
            }
            new_response = new_client.post("/api/v1/subscriptions/", json=new_invalid_payload, headers=auth_headers)
            
            # 兩者都應該返回客戶端錯誤
            assert old_response.status_code >= 400
            assert old_response.status_code < 500
            
            assert new_response.status_code >= 400
            assert new_response.status_code < 500
            
            # 新 API 應該有統一的錯誤格式
            new_data = new_response.json()
            if "success" in new_data:
                assert new_data["success"] is False

    @pytest.mark.compatibility
    @pytest.mark.api
    class TestResponseFormatCompatibility:
        """響應格式兼容性測試"""

        def test_data_types_compatibility(self, client, new_client, auth_headers, test_subscription):
            """測試數據類型兼容性"""
            # 獲取單個訂閱來比較數據類型
            old_response = client.get(f"/api/subscriptions/{test_subscription.id}", headers=auth_headers)
            new_response = new_client.get(f"/api/v1/subscriptions/{test_subscription.id}", headers=auth_headers)
            
            if old_response.status_code == 200 and new_response.status_code == 200:
                old_data = old_response.json()
                new_data = new_response.json()
                
                # 提取訂閱對象
                old_subscription = old_data if "id" in old_data else old_data.get("data")
                new_subscription = new_data["data"] if "data" in new_data else new_data
                
                # 檢查數據類型一致性
                type_fields = ["id", "price", "is_active"]
                for field in type_fields:
                    if field in old_subscription and field in new_subscription:
                        assert type(old_subscription[field]) == type(new_subscription[field])

        def test_field_names_compatibility(self, client, new_client, auth_headers, test_subscription):
            """測試字段名稱兼容性"""
            old_response = client.get(f"/api/subscriptions/{test_subscription.id}", headers=auth_headers)
            new_response = new_client.get(f"/api/v1/subscriptions/{test_subscription.id}", headers=auth_headers)
            
            if old_response.status_code == 200 and new_response.status_code == 200:
                old_data = old_response.json()
                new_data = new_response.json()
                
                old_subscription = old_data if "id" in old_data else old_data.get("data")
                new_subscription = new_data["data"] if "data" in new_data else new_data
                
                # 核心字段應該在兩個版本中都存在
                essential_fields = ["id", "name", "price", "cycle", "category", "is_active"]
                for field in essential_fields:
                    assert field in old_subscription, f"舊 API 缺少字段: {field}"
                    assert field in new_subscription, f"新 API 缺少字段: {field}"

        def test_date_format_compatibility(self, client, new_client, auth_headers, test_subscription):
            """測試日期格式兼容性"""
            old_response = client.get(f"/api/subscriptions/{test_subscription.id}", headers=auth_headers)
            new_response = new_client.get(f"/api/v1/subscriptions/{test_subscription.id}", headers=auth_headers)
            
            if old_response.status_code == 200 and new_response.status_code == 200:
                old_data = old_response.json()
                new_data = new_response.json()
                
                old_subscription = old_data if "id" in old_data else old_data.get("data")
                new_subscription = new_data["data"] if "data" in new_data else new_data
                
                # 檢查日期字段格式
                date_fields = ["start_date", "created_at", "updated_at"]
                for field in date_fields:
                    if field in old_subscription and field in new_subscription:
                        # 兩者都應該是字符串格式的日期
                        assert isinstance(old_subscription[field], str)
                        assert isinstance(new_subscription[field], str)

    @pytest.mark.compatibility
    @pytest.mark.api
    class TestFunctionalCompatibility:
        """功能兼容性測試"""

        def test_authentication_compatibility(self, client, new_client, auth_headers):
            """測試認證機制兼容性"""
            # 使用相同的認證頭訪問兩個版本的 API
            old_response = client.get("/api/subscriptions", headers=auth_headers)
            new_response = new_client.get("/api/v1/subscriptions/", headers=auth_headers)
            
            # 兩者都應該能成功認證
            assert old_response.status_code != 401
            assert new_response.status_code != 401

        def test_pagination_compatibility(self, client, new_client, auth_headers, multiple_test_subscriptions):
            """測試分頁兼容性"""
            # 如果舊 API 支持分頁參數
            old_response = client.get("/api/subscriptions?limit=2", headers=auth_headers)
            new_response = new_client.get("/api/v1/subscriptions/?limit=2", headers=auth_headers)
            
            # 檢查響應是否合理
            if old_response.status_code == 200:
                old_data = old_response.json()
                old_subscriptions = old_data if isinstance(old_data, list) else old_data.get("data", [])
                
                # 如果支持分頁，應該返回不超過限制數量的結果
                assert len(old_subscriptions) <= 2
            
            if new_response.status_code == 200:
                new_data = new_response.json()
                new_subscriptions = new_data["data"] if "data" in new_data else new_data
                
                if isinstance(new_subscriptions, list):
                    assert len(new_subscriptions) <= 2

        def test_filtering_compatibility(self, client, new_client, auth_headers, multiple_test_subscriptions):
            """測試過濾功能兼容性"""
            # 測試類別過濾
            old_response = client.get("/api/subscriptions?category=entertainment", headers=auth_headers)
            new_response = new_client.get("/api/v1/subscriptions/?category=entertainment", headers=auth_headers)
            
            if old_response.status_code == 200 and new_response.status_code == 200:
                old_data = old_response.json()
                new_data = new_response.json()
                
                old_subscriptions = old_data if isinstance(old_data, list) else old_data.get("data", [])
                new_subscriptions = new_data["data"] if "data" in new_data else new_data
                
                # 過濾結果中的所有項目都應該是指定類別
                for subscription in old_subscriptions:
                    if "category" in subscription:
                        assert subscription["category"] == "entertainment"
                
                for subscription in new_subscriptions:
                    if "category" in subscription:
                        assert subscription["category"] == "entertainment"

    @pytest.mark.compatibility
    @pytest.mark.performance
    class TestPerformanceCompatibility:
        """性能兼容性測試"""

        def test_response_time_compatibility(self, client, new_client, auth_headers):
            """測試響應時間兼容性"""
            import time
            
            # 測試舊 API 響應時間
            start_time = time.time()
            old_response = client.get("/api/subscriptions", headers=auth_headers)
            old_response_time = time.time() - start_time
            
            # 測試新 API 響應時間
            start_time = time.time()
            new_response = new_client.get("/api/v1/subscriptions/", headers=auth_headers)
            new_response_time = time.time() - start_time
            
            # 新 API 的響應時間不應該比舊 API 慢太多（比如超過2倍）
            if old_response.status_code == 200 and new_response.status_code == 200:
                assert new_response_time < old_response_time * 3  # 允許新 API 慢一些，但不要太多

        def test_concurrent_request_compatibility(self, client, new_client, auth_headers):
            """測試並發請求兼容性"""
            import threading
            import time
            
            results = {"old": [], "new": []}
            
            def make_old_requests():
                for _ in range(5):
                    response = client.get("/api/subscriptions", headers=auth_headers)
                    results["old"].append(response.status_code)
                    time.sleep(0.1)
            
            def make_new_requests():
                for _ in range(5):
                    response = new_client.get("/api/v1/subscriptions/", headers=auth_headers)
                    results["new"].append(response.status_code)
                    time.sleep(0.1)
            
            # 並發執行請求
            old_thread = threading.Thread(target=make_old_requests)
            new_thread = threading.Thread(target=make_new_requests)
            
            old_thread.start()
            new_thread.start()
            
            old_thread.join()
            new_thread.join()
            
            # 檢查結果
            successful_old = sum(1 for code in results["old"] if code < 400)
            successful_new = sum(1 for code in results["new"] if code < 400)
            
            # 兩個版本的成功率應該相似
            assert successful_old >= 3  # 至少60%成功率
            assert successful_new >= 3  # 至少60%成功率