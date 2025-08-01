from typing import Optional, Any, Dict, List, Generic, TypeVar
from pydantic import BaseModel
from enum import Enum

T = TypeVar('T')

class ResponseStatus(str, Enum):
    """響應狀態枚舉"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ApiResponse(BaseModel, Generic[T]):
    """統一 API 響應格式"""
    status: ResponseStatus
    message: Optional[str] = None
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success(
        cls,
        data: Optional[T] = None,
        message: str = "操作成功",
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ApiResponse[T]":
        """成功響應"""
        return cls(
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
            metadata=metadata
        )
    
    @classmethod
    def error(
        cls,
        message: str = "操作失敗", 
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ApiResponse[None]":
        """錯誤響應"""
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            errors=errors or [],
            metadata=metadata
        )
    
    @classmethod
    def warning(
        cls,
        data: Optional[T] = None,
        message: str = "操作完成但有警告",
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ApiResponse[T]":
        """警告響應"""
        return cls(
            status=ResponseStatus.WARNING,
            message=message,
            data=data,
            errors=errors or [],
            metadata=metadata
        )

class PaginatedResponse(BaseModel, Generic[T]):
    """分頁響應格式"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int
    ) -> "PaginatedResponse[T]":
        """創建分頁響應"""
        pages = (total + size - 1) // size  # 向上取整
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )

class ValidationErrorDetail(BaseModel):
    """驗證錯誤詳情"""
    field: str
    message: str
    value: Any

class ApiValidationError(BaseModel):
    """API 驗證錯誤響應"""
    status: ResponseStatus = ResponseStatus.ERROR
    message: str = "驗證失敗"
    details: List[ValidationErrorDetail]