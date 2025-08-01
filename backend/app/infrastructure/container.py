from typing import Dict, Type, Any, Optional, Callable
import inspect
from functools import wraps

class DIContainer:
    """依賴注入容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._transients: Dict[str, Type] = {}
        self._factories: Dict[str, Callable] = {}
    
    def register_singleton(self, interface: Type, implementation: Type):
        """註冊單例服務"""
        key = self._get_key(interface)
        self._singletons[key] = implementation
        return self
    
    def register_transient(self, interface: Type, implementation: Type):
        """註冊瞬態服務"""
        key = self._get_key(interface)
        self._transients[key] = implementation
        return self
    
    def register_factory(self, interface: Type, factory: Callable):
        """註冊工廠方法"""
        key = self._get_key(interface)
        self._factories[key] = factory
        return self
    
    def register_instance(self, interface: Type, instance: Any):
        """註冊實例"""
        key = self._get_key(interface)
        self._services[key] = instance
        return self
    
    def resolve(self, interface: Type) -> Any:
        """解析服務"""
        key = self._get_key(interface)
        
        # 檢查已註冊的實例
        if key in self._services:
            return self._services[key]
        
        # 檢查單例
        if key in self._singletons:
            if key not in self._services:
                self._services[key] = self._create_instance(self._singletons[key])
            return self._services[key]
        
        # 檢查瞬態
        if key in self._transients:
            return self._create_instance(self._transients[key])
        
        # 檢查工廠方法
        if key in self._factories:
            return self._factories[key]()
        
        # 嘗試自動解析
        if inspect.isclass(interface):
            return self._create_instance(interface)
        
        raise ValueError(f"無法解析服務: {interface}")
    
    def _get_key(self, interface: Type) -> str:
        """獲取服務鍵"""
        return f"{interface.__module__}.{interface.__name__}"
    
    def _create_instance(self, cls: Type) -> Any:
        """創建實例"""
        # 獲取構造函數參數
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.resolve(param.annotation)
                except ValueError:
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default
                    else:
                        raise ValueError(f"無法解析參數 {param_name} 的類型 {param.annotation}")
        
        return cls(**kwargs)
    
    def clear(self):
        """清空容器"""
        self._services.clear()
        self._singletons.clear()
        self._transients.clear()
        self._factories.clear()

def inject(container: DIContainer):
    """依賴注入裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 獲取函數簽名
            sig = inspect.signature(func)
            bound_args = sig.bind_partial(*args, **kwargs)
            
            # 解析未提供的參數
            for param_name, param in sig.parameters.items():
                if param_name not in bound_args.arguments:
                    if param.annotation != inspect.Parameter.empty:
                        try:
                            bound_args.arguments[param_name] = container.resolve(param.annotation)
                        except ValueError:
                            if param.default != inspect.Parameter.empty:
                                bound_args.arguments[param_name] = param.default
                            else:
                                raise
            
            return func(**bound_args.arguments)
        return wrapper
    return decorator

# 全局容器實例
container = DIContainer()

def configure_container():
    """配置依賴注入容器"""
    from app.domain.interfaces.repositories import IUnitOfWork
    from app.domain.interfaces.services import IExchangeRateService
    from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
    from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
    from app.domain.services.subscription_domain_service import SubscriptionDomainService
    from app.domain.services.budget_domain_service import BudgetDomainService
    from app.application.services.subscription_application_service import SubscriptionApplicationService
    from app.application.services.budget_application_service import BudgetApplicationService
    
    # 註冊基礎設施服務
    container.register_transient(IUnitOfWork, SQLAlchemyUnitOfWork)
    container.register_singleton(IExchangeRateService, ExchangeRateServiceImpl)
    
    # 註冊領域服務
    container.register_singleton(SubscriptionDomainService, SubscriptionDomainService)
    container.register_singleton(BudgetDomainService, BudgetDomainService)
    
    # 註冊應用服務
    container.register_transient(SubscriptionApplicationService, SubscriptionApplicationService)
    container.register_transient(BudgetApplicationService, BudgetApplicationService)
    
    return container