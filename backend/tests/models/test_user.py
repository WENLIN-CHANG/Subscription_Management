import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.auth import verify_password, get_password_hash


@pytest.mark.unit
class TestUserModel:
    """用戶模型測試"""

    def test_create_user(self, db_session: Session):
        """測試創建用戶"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_password_hashing(self):
        """測試密碼哈希"""
        password = "plaintext_password"
        hashed = get_password_hash(password)
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed
        )
        
        # 驗證密碼不是明文存儲
        assert user.hashed_password != password
        assert verify_password(password, user.hashed_password)

    def test_user_verify_password_method(self, db_session: Session):
        """測試用戶密碼驗證方法"""
        password = "testpassword123"
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash(password)
        )
        
        db_session.add(user)
        db_session.commit()
        
        # 測試正確密碼
        assert user.verify_password(password) is True
        
        # 測試錯誤密碼
        assert user.verify_password("wrongpassword") is False

    def test_user_get_password_hash_method(self):
        """測試用戶密碼哈希方法"""
        password = "testpassword123"
        hashed = User.get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)

    def test_user_unique_username_constraint(self, db_session: Session):
        """測試用戶名唯一性約束"""
        user1 = User(
            username="testuser",
            email="test1@example.com",
            hashed_password=get_password_hash("password1")
        )
        
        user2 = User(
            username="testuser",  # 相同用戶名
            email="test2@example.com",
            hashed_password=get_password_hash("password2")
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        
        # 應該拋出完整性錯誤
        with pytest.raises(Exception):
            db_session.commit()

    def test_user_unique_email_constraint(self, db_session: Session):
        """測試電子郵件唯一性約束"""
        user1 = User(
            username="testuser1",
            email="test@example.com",
            hashed_password=get_password_hash("password1")
        )
        
        user2 = User(
            username="testuser2",
            email="test@example.com",  # 相同電子郵件
            hashed_password=get_password_hash("password2")
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        
        # 應該拋出完整性錯誤
        with pytest.raises(Exception):
            db_session.commit()

    def test_user_is_active_default(self, db_session: Session):
        """測試用戶預設為活躍狀態"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.is_active is True

    def test_user_deactivate(self, db_session: Session):
        """測試停用用戶"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        
        db_session.add(user)
        db_session.commit()
        
        # 停用用戶
        user.is_active = False
        db_session.commit()
        
        assert user.is_active is False

    def test_user_relationships(self, db_session: Session):
        """測試用戶關聯關係"""
        from app.models.subscription import Subscription
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # 創建訂閱
        subscription = Subscription(
            name="Netflix",
            price=390.0,
            cycle="monthly",
            category="entertainment",
            user_id=user.id,
            start_date="2024-01-01"
        )
        
        db_session.add(subscription)
        db_session.commit()
        
        # 測試關聯關係
        assert len(user.subscriptions) == 1
        assert user.subscriptions[0].name == "Netflix"
        assert subscription.user.username == "testuser"

    def test_user_string_representation(self, db_session: Session):
        """測試用戶字串表示"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        
        db_session.add(user)
        db_session.commit()
        
        # 測試 __str__ 方法（如果有實現的話）
        user_str = str(user)
        assert "testuser" in user_str or "User" in user_str