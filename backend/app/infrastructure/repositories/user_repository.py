from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domain.interfaces.repositories import IUserRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository
from app.models.user import User

class UserRepository(SQLAlchemyBaseRepository[User], IUserRepository):
    """用戶 Repository 實現"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根據郵箱獲取用戶"""
        try:
            return self._db_session.query(User).filter(
                User.email == email
            ).first()
        except SQLAlchemyError:
            return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根據用戶名獲取用戶"""
        try:
            return self._db_session.query(User).filter(
                User.username == username
            ).first()
        except SQLAlchemyError:
            return None
    
    def email_exists(self, email: str) -> bool:
        """檢查郵箱是否已存在"""
        try:
            return self._db_session.query(User).filter(
                User.email == email
            ).count() > 0
        except SQLAlchemyError:
            return False
    
    def username_exists(self, username: str) -> bool:
        """檢查用戶名是否已存在"""
        try:
            return self._db_session.query(User).filter(
                User.username == username
            ).count() > 0
        except SQLAlchemyError:
            return False