from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar
from sqlalchemy.orm import Session

from app.models import User, Subscription, Budget

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """基礎 Repository 接口"""
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

class IUserRepository(BaseRepository[User]):
    """用戶 Repository 接口"""
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

class ISubscriptionRepository(BaseRepository[Subscription]):
    """訂閱 Repository 接口"""
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Subscription]:
        pass
    
    @abstractmethod
    def get_active_by_user_id(self, user_id: int) -> List[Subscription]:
        pass
    
    @abstractmethod
    def get_by_user_and_id(self, user_id: int, subscription_id: int) -> Optional[Subscription]:
        pass

class IBudgetRepository(BaseRepository[Budget]):
    """預算 Repository 接口"""
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[Budget]:
        pass

class IUnitOfWork(ABC):
    """工作單元接口"""
    
    @property
    @abstractmethod
    def users(self) -> IUserRepository:
        pass
    
    @property
    @abstractmethod
    def subscriptions(self) -> ISubscriptionRepository:
        pass
    
    @property
    @abstractmethod
    def budgets(self) -> IBudgetRepository:
        pass
    
    @abstractmethod
    def begin(self):
        pass
    
    @abstractmethod
    def commit(self):
        pass
    
    @abstractmethod
    def rollback(self):
        pass
    
    @abstractmethod
    def close(self):
        pass