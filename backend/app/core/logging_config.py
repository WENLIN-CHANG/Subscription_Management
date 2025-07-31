"""
日誌配置模塊
"""
import logging
import logging.handlers
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON 格式的日誌格式化器"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # 添加額外的上下文信息
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
            
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
            
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        
        # 如果有異常信息，添加異常詳情
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging():
    """設置應用程式日誌"""
    
    # 創建日誌目錄
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # 獲取根記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除現有處理器
    root_logger.handlers.clear()
    
    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    if settings.debug:
        # 開發模式使用簡單格式
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        # 生產模式使用 JSON 格式
        console_formatter = JSONFormatter()
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件處理器 - 一般日誌
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # 文件處理器 - 錯誤日誌
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'error.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)
    
    # 安全事件日誌
    security_logger = logging.getLogger('security')
    security_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'security.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=20,
        encoding='utf-8'
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(JSONFormatter())
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    
    # 訪問日誌
    access_logger = logging.getLogger('access')
    access_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'access.log',
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(JSONFormatter())
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)
    
    # 設置第三方庫的日誌級別
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    logging.info("日誌系統初始化完成")


def get_logger(name: str) -> logging.Logger:
    """獲取指定名稱的記錄器"""
    return logging.getLogger(name)


class LogContext:
    """日誌上下文管理器"""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)


def log_with_context(logger: logging.Logger, **context):
    """為記錄器添加上下文信息"""
    return LogContext(logger, **context)


# 預定義的記錄器
app_logger = get_logger('app')
security_logger = get_logger('security')
access_logger = get_logger('access')
db_logger = get_logger('database')
auth_logger = get_logger('auth')
api_logger = get_logger('api')


class SecurityEventLogger:
    """安全事件記錄器"""
    
    @staticmethod
    def log_failed_login(username: str, ip_address: str, reason: str = "Invalid credentials"):
        """記錄登入失敗事件"""
        security_logger.warning(
            f"登入失敗: 用戶 {username} 從 {ip_address} 嘗試登入失敗",
            extra={
                'event_type': 'login_failure',
                'username': username,
                'ip_address': ip_address,
                'reason': reason
            }
        )
    
    @staticmethod
    def log_successful_login(user_id: int, username: str, ip_address: str):
        """記錄成功登入事件"""
        security_logger.info(
            f"成功登入: 用戶 {username} (ID: {user_id}) 從 {ip_address} 登入",
            extra={
                'event_type': 'login_success',
                'user_id': user_id,
                'username': username,
                'ip_address': ip_address
            }
        )
    
    @staticmethod
    def log_logout(user_id: int, username: str, ip_address: str):
        """記錄登出事件"""
        security_logger.info(
            f"用戶登出: 用戶 {username} (ID: {user_id}) 從 {ip_address} 登出",
            extra={
                'event_type': 'logout',
                'user_id': user_id,
                'username': username,
                'ip_address': ip_address
            }
        )
    
    @staticmethod
    def log_password_change(user_id: int, username: str, ip_address: str):
        """記錄密碼修改事件"""
        security_logger.info(
            f"密碼修改: 用戶 {username} (ID: {user_id}) 從 {ip_address} 修改密碼",
            extra={
                'event_type': 'password_change',
                'user_id': user_id,
                'username': username,
                'ip_address': ip_address
            }
        )
    
    @staticmethod
    def log_rate_limit_exceeded(ip_address: str, endpoint: str, limit: str):
        """記錄速率限制超出事件"""
        security_logger.warning(
            f"速率限制超出: IP {ip_address} 在端點 {endpoint} 超出限制 {limit}",
            extra={
                'event_type': 'rate_limit_exceeded',
                'ip_address': ip_address,
                'endpoint': endpoint,
                'limit': limit
            }
        )
    
    @staticmethod
    def log_suspicious_activity(ip_address: str, activity: str, details: str = ""):
        """記錄可疑活動"""
        security_logger.warning(
            f"可疑活動: IP {ip_address} 進行了可疑操作 - {activity}",
            extra={
                'event_type': 'suspicious_activity',
                'ip_address': ip_address,
                'activity': activity,
                'details': details
            }
        )


class APILogger:
    """API 請求記錄器"""
    
    @staticmethod
    def log_request(method: str, endpoint: str, user_id: Optional[int], ip_address: str, 
                   response_status: int, response_time: float):
        """記錄 API 請求"""
        access_logger.info(
            f"{method} {endpoint} - Status: {response_status} - Time: {response_time:.3f}s",
            extra={
                'method': method,
                'endpoint': endpoint,
                'user_id': user_id,
                'ip_address': ip_address,
                'response_status': response_status,
                'response_time': response_time,
                'event_type': 'api_request'
            }
        )
    
    @staticmethod
    def log_api_error(method: str, endpoint: str, error: Exception, 
                     user_id: Optional[int] = None, ip_address: str = "unknown"):
        """記錄 API 錯誤"""
        api_logger.error(
            f"API 錯誤: {method} {endpoint} - {str(error)}",
            extra={
                'method': method,
                'endpoint': endpoint,
                'user_id': user_id,
                'ip_address': ip_address,
                'error_type': type(error).__name__,
                'event_type': 'api_error'
            },
            exc_info=True
        )


class DatabaseLogger:
    """資料庫操作記錄器"""
    
    @staticmethod
    def log_query_error(query: str, error: Exception, user_id: Optional[int] = None):
        """記錄資料庫查詢錯誤"""
        db_logger.error(
            f"資料庫查詢錯誤: {str(error)}",
            extra={
                'query': query[:500],  # 限制查詢字符串長度
                'user_id': user_id,
                'error_type': type(error).__name__,
                'event_type': 'db_error'
            },
            exc_info=True
        )
    
    @staticmethod
    def log_slow_query(query: str, execution_time: float, user_id: Optional[int] = None):
        """記錄慢查詢"""
        if execution_time > 1.0:  # 超過 1 秒的查詢
            db_logger.warning(
                f"慢查詢檢測: 執行時間 {execution_time:.3f}s",
                extra={
                    'query': query[:500],
                    'execution_time': execution_time,
                    'user_id': user_id,
                    'event_type': 'slow_query'
                }
            )