from typing import List, Optional, Generic, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.domain.interfaces.repositories import BaseRepository

T = TypeVar('T')

class SQLAlchemyBaseRepository(BaseRepository[T], Generic[T]):
    """SQLAlchemy 基礎 Repository 實現"""
    
    def __init__(self, db_session: Session, model_class: Type[T]):
        self._db_session = db_session
        self._model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        """根據 ID 獲取實體"""
        try:
            return self._db_session.query(self._model_class).filter(
                self._model_class.id == id
            ).first()
        except SQLAlchemyError:
            return None
    
    def get_all(self) -> List[T]:
        """獲取所有實體"""
        try:
            return self._db_session.query(self._model_class).all()
        except SQLAlchemyError:
            return []
    
    def create(self, entity: T) -> T:
        """創建實體"""
        try:
            self._db_session.add(entity)
            self._db_session.flush()  # 刷新以獲取 ID，但不提交
            self._db_session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self._db_session.rollback()
            raise e
    
    def update(self, entity: T) -> T:
        """更新實體"""
        try:
            self._db_session.merge(entity)
            self._db_session.flush()
            self._db_session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self._db_session.rollback()
            raise e
    
    def delete(self, id: int) -> bool:
        """刪除實體"""
        try:
            entity = self.get_by_id(id)
            if entity:
                self._db_session.delete(entity)
                self._db_session.flush()
                return True
            return False
        except SQLAlchemyError as e:
            self._db_session.rollback()
            raise e
    
    def exists(self, id: int) -> bool:
        """檢查實體是否存在"""
        try:
            return self._db_session.query(self._model_class).filter(
                self._model_class.id == id
            ).count() > 0
        except SQLAlchemyError:
            return False