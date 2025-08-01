#!/usr/bin/env python3
"""
簡單的基本功能測試
用於快速驗證新架構的核心組件是否能正常工作
"""

import sys
import os
import asyncio
from decimal import Decimal

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """測試所有重要模塊是否能正常導入"""
    print("🔍 測試模塊導入...")
    
    try:
        # 測試領域層導入
        from app.domain.services.subscription_domain_service import SubscriptionDomainService
        from app.domain.services.budget_domain_service import BudgetDomainService
        print("✅ 領域服務導入成功")
        
        # 測試應用層導入
        from app.application.services.subscription_application_service import SubscriptionApplicationService
        from app.application.services.budget_application_service import BudgetApplicationService
        print("✅ 應用服務導入成功")
        
        # 測試基礎設施層導入
        from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
        from app.infrastructure.container import DIContainer
        print("✅ 基礎設施服務導入成功")
        
        # 測試共通組件導入
        from app.common.responses import ApiResponse
        from app.common.exceptions import ApplicationException
        print("✅ 共通組件導入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        return False

def test_exchange_rate_service():
    """測試匯率服務"""
    print("\n💱 測試匯率服務...")
    
    try:
        from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
        
        service = ExchangeRateServiceImpl()
        
        # 測試同幣種匯率
        async def test_same_currency():
            rate = await service.get_exchange_rate("TWD", "TWD")
            assert rate == Decimal("1.0"), f"同幣種匯率應為1.0，實際為{rate}"
            print("✅ 同幣種匯率測試通過")
        
        # 測試貨幣轉換
        async def test_currency_conversion():
            amount = await service.convert_currency(100, "TWD", "TWD")
            assert amount == 100.0, f"同幣種轉換應相等，實際為{amount}"
            print("✅ 同幣種轉換測試通過")
        
        # 測試支持貨幣列表
        async def test_supported_currencies():
            currencies = await service.get_supported_currencies()
            assert isinstance(currencies, dict), "支持貨幣應為字典格式"
            assert "TWD" in currencies, "應支持TWD"
            assert "USD" in currencies, "應支持USD"
            print(f"✅ 支持貨幣測試通過，共支持{len(currencies)}種貨幣")
        
        # 運行異步測試
        asyncio.run(test_same_currency())
        asyncio.run(test_currency_conversion())
        asyncio.run(test_supported_currencies())
        
        return True
        
    except Exception as e:
        print(f"❌ 匯率服務測試失敗: {e}")
        return False

def test_domain_services():
    """測試領域服務基本功能"""
    print("\n🏗️ 測試領域服務...")
    
    try:
        from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
        from app.domain.services.subscription_domain_service import SubscriptionDomainService
        from app.domain.services.budget_domain_service import BudgetDomainService
        
        # 創建服務實例
        exchange_service = ExchangeRateServiceImpl()
        subscription_service = SubscriptionDomainService(exchange_service)
        budget_service = BudgetDomainService(subscription_service)
        
        print("✅ 領域服務實例化成功")
        
        # 測試服務方法是否存在
        assert hasattr(subscription_service, 'calculate_monthly_cost'), "缺少calculate_monthly_cost方法"
        assert hasattr(subscription_service, 'calculate_yearly_cost'), "缺少calculate_yearly_cost方法"
        assert hasattr(budget_service, 'calculate_budget_usage'), "缺少calculate_budget_usage方法"
        
        print("✅ 領域服務方法檢查通過")
        
        return True
        
    except Exception as e:
        print(f"❌ 領域服務測試失敗: {e}")
        return False

def test_response_format():
    """測試統一響應格式"""
    print("\n📝 測試響應格式...")
    
    try:
        from app.common.responses import ApiResponse
        
        # 測試成功響應
        success_response = ApiResponse.success(
            data={"test": "data"},
            message="測試成功"
        )
        
        assert success_response.status == "success"
        assert success_response.message == "測試成功"
        assert success_response.data == {"test": "data"}
        print("✅ 成功響應格式測試通過")
        
        # 測試錯誤響應
        error_response = ApiResponse.error(
            message="測試錯誤",
            errors=["錯誤1", "錯誤2"]
        )
        
        assert error_response.status == "error"
        assert error_response.message == "測試錯誤"
        assert error_response.errors == ["錯誤1", "錯誤2"]
        print("✅ 錯誤響應格式測試通過")
        
        return True
        
    except Exception as e:
        print(f"❌ 響應格式測試失敗: {e}")
        return False

def test_dependency_injection():
    """測試依賴注入容器"""
    print("\n🔧 測試依賴注入容器...")
    
    try:
        from app.infrastructure.container import DIContainer
        
        container = DIContainer()
        
        # 測試基本注冊和解析
        class TestService:
            def __init__(self):
                self.name = "test_service"
        
        class TestInterface:
            pass
        
        container.register_singleton(TestInterface, TestService)
        resolved = container.resolve(TestInterface)
        
        assert isinstance(resolved, TestService)
        assert resolved.name == "test_service"
        print("✅ 依賴注入基本功能測試通過")
        
        return True
        
    except Exception as e:
        print(f"❌ 依賴注入測試失敗: {e}")
        return False

def main():
    """運行所有基本測試"""
    print("🚀 開始快速測試新架構...\n")
    
    test_results = []
    
    # 運行所有測試
    test_results.append(("模塊導入", test_imports()))
    test_results.append(("匯率服務", test_exchange_rate_service()))
    test_results.append(("領域服務", test_domain_services()))
    test_results.append(("響應格式", test_response_format()))
    test_results.append(("依賴注入", test_dependency_injection()))
    
    # 統計結果
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"\n📊 測試結果總結:")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:20} {status}")
    
    print("=" * 50)
    print(f"總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有基本功能測試都通過了！新架構運行正常。")
        return True
    else:
        print("⚠️  部分測試失敗，需要檢查架構配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)