from sqlalchemy.ext.declarative import declarative_base

# 創建統一的 Base
Base = declarative_base()

# 導入模型類（注意順序，避免循環導入）
from .user import User, pwd_context
from .subscription import Subscription, SubscriptionCycle, SubscriptionCategory  
from .budget import Budget

__all__ = [
    "Base",
    "User",
    "Subscription", 
    "SubscriptionCycle",
    "SubscriptionCategory",
    "Budget",
    "pwd_context"
]