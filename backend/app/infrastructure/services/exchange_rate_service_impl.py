from typing import Dict
from decimal import Decimal
import httpx
import asyncio
from datetime import datetime, timedelta

from app.domain.interfaces.services import IExchangeRateService

class ExchangeRateServiceImpl(IExchangeRateService):
    """匯率服務實現"""
    
    def __init__(self):
        self._cache = {}
        self._cache_expiry = {}
        self._cache_duration = timedelta(hours=1)  # 緩存1小時
        
        # 支持的貨幣
        self._supported_currencies = {
            "TWD": "新台幣",
            "USD": "美元", 
            "EUR": "歐元",
            "JPY": "日圓",
            "GBP": "英鎊",
            "KRW": "韓圓",
            "CNY": "人民幣"
        }
        
        # 模擬匯率數據（生產環境應該從外部API獲取）
        self._mock_rates = {
            ("USD", "TWD"): Decimal("31.5"),
            ("EUR", "TWD"): Decimal("34.2"),
            ("JPY", "TWD"): Decimal("0.22"),
            ("GBP", "TWD"): Decimal("39.8"),
            ("KRW", "TWD"): Decimal("0.024"),
            ("CNY", "TWD"): Decimal("4.35"),
        }
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """獲取匯率"""
        if from_currency == to_currency:
            return Decimal("1.0")
        
        cache_key = f"{from_currency}_{to_currency}"
        
        # 檢查緩存
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        # 獲取匯率
        rate = await self._fetch_exchange_rate(from_currency, to_currency)
        
        # 更新緩存
        self._cache[cache_key] = rate
        self._cache_expiry[cache_key] = datetime.now() + self._cache_duration
        
        return rate
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """貨幣轉換"""
        if from_currency == to_currency:
            return amount
        
        rate = await self.get_exchange_rate(from_currency, to_currency)
        return float(Decimal(str(amount)) * rate)
    
    async def get_supported_currencies(self) -> Dict[str, str]:
        """獲取支持的貨幣列表"""
        return self._supported_currencies.copy()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """檢查緩存是否有效"""
        if cache_key not in self._cache:
            return False
        
        if cache_key not in self._cache_expiry:
            return False
        
        return datetime.now() < self._cache_expiry[cache_key]
    
    async def _fetch_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """獲取匯率數據"""
        # 首先嘗試直接查找
        rate_key = (from_currency, to_currency)
        if rate_key in self._mock_rates:
            return self._mock_rates[rate_key]
        
        # 嘗試反向查找
        reverse_key = (to_currency, from_currency)
        if reverse_key in self._mock_rates:
            return Decimal("1") / self._mock_rates[reverse_key]
        
        # 通過TWD作為中間貨幣
        if from_currency != "TWD" and to_currency != "TWD":
            try:
                from_to_twd = await self.get_exchange_rate(from_currency, "TWD")
                twd_to_target = await self.get_exchange_rate("TWD", to_currency)
                return from_to_twd * twd_to_target
            except:
                pass
        
        # 如果都找不到，返回默認匯率
        return Decimal("1.0")
    
    async def _fetch_from_external_api(self, from_currency: str, to_currency: str) -> Decimal:
        """從外部API獲取匯率（實際實現時使用）"""
        # 這裡可以集成真實的匯率API，例如：
        # - Fixer.io
        # - Exchange Rates API
        # - CurrencyLayer
        # - Alpha Vantage
        
        try:
            async with httpx.AsyncClient() as client:
                # 示例API調用（需要替換為真實的API）
                # response = await client.get(f"https://api.exchangerate-api.com/v4/latest/{from_currency}")
                # data = response.json()
                # return Decimal(str(data["rates"][to_currency]))
                pass
        except Exception as e:
            # API調用失敗時的回退邏輯
            print(f"外部匯率API調用失敗: {e}")
            return await self._fetch_exchange_rate(from_currency, to_currency)
        
        # 暫時返回模擬數據
        return await self._fetch_exchange_rate(from_currency, to_currency)