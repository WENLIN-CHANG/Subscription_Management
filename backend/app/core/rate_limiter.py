import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from typing import Optional
import os
from functools import lru_cache

from app.core.config import settings


class RateLimiterConfig:
    """速率限制配置"""
    
    # 基本限制
    GENERAL_RATE_LIMIT = "100/minute"  # 一般 API 限制
    
    # 認證相關限制（更嚴格）
    AUTH_RATE_LIMIT = "5/minute"       # 登入/註冊限制
    PASSWORD_CHANGE_LIMIT = "3/minute" # 密碼修改限制
    
    # 資源密集操作限制
    CREATE_RATE_LIMIT = "20/minute"    # 創建操作限制
    UPLOAD_RATE_LIMIT = "10/minute"    # 上傳操作限制
    
    # 查詢操作限制
    READ_RATE_LIMIT = "200/minute"     # 讀取操作限制


def get_redis_client() -> Optional[redis.Redis]:
    """獲取 Redis 客戶端"""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url, decode_responses=True)
        # 測試連接
        client.ping()
        return client
    except Exception as e:
        print(f"Redis 連接失敗，使用內存存儲: {e}")
        return None


def get_user_id_from_token(request: Request) -> str:
    """從 JWT token 中提取用戶 ID 作為限制標識符"""
    try:
        # 嘗試從請求中獲取當前用戶信息
        if hasattr(request.state, 'current_user') and request.state.current_user:
            return f"user:{request.state.current_user.id}"
    except Exception:
        pass
    
    # 如果無法獲取用戶信息，回退到 IP 地址
    return f"ip:{get_remote_address(request)}"


def get_identifier_for_auth(request: Request) -> str:
    """為認證端點獲取更嚴格的標識符（基於 IP）"""
    return f"auth:{get_remote_address(request)}"


# 創建 Redis 客戶端
redis_client = get_redis_client()

# 創建限制器實例
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/0" if redis_client else "memory://",
    default_limits=["200/minute"]  # 默認限制
)

# 用戶特定的限制器
user_limiter = Limiter(
    key_func=get_user_id_from_token,
    storage_uri="redis://localhost:6379/0" if redis_client else "memory://",
    default_limits=["100/minute"]
)

# 認證特定的限制器
auth_limiter = Limiter(
    key_func=get_identifier_for_auth,
    storage_uri="redis://localhost:6379/0" if redis_client else "memory://",
    default_limits=["10/minute"]
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """自定義速率限制超出處理器"""
    response = HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "速率限制超出",
            "message": f"請求過於頻繁，請在 {exc.retry_after} 秒後重試",
            "retry_after": exc.retry_after,
            "limit": exc.detail
        }
    )
    return response


# 常用的速率限制裝飾器
def general_rate_limit():
    """一般 API 速率限制"""
    return limiter.limit(RateLimiterConfig.GENERAL_RATE_LIMIT)


def auth_rate_limit():
    """認證 API 速率限制"""
    return auth_limiter.limit(RateLimiterConfig.AUTH_RATE_LIMIT)


def password_change_rate_limit():
    """密碼修改速率限制"""
    return auth_limiter.limit(RateLimiterConfig.PASSWORD_CHANGE_LIMIT)


def create_rate_limit():
    """創建操作速率限制"""
    return user_limiter.limit(RateLimiterConfig.CREATE_RATE_LIMIT)


def read_rate_limit():
    """讀取操作速率限制"""
    return user_limiter.limit(RateLimiterConfig.READ_RATE_LIMIT)


def upload_rate_limit():
    """上傳操作速率限制"""
    return user_limiter.limit(RateLimiterConfig.UPLOAD_RATE_LIMIT)


@lru_cache()
def get_rate_limiter_status() -> dict:
    """獲取速率限制器狀態"""
    return {
        "redis_connected": redis_client is not None,
        "storage_type": "redis" if redis_client else "memory",
        "limits": {
            "general": RateLimiterConfig.GENERAL_RATE_LIMIT,
            "auth": RateLimiterConfig.AUTH_RATE_LIMIT,
            "password_change": RateLimiterConfig.PASSWORD_CHANGE_LIMIT,
            "create": RateLimiterConfig.CREATE_RATE_LIMIT,
            "read": RateLimiterConfig.READ_RATE_LIMIT,
            "upload": RateLimiterConfig.UPLOAD_RATE_LIMIT
        }
    }


def reset_user_limits(user_id: int) -> bool:
    """重置特定用戶的速率限制（管理員功能）"""
    try:
        if redis_client:
            # 清除與用戶相關的所有限制鍵
            pattern = f"*user:{user_id}*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                return True
        return False
    except Exception as e:
        print(f"重置用戶限制失敗: {e}")
        return False


def get_user_limit_status(user_id: int) -> dict:
    """獲取用戶當前的限制狀態"""
    try:
        if redis_client:
            user_key = f"user:{user_id}"
            # 這裡需要根據實際的 slowapi 實現來獲取限制狀態
            # 這是一個簡化的實現
            return {
                "user_id": user_id,
                "limits_active": True,
                "storage": "redis"
            }
        else:
            return {
                "user_id": user_id,
                "limits_active": True,
                "storage": "memory"
            }
    except Exception as e:
        return {
            "user_id": user_id,
            "limits_active": False,
            "error": str(e)
        }