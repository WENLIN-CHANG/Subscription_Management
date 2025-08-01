from fastapi import APIRouter
from app.api.v1.endpoints import subscriptions, budgets, auth, exchange_rates

api_router = APIRouter()

# 包含各個模塊的路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["認證 v1"]
)

api_router.include_router(
    subscriptions.router,
    prefix="/subscriptions",
    tags=["訂閱管理 v1"]
)

api_router.include_router(
    budgets.router,
    prefix="/budgets",
    tags=["預算管理 v1"]
)

api_router.include_router(
    exchange_rates.router,
    prefix="/exchange-rates",
    tags=["匯率服務 v1"]
)