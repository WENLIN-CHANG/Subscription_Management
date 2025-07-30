from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models import User, Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from app.core.auth import get_current_active_user
from app.services.exchange_rate_service import ExchangeRateService

router = APIRouter(prefix="/subscriptions", tags=["訂閱管理"])

@router.get("/", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """獲取用戶的所有訂閱"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    return subscriptions

@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """創建新訂閱"""
    exchange_service = ExchangeRateService()
    
    # 如果不是台幣，需要轉換價格
    price_twd = subscription.price
    if subscription.currency.value != "TWD":
        price_twd = await exchange_service.convert_currency(
            subscription.currency.value, "TWD", subscription.original_price
        )
    
    db_subscription = Subscription(
        user_id=current_user.id,
        name=subscription.name,
        price=price_twd,  # 台幣價格
        original_price=subscription.original_price,  # 原始價格
        currency=subscription.currency,  # 原始貨幣
        cycle=subscription.cycle,
        category=subscription.category,
        start_date=subscription.start_date
    )
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    return db_subscription

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """獲取特定訂閱"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂閱不存在"
        )
    
    return subscription

@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    subscription_update: SubscriptionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新訂閱"""
    db_subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not db_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂閱不存在"
        )
    
    # 更新字段
    update_data = subscription_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subscription, field, value)
    
    db.commit()
    db.refresh(db_subscription)
    
    return db_subscription

@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """刪除訂閱"""
    db_subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not db_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂閱不存在"
        )
    
    db.delete(db_subscription)
    db.commit()
    
    return None