from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from app.database.connection import create_tables
from app.core.config import settings
from app.core.rate_limiter import (
    limiter, 
    rate_limit_exceeded_handler,
    get_rate_limiter_status
)
from app.core.logging_config import setup_logging, app_logger
from app.middleware.logging_middleware import LoggingMiddleware, SecurityLoggingMiddleware
from app.api import auth, subscriptions, budget, exchange_rates

# 創建 FastAPI 應用
app = FastAPI(
    title="訂閱管理系統 API",
    description="一個現代化的訂閱管理和預算追蹤系統",
    version="1.0.0"
)

# 添加速率限制器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS 中間件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite 默認端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加日誌中間件
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityLoggingMiddleware)

# 啟動時創建數據庫表
@app.on_event("startup")
async def startup_event():
    # 初始化日誌系統
    setup_logging()
    app_logger.info("訂閱管理系統 API 啟動")
    
    # 創建數據庫表
    create_tables()
    app_logger.info("數據庫表初始化完成")

# 根路由
@app.get("/")
async def root():
    return {
        "message": "訂閱管理系統 API", 
        "version": "1.0.0",
        "status": "running"
    }

# 健康檢查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rate_limiter": get_rate_limiter_status()
    }

# 包含路由
app.include_router(auth.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(budget.router, prefix="/api")
app.include_router(exchange_rates.router, prefix="/api/exchange", tags=["匯率"])