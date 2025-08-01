from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from typing import Callable

from app.common.responses import ApiResponse
from app.common.validators import RequestSizeValidator

logger = logging.getLogger(__name__)

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """請求驗證中間件"""
    
    def __init__(self, app: ASGIApp, max_request_size: int = 1024 * 1024):
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 驗證請求大小
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                content_length = int(content_length)
                errors = RequestSizeValidator.validate_content_length(
                    content_length, self.max_request_size
                )
                if errors:
                    response = ApiResponse.error(
                        message="請求驗證失敗",
                        errors=errors
                    )
                    return JSONResponse(
                        status_code=413,
                        content=response.dict()
                    )
            except ValueError:
                pass
        
        # 驗證Content-Type（對於POST/PUT請求）
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json") and not content_type.startswith("multipart/form-data"):
                response = ApiResponse.error(
                    message="不支持的Content-Type",
                    errors=[f"當前Content-Type: {content_type}，支持的類型: application/json, multipart/form-data"]
                )
                return JSONResponse(
                    status_code=415,
                    content=response.dict()
                )
        
        response = await call_next(request)
        return response

class ResponseHeadersMiddleware(BaseHTTPMiddleware):
    """響應頭中間件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全頭
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # 添加API版本頭
        response.headers["X-API-Version"] = "1.0"
        
        # 添加響應時間
        if hasattr(request.state, "start_time"):
            process_time = time.time() - request.state.start_time
            response.headers["X-Process-Time"] = str(process_time)
        
        return response

class RequestTimingMiddleware(BaseHTTPMiddleware):
    """請求計時中間件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request.state.start_time = start_time
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )
        
        return response

class RequestIDMiddleware(BaseHTTPMiddleware):
    """請求ID中間件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import uuid
        
        # 生成請求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 添加到日誌上下文
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # 添加請求ID到響應頭
        response.headers["X-Request-ID"] = request_id
        
        return response

class CORSCustomMiddleware(BaseHTTPMiddleware):
    """自定義CORS中間件"""
    
    def __init__(self, app: ASGIApp, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method == "OPTIONS":
            # 處理預檢請求
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response
        
        response = await call_next(request)
        
        # 添加CORS頭
        origin = request.headers.get("origin")
        if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

class APIMetricsMiddleware(BaseHTTPMiddleware):
    """API指標中間件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        self.request_count += 1
        
        try:
            response = await call_next(request)
            
            # 記錄錯誤狀態碼
            if response.status_code >= 400:
                self.error_count += 1
            
            # 添加指標到響應頭（僅在開發環境）
            if request.app.debug:
                response.headers["X-Request-Count"] = str(self.request_count)
                response.headers["X-Error-Count"] = str(self.error_count)
            
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"請求處理異常: {str(e)}")
            raise