from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from . import Base

class SubscriptionCycle(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    DAILY = "daily"

class SubscriptionCategory(str, enum.Enum):
    STREAMING = "streaming"
    SOFTWARE = "software"
    NEWS = "news"
    GAMING = "gaming"
    MUSIC = "music"
    EDUCATION = "education"
    PRODUCTIVITY = "productivity"
    OTHER = "other"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    cycle = Column(Enum(SubscriptionCycle), nullable=False, default=SubscriptionCycle.MONTHLY)
    category = Column(Enum(SubscriptionCategory), nullable=False, default=SubscriptionCategory.OTHER)
    start_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 關聯
    user = relationship("User", back_populates="subscriptions")