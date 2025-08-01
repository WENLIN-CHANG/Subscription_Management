"""
訂閱 Repository 測試

測試數據訪問層：
- CRUD 操作
- 查詢方法
- 過濾和排序
- 異常處理
- 數據完整性
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.repositories.subscription_repository import SubscriptionRepository
from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency


class TestSubscriptionRepository:
    """訂閱 Repository 測試類"""

    @pytest.fixture
    def subscription_repo(self, db_session):
        """創建訂閱 Repository 實例"""
        return SubscriptionRepository(db_session)

    @pytest.fixture
    def sample_subscriptions(self, db_session, test_user):
        """創建測試訂閱數據"""
        subscriptions = [
            Subscription(
                name="Netflix",
                price=390.0,
                original_price=390.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime(2024, 1, 1),
                is_active=True
            ),
            Subscription(
                name="Spotify",
                price=149.0,
                original_price=149.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.MUSIC,
                user_id=test_user.id,
                start_date=datetime(2024, 1, 15),
                is_active=True
            ),
            Subscription(
                name="Adobe Creative Cloud",
                price=1680.0,
                original_price=1680.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.YEARLY,
                category=SubscriptionCategory.PRODUCTIVITY,
                user_id=test_user.id,
                start_date=datetime(2024, 2, 1),
                is_active=False  # 非活躍
            )
        ]
        
        for subscription in subscriptions:
            db_session.add(subscription)
        
        db_session.commit()
        
        for subscription in subscriptions:
            db_session.refresh(subscription)
        
        return subscriptions

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestBasicCRUD:
        """基本 CRUD 操作測試"""

        def test_create_subscription(self, subscription_repo, test_user):
            """測試創建訂閱"""
            subscription = Subscription(
                name="Test Service",
                price=100.0,
                original_price=100.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime.now(),
                is_active=True
            )
            
            created = subscription_repo.create(subscription)
            
            assert created.id is not None
            assert created.name == "Test Service"
            assert created.price == 100.0
            assert created.user_id == test_user.id

        def test_get_by_id(self, subscription_repo, sample_subscriptions):
            """測試根據 ID 獲取訂閱"""
            subscription_id = sample_subscriptions[0].id
            
            result = subscription_repo.get_by_id(subscription_id)
            
            assert result is not None
            assert result.id == subscription_id
            assert result.name == "Netflix"

        def test_get_by_id_not_found(self, subscription_repo):
            """測試獲取不存在的訂閱"""
            result = subscription_repo.get_by_id(99999)
            
            assert result is None

        def test_update_subscription(self, subscription_repo, sample_subscriptions):
            """測試更新訂閱"""
            subscription = sample_subscriptions[0]
            original_name = subscription.name
            
            subscription.name = "Netflix Premium"
            subscription.price = 490.0
            
            updated = subscription_repo.update(subscription)
            
            assert updated.name == "Netflix Premium"
            assert updated.price == 490.0
            assert updated.id == subscription.id

        def test_delete_subscription(self, subscription_repo, sample_subscriptions):
            """測試刪除訂閱"""
            subscription_id = sample_subscriptions[0].id
            
            result = subscription_repo.delete(subscription_id)
            
            assert result is True
            
            # 驗證已刪除
            deleted_subscription = subscription_repo.get_by_id(subscription_id)
            assert deleted_subscription is None

        def test_delete_nonexistent_subscription(self, subscription_repo):
            """測試刪除不存在的訂閱"""
            result = subscription_repo.delete(99999)
            
            assert result is False

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestUserSpecificQueries:
        """用戶特定查詢測試"""

        def test_get_by_user_id(self, subscription_repo, sample_subscriptions, test_user):
            """測試根據用戶 ID 獲取所有訂閱"""
            result = subscription_repo.get_by_user_id(test_user.id)
            
            assert len(result) == 3
            # 應該按創建時間降序排列
            assert result[0].name == "Adobe Creative Cloud"  # 最後創建的
            assert result[1].name == "Spotify"
            assert result[2].name == "Netflix"

        def test_get_by_user_id_no_subscriptions(self, subscription_repo, test_admin_user):
            """測試獲取沒有訂閱的用戶"""
            result = subscription_repo.get_by_user_id(test_admin_user.id)
            
            assert len(result) == 0

        def test_get_active_by_user_id(self, subscription_repo, sample_subscriptions, test_user):
            """測試根據用戶 ID 獲取活躍訂閱"""
            result = subscription_repo.get_active_by_user_id(test_user.id)
            
            assert len(result) == 2  # 只有活躍的
            subscription_names = [s.name for s in result]
            assert "Netflix" in subscription_names
            assert "Spotify" in subscription_names
            assert "Adobe Creative Cloud" not in subscription_names  # 非活躍

        def test_get_by_user_and_id(self, subscription_repo, sample_subscriptions, test_user):
            """測試根據用戶 ID 和訂閱 ID 獲取訂閱"""
            subscription_id = sample_subscriptions[0].id
            
            result = subscription_repo.get_by_user_and_id(test_user.id, subscription_id)
            
            assert result is not None
            assert result.id == subscription_id
            assert result.user_id == test_user.id

        def test_get_by_user_and_id_wrong_user(self, subscription_repo, sample_subscriptions, test_admin_user):
            """測試用錯誤的用戶 ID 獲取訂閱"""
            subscription_id = sample_subscriptions[0].id
            
            result = subscription_repo.get_by_user_and_id(test_admin_user.id, subscription_id)
            
            assert result is None

        def test_get_by_user_and_id_nonexistent(self, subscription_repo, test_user):
            """測試獲取不存在的訂閱"""
            result = subscription_repo.get_by_user_and_id(test_user.id, 99999)
            
            assert result is None

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestCategoryQueries:
        """類別查詢測試"""

        def test_get_by_category(self, subscription_repo, sample_subscriptions, test_user):
            """測試根據類別獲取訂閱"""
            result = subscription_repo.get_by_category(test_user.id, "entertainment")
            
            assert len(result) == 1
            assert result[0].name == "Netflix"
            assert result[0].category == SubscriptionCategory.ENTERTAINMENT

        def test_get_by_category_no_results(self, subscription_repo, test_user):
            """測試獲取不存在類別的訂閱"""
            result = subscription_repo.get_by_category(test_user.id, "nonexistent")
            
            assert len(result) == 0

        def test_get_by_category_only_active(self, subscription_repo, sample_subscriptions, test_user):
            """測試類別查詢只返回活躍訂閱"""
            # 確保有非活躍的 productivity 訂閱
            assert sample_subscriptions[2].category == SubscriptionCategory.PRODUCTIVITY
            assert not sample_subscriptions[2].is_active
            
            result = subscription_repo.get_by_category(test_user.id, "productivity")
            
            assert len(result) == 0  # 非活躍的不應該返回

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestSearchQueries:
        """搜索查詢測試"""

        def test_get_by_name_pattern_exact_match(self, subscription_repo, sample_subscriptions, test_user):
            """測試精確名稱匹配搜索"""
            result = subscription_repo.get_by_name_pattern(test_user.id, "Netflix")
            
            assert len(result) == 1
            assert result[0].name == "Netflix"

        def test_get_by_name_pattern_partial_match(self, subscription_repo, sample_subscriptions, test_user):
            """測試部分名稱匹配搜索"""
            result = subscription_repo.get_by_name_pattern(test_user.id, "Spot")
            
            assert len(result) == 1
            assert result[0].name == "Spotify"

        def test_get_by_name_pattern_case_insensitive(self, subscription_repo, sample_subscriptions, test_user):
            """測試大小寫不敏感搜索"""
            result = subscription_repo.get_by_name_pattern(test_user.id, "netflix")
            
            assert len(result) == 1
            assert result[0].name == "Netflix"

        def test_get_by_name_pattern_multiple_matches(self, subscription_repo, sample_subscriptions, test_user):
            """測試多個匹配結果"""
            result = subscription_repo.get_by_name_pattern(test_user.id, "i")  # 包含 'i' 的服務
            
            # Netflix, Spotify, Creative 都包含 'i'
            assert len(result) >= 2
            names = [s.name for s in result]
            assert "Netflix" in names
            assert "Spotify" in names

        def test_get_by_name_pattern_no_matches(self, subscription_repo, test_user):
            """測試無匹配結果的搜索"""
            result = subscription_repo.get_by_name_pattern(test_user.id, "NonexistentService")
            
            assert len(result) == 0

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestCountingMethods:
        """計數方法測試"""

        def test_count_by_user_id(self, subscription_repo, sample_subscriptions, test_user):
            """測試統計用戶訂閱總數"""
            count = subscription_repo.count_by_user_id(test_user.id)
            
            assert count == 3

        def test_count_by_user_id_no_subscriptions(self, subscription_repo, test_admin_user):
            """測試統計無訂閱用戶"""
            count = subscription_repo.count_by_user_id(test_admin_user.id)
            
            assert count == 0

        def test_count_active_by_user_id(self, subscription_repo, sample_subscriptions, test_user):
            """測試統計用戶活躍訂閱數"""
            count = subscription_repo.count_active_by_user_id(test_user.id)
            
            assert count == 2  # 只有兩個活躍的

        def test_count_active_by_user_id_no_active(self, subscription_repo, db_session, test_admin_user):
            """測試統計無活躍訂閱的用戶"""
            # 創建一個非活躍的訂閱
            inactive_subscription = Subscription(
                name="Inactive Service",
                price=100.0,
                original_price=100.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_admin_user.id,
                start_date=datetime.now(),
                is_active=False
            )
            db_session.add(inactive_subscription)
            db_session.commit()
            
            count = subscription_repo.count_active_by_user_id(test_admin_user.id)
            
            assert count == 0

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestErrorHandling:
        """錯誤處理測試"""

        def test_get_by_user_id_database_error(self, subscription_repo, test_user):
            """測試數據庫錯誤時的處理"""
            # 關閉數據庫連接來模擬錯誤
            subscription_repo._db_session.close()
            
            result = subscription_repo.get_by_user_id(test_user.id)
            
            # 應該返回空列表而不是拋出異常
            assert result == []

        def test_get_active_by_user_id_database_error(self, subscription_repo, test_user):
            """測試獲取活躍訂閱時的數據庫錯誤"""
            subscription_repo._db_session.close()
            
            result = subscription_repo.get_active_by_user_id(test_user.id)
            
            assert result == []

        def test_get_by_user_and_id_database_error(self, subscription_repo, test_user):
            """測試根據用戶和ID獲取時的數據庫錯誤"""
            subscription_repo._db_session.close()
            
            result = subscription_repo.get_by_user_and_id(test_user.id, 1)
            
            assert result is None

        def test_get_by_category_database_error(self, subscription_repo, test_user):
            """測試根據類別獲取時的數據庫錯誤"""
            subscription_repo._db_session.close()
            
            result = subscription_repo.get_by_category(test_user.id, "entertainment")
            
            assert result == []

        def test_get_by_name_pattern_database_error(self, subscription_repo, test_user):
            """測試名稱搜索時的數據庫錯誤"""
            subscription_repo._db_session.close()
            
            result = subscription_repo.get_by_name_pattern(test_user.id, "test")
            
            assert result == []

        def test_count_methods_database_error(self, subscription_repo, test_user):
            """測試計數方法的數據庫錯誤"""
            subscription_repo._db_session.close()
            
            count_all = subscription_repo.count_by_user_id(test_user.id)
            count_active = subscription_repo.count_active_by_user_id(test_user.id)
            
            assert count_all == 0
            assert count_active == 0

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestDataIntegrity:
        """數據完整性測試"""

        def test_ordering_consistency(self, subscription_repo, db_session, test_user):
            """測試排序一致性"""
            # 創建具有明確時間順序的訂閱
            import time
            
            subscription1 = Subscription(
                name="First",
                price=100.0,
                original_price=100.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime.now(),
                is_active=True
            )
            db_session.add(subscription1)
            db_session.commit()
            
            time.sleep(0.1)  # 確保時間差異
            
            subscription2 = Subscription(
                name="Second",
                price=200.0,
                original_price=200.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime.now(),
                is_active=True
            )
            db_session.add(subscription2)
            db_session.commit()
            
            result = subscription_repo.get_by_user_id(test_user.id)
            
            # 應該按創建時間降序排列
            assert len(result) >= 2
            assert result[0].name == "Second"  # 最後創建的應該在前面

        def test_filter_integrity(self, subscription_repo, sample_subscriptions, test_user):
            """測試過濾器完整性"""
            all_subscriptions = subscription_repo.get_by_user_id(test_user.id)
            active_subscriptions = subscription_repo.get_active_by_user_id(test_user.id)
            
            # 活躍訂閱應該是所有訂閱的子集
            assert len(active_subscriptions) <= len(all_subscriptions)
            
            # 所有活躍訂閱都應該在全部訂閱中
            active_ids = {s.id for s in active_subscriptions}
            all_ids = {s.id for s in all_subscriptions}
            assert active_ids.issubset(all_ids)
            
            # 驗證所有返回的活躍訂閱確實是活躍的
            for subscription in active_subscriptions:
                assert subscription.is_active is True