import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.database.connection import get_db
import os

class ExchangeRateService:
    """匯率服務 - 獲取和緩存匯率數據"""
    
    def __init__(self):
        self.base_url = "http://api.exchangeratesapi.io/v1"
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY", "your_api_key_here")
        self.cache_duration = timedelta(hours=1)  # 緩存1小時
        self._rate_cache = {}
        
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """獲取匯率，優先從緩存獲取"""
        
        # 如果是相同貨幣，直接返回1
        if from_currency == to_currency:
            return 1.0
            
        cache_key = f"{from_currency}_{to_currency}"
        
        # 檢查緩存
        if self._is_cache_valid(cache_key):
            return self._rate_cache[cache_key]["rate"]
        
        # 從API獲取匯率
        try:
            rate = await self._fetch_rate_from_api(from_currency, to_currency)
            if rate:
                self._update_cache(cache_key, rate)
                return rate
        except Exception as e:
            print(f"獲取匯率失敗: {e}")
            
        # 回退到緩存的舊數據（如果存在）
        if cache_key in self._rate_cache:
            print(f"使用過期的緩存匯率: {cache_key}")
            return self._rate_cache[cache_key]["rate"]
            
        return None
    
    async def _fetch_rate_from_api(self, from_currency: str, to_currency: str) -> Optional[float]:
        """從API獲取匯率"""
        
        # 使用免費的exchangerate.host作為備用（無需API key）
        backup_url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount=1"
        
        try:
            # 優先使用exchangeratesapi.io（需要API key）
            if self.api_key and self.api_key != "your_api_key_here":
                url = f"{self.base_url}/latest?access_key={self.api_key}&base={from_currency}&symbols={to_currency}"
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success") and to_currency in data.get("rates", {}):
                            return data["rates"][to_currency]
            
            # 備用方案：使用免費的exchangerate.host
            async with httpx.AsyncClient() as client:
                response = await client.get(backup_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return data.get("result")
                        
        except Exception as e:
            print(f"API請求失敗: {e}")
            
        return None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """檢查緩存是否有效"""
        if cache_key not in self._rate_cache:
            return False
            
        cache_time = self._rate_cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_duration
    
    def _update_cache(self, cache_key: str, rate: float):
        """更新緩存"""
        self._rate_cache[cache_key] = {
            "rate": rate,
            "timestamp": datetime.now()
        }
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """貨幣轉換"""
        rate = await self.get_exchange_rate(from_currency, to_currency)
        if rate is not None:
            return round(amount * rate, 2)
        return None
    
    def get_supported_currencies(self) -> Dict[str, str]:
        """獲取支援的貨幣列表"""
        return {
            "TWD": "台幣 (New Taiwan Dollar)",
            "USD": "美金 (US Dollar)"
        }
    
    async def get_usd_to_twd_rate(self) -> Optional[float]:
        """獲取USD到TWD的匯率（常用方法）"""
        return await self.get_exchange_rate("USD", "TWD")
    
    async def get_exchange_rates(self) -> Dict[str, float]:
        """獲取所有支援貨幣的匯率（相對於TWD）"""
        currencies = ["USD", "EUR", "JPY", "GBP", "KRW", "CNY"]
        rates = {"TWD": 1.0}  # TWD 作為基準
        
        for currency in currencies:
            try:
                # 由於我們要TWD為基準，需要先獲取TWD到其他貨幣的匯率，然後取倒數
                # 或者獲取其他貨幣到TWD的匯率
                rate = await self.get_exchange_rate(currency, "TWD")
                if rate:
                    rates[currency] = rate
                else:
                    # 如果獲取失敗，使用預設匯率
                    default_rates = {
                        "USD": 31.5, "EUR": 34.2, "JPY": 0.21, 
                        "GBP": 39.8, "KRW": 0.024, "CNY": 4.35
                    }
                    rates[currency] = default_rates.get(currency, 1.0)
            except Exception as e:
                print(f"獲取{currency}匯率失敗: {e}")
                # 使用預設匯率
                default_rates = {
                    "USD": 31.5, "EUR": 34.2, "JPY": 0.21, 
                    "GBP": 39.8, "KRW": 0.024, "CNY": 4.35
                }
                rates[currency] = default_rates.get(currency, 1.0)
        
        return rates

# 全局實例
exchange_rate_service = ExchangeRateService()