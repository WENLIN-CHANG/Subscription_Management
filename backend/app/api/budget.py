from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models import User, Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.core.auth import get_current_active_user

router = APIRouter(prefix="/budget", tags=["預算管理"])

@router.get("/", response_model=BudgetResponse)
async def get_budget(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """獲取用戶預算"""
    budget = db.query(Budget).filter(Budget.user_id == current_user.id).first()
    
    if not budget:
        # 如果沒有預算，創建默認預算
        budget = Budget(user_id=current_user.id, monthly_amount=0.0)
        db.add(budget)
        db.commit()
        db.refresh(budget)
    
    return budget

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """創建或更新用戶預算"""
    existing_budget = db.query(Budget).filter(Budget.user_id == current_user.id).first()
    
    if existing_budget:
        # 更新現有預算
        existing_budget.monthly_amount = budget_data.monthly_amount
        db.commit()
        db.refresh(existing_budget)
        return existing_budget
    else:
        # 創建新預算
        new_budget = Budget(
            user_id=current_user.id,
            monthly_amount=budget_data.monthly_amount
        )
        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)
        return new_budget

@router.put("/", response_model=BudgetResponse)
async def update_budget(
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新預算"""
    budget = db.query(Budget).filter(Budget.user_id == current_user.id).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預算不存在"
        )
    
    update_data = budget_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(budget, field, value)
    
    db.commit()
    db.refresh(budget)
    
    return budget