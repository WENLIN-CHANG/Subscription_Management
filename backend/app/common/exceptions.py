from typing import Optional, List, Dict, Any

class ApplicationException(Exception):
    """應用程序基礎異常"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        self.metadata = metadata or {}

class ValidationException(ApplicationException):
    """驗證異常"""
    
    def __init__(
        self,
        message: str = "驗證失敗",
        errors: Optional[List[str]] = None,
        field_errors: Optional[Dict[str, str]] = None
    ):
        super().__init__(message, 400, errors)
        self.field_errors = field_errors or {}

class NotFoundException(ApplicationException):
    """資源不存在異常"""
    
    def __init__(self, resource: str = "資源", resource_id: Optional[str] = None):
        message = f"{resource}不存在"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, 404)

class ConflictException(ApplicationException):
    """衝突異常"""
    
    def __init__(self, message: str = "資源衝突"):
        super().__init__(message, 409)

class UnauthorizedException(ApplicationException):
    """未授權異常"""
    
    def __init__(self, message: str = "未授權訪問"):
        super().__init__(message, 401)

class ForbiddenException(ApplicationException):
    """禁止訪問異常"""
    
    def __init__(self, message: str = "禁止訪問"):
        super().__init__(message, 403)

class TooManyRequestsException(ApplicationException):
    """請求過多異常"""
    
    def __init__(self, message: str = "請求過於頻繁"):
        super().__init__(message, 429)

class ExternalServiceException(ApplicationException):
    """外部服務異常"""
    
    def __init__(
        self, 
        service_name: str,
        message: str = "外部服務錯誤",
        original_error: Optional[Exception] = None
    ):
        super().__init__(f"{service_name}: {message}", 502)
        self.service_name = service_name
        self.original_error = original_error

class BusinessRuleException(ApplicationException):
    """業務規則異常"""
    
    def __init__(self, message: str = "業務規則驗證失敗"):
        super().__init__(message, 422)