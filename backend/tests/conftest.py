import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, MagicMock

# 新架構的導入
from app.main_new import app as new_app  # 新架構的應用
from app.main import app as old_app  # 舊架構的應用 (向後兼容測試用)
from app.database.connection import get_db, Base
from app.core.config import settings
from app.models.user import User
from app.models.subscription import Subscription
from app.models.budget import Budget
from app.core.auth import get_password_hash, create_access_token

# 新架構組件導入
from app.infrastructure.container import configure_container
from app.infrastructure.dependencies import get_unit_of_work, get_subscription_app_service, get_budget_app_service
from app.infrastructure.unit_of_work import UnitOfWork
from app.application.services.subscription_application_service import SubscriptionApplicationService
from app.application.services.budget_application_service import BudgetApplicationService
from app.domain.services.subscription_domain_service import SubscriptionDomainService
from app.domain.services.budget_domain_service import BudgetDomainService

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
    """創建舊架構測試客戶端 (向後兼容測試用)"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    old_app.dependency_overrides[get_db] = override_get_db
    with TestClient(old_app) as test_client:
        yield test_client
    old_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def new_client(db_session):
    """創建新架構測試客戶端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # 覆蓋數據庫依賴
    new_app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(new_app) as test_client:
        yield test_client
    new_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def container():
    """創建測試用的依賴注入容器"""
    return configure_container()


@pytest.fixture(scope="function")
def unit_of_work(db_session):
    """創建測試用的 Unit of Work"""
    uow = UnitOfWork()
    # 注入測試資料庫會話
    uow._session = db_session
    return uow


@pytest.fixture(scope="function")
def subscription_domain_service():
    """創建訂閱領域服務"""
    return SubscriptionDomainService()


@pytest.fixture(scope="function")
def budget_domain_service():
    """創建預算領域服務"""
    return BudgetDomainService()


@pytest.fixture(scope="function")
def subscription_app_service(unit_of_work, subscription_domain_service):
    """創建訂閱應用服務"""
    return SubscriptionApplicationService(unit_of_work, subscription_domain_service)


@pytest.fixture(scope="function")
def budget_app_service(unit_of_work, budget_domain_service):
    """創建預算應用服務"""
    return BudgetApplicationService(unit_of_work, budget_domain_service)


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


@pytest.fixture
def test_budget(db_session, test_user):
    """創建測試預算"""
    budget = Budget(
        category="entertainment",
        amount=1000.0,
        period="monthly",
        user_id=test_user.id
    )
    db_session.add(budget)
    db_session.commit()
    db_session.refresh(budget)
    return budget


@pytest.fixture
def multiple_test_budgets(db_session, test_user):
    """創建多個測試預算"""
    budgets = [
        Budget(
            category="entertainment",
            amount=1000.0,
            period="monthly",
            user_id=test_user.id
        ),
        Budget(
            category="productivity",
            amount=2000.0,
            period="monthly",
            user_id=test_user.id
        ),
        Budget(
            category="music",
            amount=500.0,
            period="monthly",
            user_id=test_user.id
        )
    ]
    
    for budget in budgets:
        db_session.add(budget)
    
    db_session.commit()
    
    for budget in budgets:
        db_session.refresh(budget)
    
    return budgets


# 測試標記
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.auth = pytest.mark.auth
pytest.mark.api = pytest.mark.api
pytest.mark.slow = pytest.mark.slow
pytest.mark.domain = pytest.mark.domain  # 領域層測試
pytest.mark.application = pytest.mark.application  # 應用層測試
pytest.mark.infrastructure = pytest.mark.infrastructure  # 基礎設施層測試
pytest.mark.compatibility = pytest.mark.compatibility  # 向後兼容性測試
pytest.mark.performance = pytest.mark.performance  # 性能測試