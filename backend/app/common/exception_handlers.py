from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.common.exceptions import ApplicationException
from app.common.responses import ApiResponse, ValidationErrorDetail, ApiValidationError

logger = logging.getLogger(__name__)

async def application_exception_handler(request: Request, exc: ApplicationException) -> JSONResponse:
    """應用程序異常處理器"""
    logger.error(f"應用程序異常: {exc.message}", exc_info=exc)
    
    response = ApiResponse.error(
        message=exc.message,
        errors=exc.errors,
        metadata=exc.metadata
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP 異常處理器"""
    logger.warning(f"HTTP 異常: {exc.detail}")
    
    response = ApiResponse.error(
        message=str(exc.detail) if exc.detail else "HTTP 錯誤"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """請求驗證異常處理器"""
    logger.warning(f"請求驗證失敗: {exc.errors()}")
    
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details.append(ValidationErrorDetail(
            field=field,
            message=error["msg"],
            value=error.get("input", "")
        ))
    
    response = ApiValidationError(details=details)
    
    return JSONResponse(
        status_code=422,
        content=response.dict()
    )

async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Pydantic 驗證異常處理器"""
    logger.warning(f"Pydantic 驗證失敗: {exc.errors()}")
    
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details.append(ValidationErrorDetail(
            field=field,
            message=error["msg"],
            value=error.get("input", "")
        ))
    
    response = ApiValidationError(details=details)
    
    return JSONResponse(
        status_code=422,
        content=response.dict()
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """SQLAlchemy 異常處理器"""
    logger.error(f"數據庫錯誤: {str(exc)}", exc_info=exc)
    
    response = ApiResponse.error(
        message="數據庫操作失敗",
        metadata={"error_type": "database_error"}
    )
    
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用異常處理器"""
    logger.error(f"未處理的異常: {str(exc)}", exc_info=exc)
    
    response = ApiResponse.error(
        message="服務器內部錯誤",
        metadata={"error_type": "internal_server_error"}
    )
    
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )