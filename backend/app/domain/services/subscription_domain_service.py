from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from app.models.subscription import Subscription, SubscriptionCycle
from app.domain.interfaces.services import IExchangeRateService

class SubscriptionDomainService:
    """訂閱領域服務 - 處理核心業務邏輯"""
    
    def __init__(self, exchange_rate_service: IExchangeRateService):
        self._exchange_rate_service = exchange_rate_service
    
    async def calculate_twd_price(self, original_price: float, currency: str) -> float:
        """計算台幣價格"""
        if currency == "TWD":
            return original_price
        
        return await self._exchange_rate_service.convert_currency(
            original_price, currency, "TWD"
        )
    
    def calculate_monthly_cost(self, subscription: Subscription) -> float:
        """計算月度成本"""
        if subscription.cycle == SubscriptionCycle.MONTHLY:
            return subscription.price
        elif subscription.cycle == SubscriptionCycle.QUARTERLY:
            return subscription.price / 3
        elif subscription.cycle == SubscriptionCycle.YEARLY:
            return subscription.price / 12
        else:
            raise ValueError(f"不支持的訂閱週期: {subscription.cycle}")
    
    def calculate_yearly_cost(self, subscription: Subscription) -> float:
        """計算年度成本"""
        if subscription.cycle == SubscriptionCycle.MONTHLY:
            return subscription.price * 12
        elif subscription.cycle == SubscriptionCycle.QUARTERLY:
            return subscription.price * 4
        elif subscription.cycle == SubscriptionCycle.YEARLY:
            return subscription.price
        else:
            raise ValueError(f"不支持的訂閱週期: {subscription.cycle}")
    
    def calculate_next_billing_date(self, subscription: Subscription) -> datetime:
        """計算下次計費日期"""
        if subscription.cycle == SubscriptionCycle.MONTHLY:
            return subscription.start_date + relativedelta(months=1)
        elif subscription.cycle == SubscriptionCycle.QUARTERLY:
            return subscription.start_date + relativedelta(months=3)
        elif subscription.cycle == SubscriptionCycle.YEARLY:
            return subscription.start_date + relativedelta(years=1)
        else:
            raise ValueError(f"不支持的訂閱週期: {subscription.cycle}")
    
    def is_due_soon(self, subscription: Subscription, days_ahead: int = 7) -> bool:
        """檢查訂閱是否即將到期"""
        next_billing = self.calculate_next_billing_date(subscription)
        warning_date = datetime.now() + timedelta(days=days_ahead)
        return next_billing <= warning_date
    
    def calculate_total_monthly_cost(self, subscriptions: List[Subscription]) -> float:
        """計算總月度成本"""
        return sum(self.calculate_monthly_cost(sub) for sub in subscriptions if sub.is_active)
    
    def calculate_total_yearly_cost(self, subscriptions: List[Subscription]) -> float:
        """計算總年度成本"""
        return sum(self.calculate_yearly_cost(sub) for sub in subscriptions if sub.is_active)
    
    def group_by_category(self, subscriptions: List[Subscription]) -> dict:
        """按類別分組訂閱"""
        grouped = {}
        for subscription in subscriptions:
            if subscription.is_active:
                category = subscription.category.value
                if category not in grouped:
                    grouped[category] = []
                grouped[category].append(subscription)
        return grouped
    
    def calculate_category_costs(self, subscriptions: List[Subscription]) -> dict:
        """計算各類別的月度成本"""
        grouped = self.group_by_category(subscriptions)
        category_costs = {}
        
        for category, subs in grouped.items():
            category_costs[category] = sum(self.calculate_monthly_cost(sub) for sub in subs)
        
        return category_costs
    
    async def validate_subscription_data(self, name: str, price: float, currency: str) -> dict:
        """驗證訂閱數據"""
        errors = []
        
        if not name or len(name.strip()) == 0:
            errors.append("訂閱名稱不能為空")
        
        if price <= 0:
            errors.append("價格必須大於0")
        
        if currency not in ["TWD", "USD", "EUR", "JPY", "GBP", "KRW", "CNY"]:
            errors.append("不支持的貨幣類型")
        
        # 檢查匯率是否可獲取（如果不是台幣）
        if currency != "TWD":
            try:
                await self._exchange_rate_service.get_exchange_rate(currency, "TWD")
            except Exception:
                errors.append(f"無法獲取 {currency} 到 TWD 的匯率")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }