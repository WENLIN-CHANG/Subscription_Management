from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from slowapi.errors import RateLimitExceeded

from app.database.connection import create_tables
from app.core.config import settings
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.core.logging_config import setup_logging, app_logger
from app.common.exception_handlers import (
    application_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    pydantic_validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
from app.common.exceptions import ApplicationException
from app.common.middleware import (
    RequestValidationMiddleware,
    ResponseHeadersMiddleware,
    RequestTimingMiddleware,
    RequestIDMiddleware,
    APIMetricsMiddleware
)
from app.infrastructure.container import configure_container
from app.api.v1.router import api_router

# 配置依賴注入容器
container = configure_container()

# 創建 FastAPI 應用
app = FastAPI(
    title="訂閱管理系統 API",
    description="一個現代化的訂閱管理和預算追蹤系統 - 重構版",
    version="2.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# 添加速率限制器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# 添加異常處理器
app.add_exception_handler(ApplicationException, application_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS 中間件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定義中間件
app.add_middleware(APIMetricsMiddleware)
app.add_middleware(ResponseHeadersMiddleware)
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestValidationMiddleware, max_request_size=2*1024*1024)  # 2MB

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    # 初始化日誌系統
    setup_logging()
    app_logger.info("訂閱管理系統 API v2.0 啟動")
    
    # 創建數據庫表
    create_tables()
    app_logger.info("數據庫表初始化完成")
    
    app_logger.info("新架構初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    app_logger.info("訂閱管理系統 API 關閉")

# 根路由
@app.get("/")
async def root():
    return {
        "message": "訂閱管理系統 API - 重構版", 
        "version": "2.0.0",
        "status": "running",
        "architecture": "Clean Architecture with DDD",
        "features": [
            "領域驅動設計",
            "依賴注入",
            "Repository 模式",
            "Unit of Work 模式",
            "統一響應格式",
            "API 版本控制",
            "完善的錯誤處理"
        ]
    }

# 健康檢查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "Clean Architecture"
    }

# API 版本檢查
@app.get("/api/version")
async def api_version():
    return {
        "api_version": "v1",
        "app_version": "2.0.0",
        "supported_versions": ["v1"]
    }

# 包含 v1 API 路由
app.include_router(
    api_router,
    prefix="/api/v1"
)

# 為了向後兼容，保留舊的路由前綴
app.include_router(
    api_router,
    prefix="/api"
)