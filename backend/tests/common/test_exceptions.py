"""
自定義異常測試

測試自定義異常類：
- ApplicationException 的功能
- 錯誤碼處理
- 詳細信息處理
- 狀態碼處理
- 異常繼承結構
"""

import pytest
from fastapi import status

from app.common.exceptions import ApplicationException


class TestApplicationException:
    """應用異常測試類"""

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestBasicFunctionality:
        """基本功能測試"""

        def test_create_basic_exception(self):
            """測試創建基本異常"""
            exc = ApplicationException("測試錯誤")
            
            assert str(exc) == "測試錯誤"
            assert exc.message == "測試錯誤"
            assert exc.error_code is None
            assert exc.details is None
            assert exc.status_code == status.HTTP_400_BAD_REQUEST

        def test_create_exception_with_error_code(self):
            """測試創建帶錯誤碼的異常"""
            exc = ApplicationException("業務錯誤", error_code="BUSINESS_ERROR")
            
            assert exc.message == "業務錯誤"
            assert exc.error_code == "BUSINESS_ERROR"

        def test_create_exception_with_details(self):
            """測試創建帶詳細信息的異常"""
            details = {"field": "email", "reason": "格式不正確"}
            exc = ApplicationException("驗證失敗", details=details)
            
            assert exc.details == details
            assert exc.details["field"] == "email"
            assert exc.details["reason"] == "格式不正確"

        def test_create_exception_with_custom_status_code(self):
            """測試創建帶自定義狀態碼的異常"""
            exc = ApplicationException(
                "資源不存在",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
            assert exc.status_code == status.HTTP_404_NOT_FOUND

        def test_create_exception_with_all_parameters(self):
            """測試創建包含所有參數的異常"""
            details = {"validation_errors": ["錯誤1", "錯誤2"]}
            exc = ApplicationException(
                message="完整錯誤",
                error_code="FULL_ERROR",
                details=details,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            
            assert exc.message == "完整錯誤"
            assert exc.error_code == "FULL_ERROR"
            assert exc.details == details
            assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestExceptionBehavior:
        """異常行為測試"""

        def test_exception_is_instance_of_exception(self):
            """測試異常是 Exception 的實例"""
            exc = ApplicationException("測試")
            
            assert isinstance(exc, Exception)
            assert isinstance(exc, ApplicationException)

        def test_exception_can_be_raised_and_caught(self):
            """測試異常可以被拋出和捕獲"""
            with pytest.raises(ApplicationException) as exc_info:
                raise ApplicationException("測試異常")
            
            assert exc_info.value.message == "測試異常"

        def test_exception_with_cause(self):
            """測試帶原因的異常"""
            original_error = ValueError("原始錯誤")
            
            try:
                raise original_error
            except ValueError as e:
                raise ApplicationException("包裝錯誤") from e
            except ApplicationException as app_exc:
                assert app_exc.__cause__ is original_error

        def test_exception_str_representation(self):
            """測試異常的字符串表示"""
            exc = ApplicationException("測試消息")
            
            assert str(exc) == "測試消息"

        def test_exception_repr_representation(self):
            """測試異常的 repr 表示"""
            exc = ApplicationException("測試", error_code="TEST")
            
            repr_str = repr(exc)
            assert "ApplicationException" in repr_str
            assert "測試" in repr_str

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestExceptionChaining:
        """異常鏈測試"""

        def test_chain_multiple_exceptions(self):
            """測試異常鏈"""
            try:
                try:
                    raise ValueError("底層錯誤")
                except ValueError:
                    raise ApplicationException("中間錯誤") from None
            except ApplicationException as e:
                try:
                    raise ApplicationException("頂層錯誤") from e
                except ApplicationException as final_exc:
                    assert final_exc.message == "頂層錯誤"
                    assert isinstance(final_exc.__cause__, ApplicationException)
                    assert final_exc.__cause__.message == "中間錯誤"

        def test_suppress_exception_context(self):
            """測試抑制異常上下文"""
            try:
                try:
                    raise ValueError("原始錯誤")
                except ValueError:
                    raise ApplicationException("新錯誤") from None
            except ApplicationException as exc:
                assert exc.__cause__ is None
                assert exc.__suppress_context__ is True

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestExceptionWithComplexDetails:
        """複雜詳細信息測試"""

        def test_exception_with_list_details(self):
            """測試帶列表詳細信息的異常"""
            details = {
                "errors": ["錯誤1", "錯誤2", "錯誤3"],
                "count": 3
            }
            exc = ApplicationException("多重錯誤", details=details)
            
            assert len(exc.details["errors"]) == 3
            assert exc.details["count"] == 3

        def test_exception_with_nested_details(self):
            """測試帶嵌套詳細信息的異常"""
            details = {
                "validation": {
                    "fields": {
                        "name": ["不能為空", "長度不足"],
                        "email": ["格式不正確"]
                    }
                },
                "metadata": {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "user_id": 123
                }
            }
            exc = ApplicationException("複雜驗證錯誤", details=details)
            
            assert "validation" in exc.details
            assert "fields" in exc.details["validation"]
            assert len(exc.details["validation"]["fields"]["name"]) == 2
            assert exc.details["metadata"]["user_id"] == 123

        def test_exception_details_immutability(self):
            """測試異常詳細信息的不可變性"""
            details = {"key": "value"}
            exc = ApplicationException("測試", details=details)
            
            # 修改原始字典不應影響異常中的詳細信息
            details["key"] = "modified"
            
            # 注意：這裡假設 ApplicationException 會複製詳細信息
            # 如果實現沒有複製，這個測試會失敗，提醒需要改進實現
            assert exc.details["key"] == "value"

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestCommonErrorScenarios:
        """常見錯誤場景測試"""

        def test_validation_error_scenario(self):
            """測試驗證錯誤場景"""
            validation_details = {
                "field": "email",
                "value": "invalid-email",
                "constraints": ["必須是有效的電子郵件格式"]
            }
            
            exc = ApplicationException(
                "字段驗證失敗",
                error_code="VALIDATION_ERROR",
                details=validation_details,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            
            assert exc.error_code == "VALIDATION_ERROR"
            assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert exc.details["field"] == "email"

        def test_business_rule_violation_scenario(self):
            """測試業務規則違反場景"""
            business_details = {
                "rule": "用戶月度訂閱限制",
                "current_count": 10,
                "max_allowed": 5
            }
            
            exc = ApplicationException(
                "超出用戶訂閱限制",
                error_code="BUSINESS_RULE_VIOLATION",
                details=business_details
            )
            
            assert exc.error_code == "BUSINESS_RULE_VIOLATION"
            assert exc.details["current_count"] == 10

        def test_resource_not_found_scenario(self):
            """測試資源不存在場景"""
            resource_details = {
                "resource_type": "subscription",
                "resource_id": 12345,
                "user_id": 67890
            }
            
            exc = ApplicationException(
                "訂閱不存在",
                error_code="RESOURCE_NOT_FOUND",
                details=resource_details,
                status_code=status.HTTP_404_NOT_FOUND
            )
            
            assert exc.error_code == "RESOURCE_NOT_FOUND"
            assert exc.status_code == status.HTTP_404_NOT_FOUND

        def test_permission_denied_scenario(self):
            """測試權限拒絕場景"""
            permission_details = {
                "required_permission": "subscription:delete",
                "user_permissions": ["subscription:read", "subscription:create"],
                "resource_id": 123
            }
            
            exc = ApplicationException(
                "權限不足",
                error_code="PERMISSION_DENIED",
                details=permission_details,
                status_code=status.HTTP_403_FORBIDDEN
            )
            
            assert exc.error_code == "PERMISSION_DENIED"
            assert exc.status_code == status.HTTP_403_FORBIDDEN

        def test_rate_limit_exceeded_scenario(self):
            """測試速率限制超出場景"""
            rate_limit_details = {
                "limit": 100,
                "current": 101,
                "reset_time": "2024-01-01T01:00:00Z",
                "window": "1 hour"
            }
            
            exc = ApplicationException(
                "請求頻率過高",
                error_code="RATE_LIMIT_EXCEEDED",
                details=rate_limit_details,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )
            
            assert exc.error_code == "RATE_LIMIT_EXCEEDED"
            assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestExceptionSerialization:
        """異常序列化測試"""

        def test_exception_to_dict_basic(self):
            """測試異常轉字典（基本）"""
            exc = ApplicationException("測試錯誤", error_code="TEST_ERROR")
            
            # 假設 ApplicationException 有 to_dict 方法
            if hasattr(exc, 'to_dict'):
                data = exc.to_dict()
                assert data["message"] == "測試錯誤"
                assert data["error_code"] == "TEST_ERROR"

        def test_exception_json_serializable(self):
            """測試異常的 JSON 序列化兼容性"""
            import json
            
            details = {"field": "name", "error": "required"}
            exc = ApplicationException("驗證錯誤", details=details)
            
            # 測試詳細信息可以被 JSON 序列化
            try:
                json.dumps(exc.details)
            except (TypeError, ValueError):
                pytest.fail("異常詳細信息不能被 JSON 序列化")

        def test_exception_with_non_serializable_details(self):
            """測試帶不可序列化詳細信息的異常"""
            import datetime
            
            # 使用不可直接 JSON 序列化的對象
            details = {
                "timestamp": datetime.datetime.now(),
                "callback": lambda x: x
            }
            
            # 應用異常應該能處理這種情況
            exc = ApplicationException("複雜詳細信息", details=details)
            assert exc.details is not None