"""
依賴注入容器測試

測試 DI 容器的功能：
- 服務註冊 (單例、瞬態、工廠、實例)
- 服務解析
- 依賴自動注入
- 循環依賴檢測
- 容器配置
"""

import pytest
from unittest.mock import Mock
from typing import Protocol

from app.infrastructure.container import DIContainer, inject, configure_container


# 測試用的接口和類
class ITestService(Protocol):
    def get_value(self) -> str:
        pass

class TestService:
    def get_value(self) -> str:
        return "TestService"

class IDependency(Protocol):
    def get_name(self) -> str:
        pass

class Dependency:
    def get_name(self) -> str:
        return "Dependency"

class ServiceWithDependency:
    def __init__(self, dependency: IDependency):
        self.dependency = dependency
    
    def get_info(self) -> str:
        return f"Service with {self.dependency.get_name()}"

class ServiceWithOptionalDependency:
    def __init__(self, dependency: IDependency = None):
        self.dependency = dependency
    
    def get_info(self) -> str:
        if self.dependency:
            return f"Service with {self.dependency.get_name()}"
        return "Service without dependency"

class ServiceWithMultipleDependencies:
    def __init__(self, service: ITestService, dependency: IDependency):
        self.service = service
        self.dependency = dependency
    
    def get_combined_info(self) -> str:
        return f"{self.service.get_value()} and {self.dependency.get_name()}"


