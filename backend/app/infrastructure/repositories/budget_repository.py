from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domain.interfaces.repositories import IBudgetRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository
from app.models.budget import Budget

class BudgetRepository(SQLAlchemyBaseRepository[Budget], IBudgetRepository):
    """預算 Repository 實現"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Budget)
    
    def get_by_user_id(self, user_id: int) -> Optional[Budget]:
        """根據用戶 ID 獲取預算"""
        try:
            return self._db_session.query(Budget).filter(
                Budget.user_id == user_id
            ).first()
        except SQLAlchemyError:
            return None
    
    def user_has_budget(self, user_id: int) -> bool:
        """檢查用戶是否有預算設置"""
        try:
            return self._db_session.query(Budget).filter(
                Budget.user_id == user_id
            ).count() > 0
        except SQLAlchemyError:
            return False