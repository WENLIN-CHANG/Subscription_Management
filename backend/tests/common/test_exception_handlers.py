"""
異常處理器測試

測試全局異常處理：
- 應用異常處理
- HTTP 異常處理
- 驗證異常處理
- SQLAlchemy 異常處理
- 通用異常處理
- 異常響應格式
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from starlette.responses import JSONResponse

from app.common.exceptions import ApplicationException
from app.common.exception_handlers import (
    application_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    pydantic_validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)


class TestExceptionHandlers:
    """異常處理器測試類"""

    @pytest.fixture
    def mock_request(self):
        """模擬請求對象"""
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.method = "POST"
        return request

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestApplicationExceptionHandler:
        """應用異常處理器測試"""

        def test_handle_application_exception(self, mock_request):
            """測試處理應用異常"""
            exc = ApplicationException("應用業務錯誤", error_code="BUSINESS_ERROR")
            
            response = application_exception_handler(mock_request, exc)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            # 檢查響應內容
            content = response.body.decode()
            assert "應用業務錯誤" in content
            assert "BUSINESS_ERROR" in content
            assert "success" in content
            assert "false" in content.lower()

        def test_handle_application_exception_with_details(self, mock_request):
            """測試處理帶詳細信息的應用異常"""
            details = {"field": "name", "error": "不能為空"}
            exc = ApplicationException(
                "驗證失敗", 
                error_code="VALIDATION_ERROR",
                details=details
            )
            
            response = application_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            content = response.body.decode()
            assert "驗證失敗" in content
            assert "VALIDATION_ERROR" in content
            assert "field" in content
            assert "不能為空" in content

        def test_handle_application_exception_with_custom_status_code(self, mock_request):
            """測試處理帶自定義狀態碼的應用異常"""
            exc = ApplicationException(
                "資源不存在", 
                error_code="NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
            response = application_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestHTTPExceptionHandler:
        """HTTP 異常處理器測試"""

        def test_handle_http_exception_404(self, mock_request):
            """測試處理 404 HTTP 異常"""
            exc = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="資源不存在"
            )
            
            response = http_exception_handler(mock_request, exc)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_404_NOT_FOUND
            
            content = response.body.decode()
            assert "資源不存在" in content
            assert "success" in content
            assert "false" in content.lower()

        def test_handle_http_exception_401(self, mock_request):
            """測試處理 401 HTTP 異常"""
            exc = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未授權訪問",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
            response = http_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.headers.get("WWW-Authenticate") == "Bearer"

        def test_handle_http_exception_with_dict_detail(self, mock_request):
            """測試處理帶字典詳情的 HTTP 異常"""
            detail = {"errors": ["錯誤1", "錯誤2"], "code": "MULTIPLE_ERRORS"}
            exc = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )
            
            response = http_exception_handler(mock_request, exc)
            
            content = response.body.decode()
            assert "錯誤1" in content
            assert "錯誤2" in content
            assert "MULTIPLE_ERRORS" in content

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestValidationExceptionHandler:
        """驗證異常處理器測試"""

        def test_handle_validation_error(self, mock_request):
            """測試處理請求驗證錯誤"""
            # 模擬驗證錯誤
            from pydantic import BaseModel, validator
            
            class TestModel(BaseModel):
                name: str
                age: int
                
                @validator('age')
                def validate_age(cls, v):
                    if v < 0:
                        raise ValueError('年齡不能為負數')
                    return v
            
            try:
                TestModel(name="", age=-1)
            except ValidationError as validation_error:
                # 創建 RequestValidationError
                exc = RequestValidationError([validation_error])
                
                response = validation_exception_handler(mock_request, exc)
                
                assert isinstance(response, JSONResponse)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                
                content = response.body.decode()
                assert "驗證錯誤" in content
                assert "success" in content
                assert "false" in content.lower()

        def test_handle_empty_validation_error(self, mock_request):
            """測試處理空驗證錯誤"""
            exc = RequestValidationError([])
            
            response = validation_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            content = response.body.decode()
            assert "請求數據格式錯誤" in content

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestPydanticValidationExceptionHandler:
        """Pydantic 驗證異常處理器測試"""

        def test_handle_pydantic_validation_error(self, mock_request):
            """測試處理 Pydantic 驗證錯誤"""
            from pydantic import BaseModel, Field
            
            class TestModel(BaseModel):
                name: str = Field(..., min_length=1)
                email: str = Field(..., regex=r'^[^@]+@[^@]+\\.[^@]+$')
            
            try:
                TestModel(name="", email="invalid-email")
            except ValidationError as exc:
                response = pydantic_validation_exception_handler(mock_request, exc)
                
                assert isinstance(response, JSONResponse)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                
                content = response.body.decode()
                assert "數據驗證失敗" in content
                assert "success" in content
                assert "false" in content.lower()

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestSQLAlchemyExceptionHandler:
        """SQLAlchemy 異常處理器測試"""

        def test_handle_integrity_error(self, mock_request):
            """測試處理完整性約束錯誤"""
            exc = IntegrityError(
                statement="INSERT INTO users...",
                params={},
                orig=Mock()
            )
            exc.orig.args = ("UNIQUE constraint failed: users.email",)
            
            response = sqlalchemy_exception_handler(mock_request, exc)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_409_CONFLICT
            
            content = response.body.decode()
            assert "數據完整性約束違反" in content
            assert "success" in content
            assert "false" in content.lower()

        def test_handle_operational_error(self, mock_request):
            """測試處理操作錯誤"""
            exc = OperationalError(
                statement="SELECT * FROM users",
                params={},
                orig=Mock()
            )
            exc.orig.args = ("database is locked",)
            
            response = sqlalchemy_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            
            content = response.body.decode()
            assert "數據庫操作失敗" in content

        def test_handle_generic_sqlalchemy_error(self, mock_request):
            """測試處理通用 SQLAlchemy 錯誤"""
            exc = SQLAlchemyError("Generic database error")
            
            response = sqlalchemy_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            
            content = response.body.decode()
            assert "數據庫錯誤" in content

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestGenericExceptionHandler:
        """通用異常處理器測試"""

        def test_handle_generic_exception(self, mock_request):
            """測試處理通用異常"""
            exc = Exception("意外錯誤")
            
            with patch('app.common.exception_handlers.app_logger') as mock_logger:
                response = generic_exception_handler(mock_request, exc)
                
                # 驗證日誌記錄
                mock_logger.error.assert_called_once()
                
                assert isinstance(response, JSONResponse)
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                
                content = response.body.decode()
                assert "內部服務器錯誤" in content
                assert "success" in content
                assert "false" in content.lower()

        def test_handle_value_error(self, mock_request):
            """測試處理 ValueError"""
            exc = ValueError("無效的參數值")
            
            response = generic_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        def test_handle_key_error(self, mock_request):
            """測試處理 KeyError"""
            exc = KeyError("missing_key")
            
            response = generic_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestResponseFormat:
        """響應格式測試"""

        def test_unified_error_response_format(self, mock_request):
            """測試統一錯誤響應格式"""
            exc = ApplicationException("測試錯誤")
            
            response = application_exception_handler(mock_request, exc)
            
            content = response.body.decode()
            import json
            data = json.loads(content)
            
            # 驗證響應格式
            assert "success" in data
            assert "message" in data
            assert "timestamp" in data
            assert "path" in data
            assert "error_code" in data
            
            assert data["success"] is False
            assert data["message"] == "測試錯誤"
            assert data["path"] == "/api/v1/test"

        def test_error_response_with_details(self, mock_request):
            """測試帶詳細信息的錯誤響應"""
            details = {"field": "email", "error": "格式不正確"}
            exc = ApplicationException("驗證失敗", details=details)
            
            response = application_exception_handler(mock_request, exc)
            
            content = response.body.decode()
            import json
            data = json.loads(content)
            
            assert "details" in data
            assert data["details"]["field"] == "email"
            assert data["details"]["error"] == "格式不正確"

        def test_timestamp_format(self, mock_request):
            """測試時間戳格式"""
            exc = ApplicationException("測試錯誤")
            
            response = application_exception_handler(mock_request, exc)
            
            content = response.body.decode()
            import json
            data = json.loads(content)
            
            timestamp = data["timestamp"]
            # 驗證 ISO 格式時間戳
            from datetime import datetime
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail("時間戳格式不正確")

    @pytest.mark.integration
    @pytest.mark.infrastructure
    class TestExceptionHandlerIntegration:
        """異常處理器集成測試"""

        def test_exception_handler_with_new_client(self, new_client, auth_headers):
            """測試異常處理器與新客戶端的集成"""
            # 嘗試創建無效訂閱來觸發驗證錯誤
            payload = {
                "name": "",  # 空名稱
                "original_price": -100,  # 負價格
                "currency": "INVALID",  # 無效貨幣
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01T00:00:00"
            }
            
            response = new_client.post(
                "/api/v1/subscriptions/",
                json=payload,
                headers=auth_headers
            )
            
            # 應該觸發異常處理器
            assert response.status_code in [400, 422]
            
            data = response.json()
            assert "success" in data
            assert data["success"] is False
            assert "timestamp" in data

        def test_404_exception_handler(self, new_client, auth_headers):
            """測試 404 異常處理"""
            response = new_client.get(
                "/api/v1/subscriptions/99999",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            
            data = response.json()
            assert data["success"] is False
            assert "訂閱不存在" in data["message"]
            assert "timestamp" in data

        def test_401_exception_handler(self, new_client):
            """測試 401 異常處理"""
            response = new_client.get("/api/v1/subscriptions/")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
            data = response.json()
            assert data["success"] is False
            assert "timestamp" in data

        def test_validation_exception_in_api(self, new_client, auth_headers):
            """測試 API 中的驗證異常"""
            # 發送格式錯誤的 JSON
            response = new_client.post(
                "/api/v1/subscriptions/",
                data="invalid json",  # 不是 JSON 格式
                headers={**auth_headers, "Content-Type": "application/json"}
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            data = response.json()
            assert data["success"] is False

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestExceptionLogging:
        """異常日誌記錄測試"""

        @patch('app.common.exception_handlers.app_logger')
        def test_application_exception_logging(self, mock_logger, mock_request):
            """測試應用異常的日誌記錄"""
            exc = ApplicationException("應用錯誤", error_code="TEST_ERROR")
            
            application_exception_handler(mock_request, exc)
            
            # 驗證日誌記錄
            mock_logger.warning.assert_called_once()
            args = mock_logger.warning.call_args[0]
            assert "應用異常" in args[0]
            assert "TEST_ERROR" in str(args)

        @patch('app.common.exception_handlers.app_logger')
        def test_sqlalchemy_exception_logging(self, mock_logger, mock_request):
            """測試 SQLAlchemy 異常的日誌記錄"""
            exc = SQLAlchemyError("Database error")
            
            sqlalchemy_exception_handler(mock_request, exc)
            
            # 驗證日誌記錄
            mock_logger.error.assert_called_once()
            args = mock_logger.error.call_args[0]
            assert "數據庫異常" in args[0]

        @patch('app.common.exception_handlers.app_logger')
        def test_generic_exception_logging(self, mock_logger, mock_request):
            """測試通用異常的日誌記錄"""
            exc = Exception("Unexpected error")
            
            generic_exception_handler(mock_request, exc)
            
            # 驗證日誌記錄
            mock_logger.error.assert_called_once()
            args = mock_logger.error.call_args[0]
            assert "未處理異常" in args[0]