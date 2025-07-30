from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import create_tables
from app.core.config import settings
from app.api import auth

# 創建 FastAPI 應用
app = FastAPI(
    title="訂閱管理系統 API",
    description="一個現代化的訂閱管理和預算追蹤系統",
    version="1.0.0"
)

# CORS 中間件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite 默認端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 啟動時創建數據庫表
@app.on_event("startup")
async def startup_event():
    create_tables()

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
    return {"status": "healthy"}

# 包含路由
app.include_router(auth.router, prefix="/api")