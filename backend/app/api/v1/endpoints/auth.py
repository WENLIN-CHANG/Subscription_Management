from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.common.responses import ApiResponse
from app.core.auth import create_access_token
from app.core.rate_limiter import auth_rate_limit, general_rate_limit

router = APIRouter()

@router.get("/health", response_model=ApiResponse[dict])
async def auth_health():
    """認證服務健康檢查"""
    return ApiResponse.success(
        data={"service": "auth", "status": "healthy"},
        message="認證服務運行正常"
    )

# TODO: 完整的認證功能需要在後續實施
# 目前暫時註釋掉，避免啟動錯誤