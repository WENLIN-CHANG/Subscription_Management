from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domain.interfaces.repositories import ISubscriptionRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository
from app.models.subscription import Subscription

class SubscriptionRepository(SQLAlchemyBaseRepository[Subscription], ISubscriptionRepository):
    """訂閱 Repository 實現"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Subscription)
    
    def get_by_user_id(self, user_id: int) -> List[Subscription]:
        """根據用戶 ID 獲取所有訂閱"""
        try:
            return self._db_session.query(Subscription).filter(
                Subscription.user_id == user_id
            ).order_by(Subscription.created_at.desc()).all()
        except SQLAlchemyError:
            return []
    
    def get_active_by_user_id(self, user_id: int) -> List[Subscription]:
        """根據用戶 ID 獲取活躍訂閱"""
        try:
            return self._db_session.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).order_by(Subscription.created_at.desc()).all()
        except SQLAlchemyError:
            return []
    
    def get_by_user_and_id(self, user_id: int, subscription_id: int) -> Optional[Subscription]:
        """根據用戶 ID 和訂閱 ID 獲取訂閱"""
        try:
            return self._db_session.query(Subscription).filter(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            ).first()
        except SQLAlchemyError:
            return None
    
    def get_by_category(self, user_id: int, category: str) -> List[Subscription]:
        """根據類別獲取用戶訂閱"""
        try:
            return self._db_session.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.category == category,
                Subscription.is_active == True
            ).order_by(Subscription.created_at.desc()).all()
        except SQLAlchemyError:
            return []
    
    def get_by_name_pattern(self, user_id: int, name_pattern: str) -> List[Subscription]:
        """根據名稱模式搜索訂閱"""
        try:
            return self._db_session.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.name.ilike(f"%{name_pattern}%")
            ).order_by(Subscription.created_at.desc()).all()
        except SQLAlchemyError:
            return []
    
    def count_by_user_id(self, user_id: int) -> int:
        """統計用戶訂閱數量"""
        try:
            return self._db_session.query(Subscription).filter(
                Subscription.user_id == user_id
            ).count()
        except SQLAlchemyError:
            return 0
    
    def count_active_by_user_id(self, user_id: int) -> int:
        """統計用戶活躍訂閱數量"""
        try:
            return self._db_session.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).count()
        except SQLAlchemyError:
            return 0