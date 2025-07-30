from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

# 數據庫配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./subscription_db.sqlite")

# 創建數據庫引擎
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建表
def create_tables():
    Base.metadata.create_all(bind=engine)

# 數據庫依賴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()