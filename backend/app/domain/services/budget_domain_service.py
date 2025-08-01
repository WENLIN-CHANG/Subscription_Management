from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.models.budget import Budget
from app.models.subscription import Subscription
from app.domain.services.subscription_domain_service import SubscriptionDomainService

class BudgetDomainService:
    """預算領域服務 - 處理預算相關業務邏輯"""
    
    def __init__(self, subscription_service: SubscriptionDomainService):
        self._subscription_service = subscription_service
    
    def calculate_budget_usage(self, budget: Budget, subscriptions: List[Subscription]) -> Dict[str, Any]:
        """計算預算使用情況"""
        if not budget:
            return {
                "total_budget": 0,
                "used_amount": 0,
                "remaining_amount": 0,
                "usage_percentage": 0,
                "is_over_budget": False,
                "over_budget_amount": 0
            }
        
        total_monthly_cost = self._subscription_service.calculate_total_monthly_cost(subscriptions)
        remaining = budget.monthly_limit - total_monthly_cost
        usage_percentage = (total_monthly_cost / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0
        is_over_budget = total_monthly_cost > budget.monthly_limit
        over_budget_amount = max(0, total_monthly_cost - budget.monthly_limit)
        
        return {
            "total_budget": budget.monthly_limit,
            "used_amount": total_monthly_cost,
            "remaining_amount": remaining,
            "usage_percentage": round(usage_percentage, 2),
            "is_over_budget": is_over_budget,
            "over_budget_amount": over_budget_amount
        }
    
    def calculate_category_budget_usage(self, budget: Budget, subscriptions: List[Subscription]) -> Dict[str, Any]:
        """計算各類別的預算使用情況"""
        category_costs = self._subscription_service.calculate_category_costs(subscriptions)
        total_monthly_cost = sum(category_costs.values())
        
        result = {
            "total_budget": budget.monthly_limit if budget else 0,
            "total_used": total_monthly_cost,
            "categories": {}
        }
        
        for category, cost in category_costs.items():
            percentage = (cost / total_monthly_cost * 100) if total_monthly_cost > 0 else 0
            budget_percentage = (cost / budget.monthly_limit * 100) if budget and budget.monthly_limit > 0 else 0
            
            result["categories"][category] = {
                "cost": cost,
                "percentage_of_total": round(percentage, 2),
                "percentage_of_budget": round(budget_percentage, 2)
            }
        
        return result
    
    def get_budget_recommendations(self, budget: Budget, subscriptions: List[Subscription]) -> List[str]:
        """獲取預算建議"""
        recommendations = []
        
        if not budget:
            recommendations.append("建議設置月度預算限制以更好地管理訂閱支出")
            return recommendations
        
        usage_info = self.calculate_budget_usage(budget, subscriptions)
        
        if usage_info["is_over_budget"]:
            recommendations.append(f"當前支出超出預算 {usage_info['over_budget_amount']:.2f} 元，建議檢視並取消不必要的訂閱")
        
        if usage_info["usage_percentage"] > 90:
            recommendations.append("預算使用率超過90%，接近預算上限")
        elif usage_info["usage_percentage"] > 80:
            recommendations.append("預算使用率超過80%，建議注意支出控制")
        
        # 檢查是否有太多相同類別的訂閱
        category_usage = self.calculate_category_budget_usage(budget, subscriptions)
        for category, info in category_usage["categories"].items():
            if info["percentage_of_budget"] > 50:
                recommendations.append(f"「{category}」類別支出佔預算的{info['percentage_of_budget']:.1f}%，建議檢視是否有重複或不必要的訂閱")
        
        return recommendations
    
    def validate_budget_data(self, monthly_limit: float) -> Dict[str, Any]:
        """驗證預算數據"""
        errors = []
        
        if monthly_limit <= 0:
            errors.append("月度預算限制必須大於0")
        
        if monthly_limit > 1000000:  # 100萬台幣
            errors.append("月度預算限制不能超過1,000,000元")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def calculate_savings_potential(self, subscriptions: List[Subscription]) -> Dict[str, Any]:
        """計算潛在節省金額"""
        yearly_costs = []
        monthly_costs = []
        
        for subscription in subscriptions:
            if subscription.is_active:
                yearly_cost = self._subscription_service.calculate_yearly_cost(subscription)
                monthly_cost = self._subscription_service.calculate_monthly_cost(subscription)
                
                yearly_costs.append(yearly_cost)
                monthly_costs.append(monthly_cost)
        
        # 如果全部改為年付，可能的節省（假設年付有10%折扣）
        potential_yearly_total = sum(yearly_costs) * 0.9  # 假設年付9折
        current_yearly_total = sum(monthly_costs) * 12
        potential_savings = current_yearly_total - potential_yearly_total
        
        return {
            "current_yearly_cost": current_yearly_total,
            "potential_yearly_cost": potential_yearly_total,
            "potential_annual_savings": max(0, potential_savings),
            "savings_percentage": (potential_savings / current_yearly_total * 100) if current_yearly_total > 0 else 0
        }