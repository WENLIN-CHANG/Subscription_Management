from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domain.interfaces.repositories import IUnitOfWork, IUserRepository, ISubscriptionRepository, IBudgetRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.subscription_repository import SubscriptionRepository
from app.infrastructure.repositories.budget_repository import BudgetRepository

class SQLAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy Unit of Work 實現"""
    
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._users: Optional[IUserRepository] = None
        self._subscriptions: Optional[ISubscriptionRepository] = None
        self._budgets: Optional[IBudgetRepository] = None
        self._transaction_started = False
    
    @property
    def users(self) -> IUserRepository:
        """用戶 Repository"""
        if self._users is None:
            self._users = UserRepository(self._db_session)
        return self._users
    
    @property
    def subscriptions(self) -> ISubscriptionRepository:
        """訂閱 Repository"""
        if self._subscriptions is None:
            self._subscriptions = SubscriptionRepository(self._db_session)
        return self._subscriptions
    
    @property
    def budgets(self) -> IBudgetRepository:
        """預算 Repository"""
        if self._budgets is None:
            self._budgets = BudgetRepository(self._db_session)
        return self._budgets
    
    def begin(self):
        """開始事務"""
        if not self._transaction_started:
            self._db_session.begin()
            self._transaction_started = True
    
    def commit(self):
        """提交事務"""
        try:
            if self._transaction_started:
                self._db_session.commit()
                self._transaction_started = False
        except SQLAlchemyError as e:
            self.rollback()
            raise e
    
    def rollback(self):
        """回滾事務"""
        try:
            if self._transaction_started:
                self._db_session.rollback()
                self._transaction_started = False
        except SQLAlchemyError:
            pass  # 回滾失敗也沒關係
    
    def close(self):
        """關閉會話"""
        try:
            if self._transaction_started:
                self.rollback()
            self._db_session.close()
        except SQLAlchemyError:
            pass
    
    def __enter__(self):
        """上下文管理器進入"""
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()