class TestDIContainer:
    """DI 容器測試類"""

    @pytest.fixture
    def container(self):
        """創建新的容器實例"""
        return DIContainer()

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestServiceRegistration:
        """服務註冊測試"""

        def test_register_singleton(self, container):
            """測試註冊單例服務"""
            container.register_singleton(ITestService, TestService)
            
            # 解析兩次應該返回同一個實例
            instance1 = container.resolve(ITestService)
            instance2 = container.resolve(ITestService)
            
            assert isinstance(instance1, TestService)
            assert instance1 is instance2  # 應該是同一個實例

        def test_register_transient(self, container):
            """測試註冊瞬態服務"""
            container.register_transient(ITestService, TestService)
            
            # 解析兩次應該返回不同的實例
            instance1 = container.resolve(ITestService)
            instance2 = container.resolve(ITestService)
            
            assert isinstance(instance1, TestService)
            assert isinstance(instance2, TestService)
            assert instance1 is not instance2  # 應該是不同的實例

        def test_register_instance(self, container):
            """測試註冊現有實例"""
            test_instance = TestService()
            container.register_instance(ITestService, test_instance)
            
            resolved_instance = container.resolve(ITestService)
            
            assert resolved_instance is test_instance

        def test_register_factory(self, container):
            """測試註冊工廠方法"""
            def test_factory():
                service = TestService()
                service.custom_property = "factory_created"
                return service
            
            container.register_factory(ITestService, test_factory)
            
            instance = container.resolve(ITestService)
            
            assert isinstance(instance, TestService)
            assert hasattr(instance, 'custom_property')
            assert instance.custom_property == "factory_created"

        def test_chained_registration(self, container):
            """測試鏈式註冊"""
            result = (container
                     .register_singleton(ITestService, TestService)
                     .register_transient(IDependency, Dependency))
            
            assert result is container
            
            # 驗證兩個服務都已註冊
            service = container.resolve(ITestService)
            dependency = container.resolve(IDependency)
            
            assert isinstance(service, TestService)
            assert isinstance(dependency, Dependency)

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestServiceResolution:
        """服務解析測試"""

        def test_resolve_registered_service(self, container):
            """測試解析已註冊的服務"""
            container.register_singleton(ITestService, TestService)
            
            service = container.resolve(ITestService)
            
            assert isinstance(service, TestService)
            assert service.get_value() == "TestService"

        def test_resolve_unregistered_class(self, container):
            """測試解析未註冊的類（自動解析）"""
            service = container.resolve(TestService)
            
            assert isinstance(service, TestService)
            assert service.get_value() == "TestService"

        def test_resolve_with_dependencies(self, container):
            """測試解析帶依賴的服務"""
            container.register_singleton(IDependency, Dependency)
            
            service = container.resolve(ServiceWithDependency)
            
            assert isinstance(service, ServiceWithDependency)
            assert isinstance(service.dependency, Dependency)
            assert service.get_info() == "Service with Dependency"

        def test_resolve_with_multiple_dependencies(self, container):
            """測試解析帶多個依賴的服務"""
            container.register_singleton(ITestService, TestService)
            container.register_singleton(IDependency, Dependency)
            
            service = container.resolve(ServiceWithMultipleDependencies)
            
            assert isinstance(service, ServiceWithMultipleDependencies)
            assert service.get_combined_info() == "TestService and Dependency"

        def test_resolve_with_optional_dependency_present(self, container):
            """測試解析可選依賴存在時"""
            container.register_singleton(IDependency, Dependency)
            
            service = container.resolve(ServiceWithOptionalDependency)
            
            assert service.get_info() == "Service with Dependency"

        def test_resolve_with_optional_dependency_missing(self, container):
            """測試解析可選依賴缺失時"""
            service = container.resolve(ServiceWithOptionalDependency)
            
            assert service.get_info() == "Service without dependency"

        def test_resolve_nonexistent_service(self, container):
            """測試解析不存在的服務"""
            with pytest.raises(ValueError, match="無法解析服務"):
                container.resolve(ITestService)  # 接口無法直接實例化

        def test_resolve_missing_required_dependency(self, container):
            """測試解析缺少必需依賴的服務"""
            with pytest.raises(ValueError, match="無法解析參數"):
                container.resolve(ServiceWithDependency)

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestServiceLifecycle:
        """服務生命週期測試"""

        def test_singleton_lifecycle(self, container):
            """測試單例服務生命週期"""
            container.register_singleton(ITestService, TestService)
            
            # 多次解析應該返回同一實例
            instances = [container.resolve(ITestService) for _ in range(5)]
            
            first_instance = instances[0]
            for instance in instances[1:]:
                assert instance is first_instance

        def test_transient_lifecycle(self, container):
            """測試瞬態服務生命週期"""
            container.register_transient(ITestService, TestService)
            
            # 多次解析應該返回不同實例
            instances = [container.resolve(ITestService) for _ in range(5)]
            
            for i, instance1 in enumerate(instances):
                for j, instance2 in enumerate(instances):
                    if i != j:
                        assert instance1 is not instance2

        def test_factory_lifecycle(self, container):
            """測試工廠方法生命週期"""
            call_count = 0
            
            def counting_factory():
                nonlocal call_count
                call_count += 1
                service = TestService()
                service.call_number = call_count
                return service
            
            container.register_factory(ITestService, counting_factory)
            
            # 每次解析都應該調用工廠方法
            instance1 = container.resolve(ITestService)
            instance2 = container.resolve(ITestService)
            
            assert instance1.call_number == 1
            assert instance2.call_number == 2
            assert call_count == 2

        def test_mixed_lifecycles(self, container):
            """測試混合生命週期"""
            container.register_singleton(IDependency, Dependency)
            container.register_transient(ServiceWithDependency, ServiceWithDependency)
            
            # 依賴應該是單例，但服務應該是瞬態
            service1 = container.resolve(ServiceWithDependency)
            service2 = container.resolve(ServiceWithDependency)
            
            # 服務實例不同
            assert service1 is not service2
            
            # 但依賴實例相同
            assert service1.dependency is service2.dependency

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestContainerManagement:
        """容器管理測試"""

        def test_clear_container(self, container):
            """測試清空容器"""
            container.register_singleton(ITestService, TestService)
            container.register_transient(IDependency, Dependency)
            
            # 解析一個單例以確保它被緩存
            container.resolve(ITestService)
            
            container.clear()
            
            # 清空後應該無法解析
            with pytest.raises(ValueError):
                container.resolve(ITestService)

        def test_get_key_generation(self, container):
            """測試服務鍵生成"""
            key1 = container._get_key(TestService)
            key2 = container._get_key(TestService)
            
            assert key1 == key2
            assert isinstance(key1, str)
            assert "TestService" in key1

        def test_instance_creation(self, container):
            """測試實例創建邏輯"""
            container.register_singleton(IDependency, Dependency)
            
            # 直接測試實例創建方法
            instance = container._create_instance(ServiceWithDependency)
            
            assert isinstance(instance, ServiceWithDependency)
            assert isinstance(instance.dependency, Dependency)

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestInjectDecorator:
        """依賴注入裝飾器測試"""

        def test_inject_decorator_basic(self, container):
            """測試基本依賴注入裝飾器"""
            container.register_singleton(ITestService, TestService)
            
            @inject(container)
            def test_function(service: ITestService):
                return service.get_value()
            
            result = test_function()
            assert result == "TestService"

        def test_inject_decorator_with_args(self, container):
            """測試帶參數的依賴注入"""
            container.register_singleton(ITestService, TestService)
            
            @inject(container)
            def test_function(prefix: str, service: ITestService):
                return f"{prefix}: {service.get_value()}"
            
            result = test_function("Result")
            assert result == "Result: TestService"

        def test_inject_decorator_with_explicit_args(self, container):
            """測試顯式傳遞參數時的行為"""
            container.register_singleton(ITestService, TestService)
            mock_service = Mock()
            mock_service.get_value.return_value = "MockService"
            
            @inject(container)
            def test_function(service: ITestService):
                return service.get_value()
            
            # 顯式傳遞參數應該覆蓋容器解析
            result = test_function(service=mock_service)
            assert result == "MockService"

        def test_inject_decorator_with_defaults(self, container):
            """測試帶默認值的依賴注入"""
            @inject(container)
            def test_function(service: ITestService = None):
                return service.get_value() if service else "No service"
            
            # 無法解析時應該使用默認值
            result = test_function()
            assert result == "No service"

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestErrorHandling:
        """錯誤處理測試"""

        def test_circular_dependency_detection(self, container):
            """測試循環依賴檢測"""
            # 創建循環依賴的類
            class ServiceA:
                def __init__(self, service_b: 'ServiceB'):
                    self.service_b = service_b
            
            class ServiceB:
                def __init__(self, service_a: ServiceA):
                    self.service_a = service_a
            
            container.register_singleton(ServiceA, ServiceA)
            container.register_singleton(ServiceB, ServiceB)
            
            # 應該在解析時檢測到循環依賴
            with pytest.raises(RecursionError):
                container.resolve(ServiceA)

        def test_invalid_service_type(self, container):
            """測試無效服務類型"""
            with pytest.raises(ValueError, match="無法解析服務"):
                container.resolve("not_a_type")

        def test_missing_type_annotation(self, container):
            """測試缺少類型注解的參數"""
            class ServiceWithoutAnnotation:
                def __init__(self, service):  # 沒有類型注解
                    self.service = service
            
            with pytest.raises(ValueError, match="無法解析參數"):
                container.resolve(ServiceWithoutAnnotation)

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestContainerConfiguration:
        """容器配置測試"""

        def test_configure_container(self):
            """測試容器配置函數"""
            configured_container = configure_container()
            
            assert configured_container is not None
            
            # 測試是否能解析已配置的服務
            from app.domain.interfaces.services import IExchangeRateService
            from app.domain.services.subscription_domain_service import SubscriptionDomainService
            
            exchange_service = configured_container.resolve(IExchangeRateService)
            domain_service = configured_container.resolve(SubscriptionDomainService)
            
            assert exchange_service is not None
            assert domain_service is not None

        def test_configured_services_are_properly_wired(self):
            """測試配置的服務是否正確連接"""
            configured_container = configure_container()
            
            from app.application.services.subscription_application_service import SubscriptionApplicationService
            
            app_service = configured_container.resolve(SubscriptionApplicationService)
            
            assert app_service is not None
            assert hasattr(app_service, '_uow')
            assert hasattr(app_service, '_domain_service')

        def test_singleton_services_in_configuration(self):
            """測試配置中的單例服務"""
            configured_container = configure_container()
            
            from app.domain.services.subscription_domain_service import SubscriptionDomainService
            
            # 解析兩次應該返回同一實例
            service1 = configured_container.resolve(SubscriptionDomainService)
            service2 = configured_container.resolve(SubscriptionDomainService)
            
            assert service1 is service2

        def test_transient_services_in_configuration(self):
            """測試配置中的瞬態服務"""
            configured_container = configure_container()
            
            from app.application.services.subscription_application_service import SubscriptionApplicationService
            
            # 解析兩次應該返回不同實例
            service1 = configured_container.resolve(SubscriptionApplicationService)
            service2 = configured_container.resolve(SubscriptionApplicationService)
            
            assert service1 is not service2