import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import get_db, Base
from app.core.config import settings
from app.models.user import User
from app.models.subscription import Subscription
from app.core.auth import get_password_hash, create_access_token

# 測試資料庫配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環"""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """創建測試資料庫會話"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """創建測試客戶端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """創建測試用戶"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session):
    """創建測試管理員用戶"""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """創建認證標頭"""
    access_token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_auth_headers(test_admin_user):
    """創建管理員認證標頭"""
    access_token = create_access_token(data={"sub": test_admin_user.username})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_subscription(db_session, test_user):
    """創建測試訂閱"""
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
    return subscription


@pytest.fixture
def multiple_test_subscriptions(db_session, test_user):
    """創建多個測試訂閱"""
    subscriptions = [
        Subscription(
            name="Netflix",
            price=390.0,
            cycle="monthly",
            category="entertainment",
            user_id=test_user.id,
            start_date="2024-01-01"
        ),
        Subscription(
            name="Spotify",
            price=149.0,
            cycle="monthly",
            category="music",
            user_id=test_user.id,
            start_date="2024-01-15"
        ),
        Subscription(
            name="Adobe Creative Cloud",
            price=1680.0,
            cycle="yearly",
            category="productivity",
            user_id=test_user.id,
            start_date="2024-02-01"
        )
    ]
    
    for subscription in subscriptions:
        db_session.add(subscription)
    
    db_session.commit()
    
    for subscription in subscriptions:
        db_session.refresh(subscription)
    
    return subscriptions


# 測試標記
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.auth = pytest.mark.auth
pytest.mark.api = pytest.mark.api
pytest.mark.slow = pytest.mark.slow