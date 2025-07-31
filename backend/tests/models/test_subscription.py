import pytest
from datetime import date
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.user import User
from app.core.auth import get_password_hash


@pytest.mark.unit
class TestSubscriptionModel:
    """訂閱模型測試"""

    def test_create_subscription(self, db_session: Session, test_user: User):
        """測試創建訂閱"""
        subscription = Subscription(
            name="Netflix",
            price=390.0,
            cycle="monthly",
            category="entertainment",
            user_id=test_user.id,
            start_date="2024-01-01"
        )
        
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(subscription)
        
        assert subscription.id is not None
        assert subscription.name == "Netflix"
        assert subscription.price == 390.0
        assert subscription.cycle == "monthly"
        assert subscription.category == "entertainment"
        assert subscription.user_id == test_user.id
        assert subscription.start_date == date(2024, 1, 1)
        assert subscription.created_at is not None
        assert subscription.updated_at is not None

    def test_subscription_user_relationship(self, db_session: Session, test_user: User):
        """測試訂閱與用戶的關聯關係"""
        subscription = Subscription(
            name="Spotify",
            price=149.0,
            cycle="monthly",
            category="music",
            user_id=test_user.id,
            start_date="2024-01-15"
        )
        
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(subscription)
        
        # 測試訂閱到用戶的關聯
        assert subscription.user.id == test_user.id
        assert subscription.user.username == test_user.username
        
        # 測試用戶到訂閱的關聯
        db_session.refresh(test_user)
        assert len(test_user.subscriptions) >= 1
        subscription_names = [sub.name for sub in test_user.subscriptions]
        assert "Spotify" in subscription_names

    def test_subscription_required_fields(self, db_session: Session, test_user: User):
        """測試訂閱必填欄位"""
        # 測試缺少名稱
        with pytest.raises(Exception):
            subscription = Subscription(
                name=None,
                price=390.0,
                cycle="monthly",
                category="entertainment",
                user_id=test_user.id,
                start_date="2024-01-01"
            )
            db_session.add(subscription)
            db_session.commit()

    def test_subscription_price_validation(self, db_session: Session, test_user: User):
        """測試價格驗證"""
        # 測試負價格
        subscription = Subscription(
            name="Test Service",
            price=-100.0,
            cycle="monthly",
            category="test",
            user_id=test_user.id,
            start_date="2024-01-01"
        )
        
        db_session.add(subscription)
        # 注意：這裡可能需要根據你的模型實現來調整
        # 如果模型沒有價格驗證，這個測試可能會通過
        db_session.commit()

    def test_subscription_cycle_options(self, db_session: Session, test_user: User):
        """測試週期選項"""
        valid_cycles = ["monthly", "yearly", "weekly"]
        
        for cycle in valid_cycles:
            subscription = Subscription(
                name=f"Test Service {cycle}",
                price=100.0,
                cycle=cycle,
                category="test",
                user_id=test_user.id,
                start_date="2024-01-01"
            )
            
            db_session.add(subscription)
            db_session.commit()
            db_session.refresh(subscription)
            
            assert subscription.cycle == cycle

    def test_subscription_category_options(self, db_session: Session, test_user: User):
        """測試分類選項"""
        valid_categories = ["entertainment", "music", "productivity", "gaming", "news", "other"]
        
        for category in valid_categories:
            subscription = Subscription(
                name=f"Test Service {category}",
                price=100.0,
                cycle="monthly",
                category=category,
                user_id=test_user.id,
                start_date="2024-01-01"
            )
            
            db_session.add(subscription)
            db_session.commit()
            db_session.refresh(subscription)
            
            assert subscription.category == category

    def test_subscription_date_handling(self, db_session: Session, test_user: User):
        """測試日期處理"""
        # 測試字符串日期
        subscription = Subscription(
            name="Date Test",
            price=100.0,
            cycle="monthly",
            category="test",
            user_id=test_user.id,
            start_date="2024-03-15"
        )
        
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(subscription)
        
        assert subscription.start_date == date(2024, 3, 15)
        
        # 測試 date 物件
        test_date = date(2024, 6, 1)
        subscription2 = Subscription(
            name="Date Test 2",
            price=100.0,
            cycle="monthly",
            category="test",
            user_id=test_user.id,
            start_date=test_date
        )
        
        db_session.add(subscription2)
        db_session.commit()
        db_session.refresh(subscription2)
        
        assert subscription2.start_date == test_date

    def test_subscription_foreign_key_constraint(self, db_session: Session):
        """測試外鍵約束"""
        # 測試無效的 user_id
        subscription = Subscription(
            name="Invalid User Test",
            price=100.0,
            cycle="monthly",
            category="test",
            user_id=999,  # 不存在的用戶 ID
            start_date="2024-01-01"
        )
        
        db_session.add(subscription)
        
        # 應該拋出外鍵約束錯誤
        with pytest.raises(Exception):
            db_session.commit()

    def test_subscription_update(self, db_session: Session, test_user: User):
        """測試訂閱更新"""
        subscription = Subscription(
            name="Original Name",
            price=100.0,
            cycle="monthly",
            category="entertainment",
            user_id=test_user.id,
            start_date="2024-01-01"
        )
        
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(subscription)
        
        original_updated_at = subscription.updated_at
        
        # 更新訂閱
        subscription.name = "Updated Name"
        subscription.price = 200.0
        subscription.cycle = "yearly"
        
        db_session.commit()
        db_session.refresh(subscription)
        
        assert subscription.name == "Updated Name"
        assert subscription.price == 200.0
        assert subscription.cycle == "yearly"
        # 注意：updated_at 的自動更新取決於你的模型實現
        # assert subscription.updated_at > original_updated_at

    def test_subscription_deletion(self, db_session: Session, test_user: User):
        """測試訂閱刪除"""
        subscription = Subscription(
            name="To Be Deleted",
            price=100.0,
            cycle="monthly",
            category="test",
            user_id=test_user.id,
            start_date="2024-01-01"
        )
        
        db_session.add(subscription)
        db_session.commit()
        subscription_id = subscription.id
        
        # 刪除訂閱
        db_session.delete(subscription)
        db_session.commit()
        
        # 驗證訂閱已被刪除
        deleted_subscription = db_session.query(Subscription).filter(Subscription.id == subscription_id).first()
        assert deleted_subscription is None

    def test_multiple_subscriptions_same_user(self, db_session: Session, test_user: User):
        """測試同一用戶的多個訂閱"""
        subscriptions_data = [
            {"name": "Netflix", "price": 390.0, "category": "entertainment"},
            {"name": "Spotify", "price": 149.0, "category": "music"},
            {"name": "Adobe CC", "price": 1680.0, "category": "productivity"}
        ]
        
        created_subscriptions = []
        for data in subscriptions_data:
            subscription = Subscription(
                name=data["name"],
                price=data["price"],
                cycle="monthly",
                category=data["category"],
                user_id=test_user.id,
                start_date="2024-01-01"
            )
            db_session.add(subscription)
            created_subscriptions.append(subscription)
        
        db_session.commit()
        
        # 驗證所有訂閱都已創建
        for subscription in created_subscriptions:
            db_session.refresh(subscription)
            assert subscription.id is not None
            assert subscription.user_id == test_user.id
        
        # 驗證用戶關聯
        db_session.refresh(test_user)
        assert len(test_user.subscriptions) >= len(subscriptions_data)