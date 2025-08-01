from abc import ABC, abstractmethod
from typing import Dict, Any
from decimal import Decimal

class IExchangeRateService(ABC):
    """匯率服務接口"""
    
    @abstractmethod
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """獲取匯率"""
        pass
    
    @abstractmethod
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """貨幣轉換"""
        pass
    
    @abstractmethod
    async def get_supported_currencies(self) -> Dict[str, str]:
        """獲取支持的貨幣列表"""
        pass

class IEmailService(ABC):
    """郵件服務接口"""
    
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """發送郵件"""
        pass
    
    @abstractmethod
    async def send_subscription_reminder(self, user_email: str, subscription_name: str, amount: float) -> bool:
        """發送訂閱提醒"""
        pass

class ICacheService(ABC):
    """緩存服務接口"""
    
    @abstractmethod
    async def get(self, key: str) -> Any:
        """獲取緩存"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """設置緩存"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """刪除緩存"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """檢查緩存是否存在"""
        pass