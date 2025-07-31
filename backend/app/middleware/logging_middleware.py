"""
日誌中間件 - 記錄所有 API 請求和響應
"""
import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.logging_config import APILogger, SecurityEventLogger


class LoggingMiddleware(BaseHTTPMiddleware):
    """API 請求日誌中間件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 記錄請求開始時間
        start_time = time.time()
        
        # 獲取客戶端 IP
        client_ip = self.get_client_ip(request)
        
        # 獲取用戶 ID（如果已登入）
        user_id = getattr(request.state, 'user_id', None) if hasattr(request.state, 'user_id') else None
        
        # 生成請求 ID
        request_id = f"{int(time.time() * 1000000)}"
        request.state.request_id = request_id
        
        try:
            # 處理請求
            response = await call_next(request)
            
            # 計算響應時間
            process_time = time.time() - start_time
            
            # 記錄 API 請求
            APILogger.log_request(
                method=request.method,
                endpoint=request.url.path,
                user_id=user_id,
                ip_address=client_ip,
                response_status=response.status_code,
                response_time=process_time
            )
            
            # 添加響應標頭
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 計算錯誤響應時間
            process_time = time.time() - start_time
            
            # 記錄 API 錯誤
            APILogger.log_api_error(
                method=request.method,
                endpoint=request.url.path,
                error=e,
                user_id=user_id,
                ip_address=client_ip
            )
            
            # 返回錯誤響應
            return JSONResponse(
                status_code=500,
                content={
                    "error": "內部服務器錯誤",
                    "request_id": request_id
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time": str(process_time)
                }
            )
    
    def get_client_ip(self, request: Request) -> str:
        """獲取客戶端真實 IP 地址"""  
        # 檢查各種可能的 IP 標頭
        ip_headers = [
            "X-Forwarded-For",
            "X-Real-IP", 
            "X-Client-IP",
            "CF-Connecting-IP",  # Cloudflare
            "True-Client-IP"     # Akamai
        ]
        
        for header in ip_headers:
            ip = request.headers.get(header)
            if ip:
                # X-Forwarded-For 可能包含多個 IP，取第一個
                return ip.split(',')[0].strip()
        
        # 回退到連接信息
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """安全事件日誌中間件"""
    
    # 需要特別監控的端點
    SENSITIVE_ENDPOINTS = {
        '/api/auth/login',
        '/api/auth/register', 
        '/api/auth/change-password'
    }
    
    # 可疑的用戶代理字符串
    SUSPICIOUS_USER_AGENTS = [
        'sqlmap',
        'nmap',
        'nikto',
        'burp',
        'owasp',
        'scanner'
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 獲取客戶端信息
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "").lower()
        
        # 檢查可疑活動
        self.check_suspicious_activity(request, client_ip, user_agent)
        
        # 處理請求
        response = await call_next(request)
        
        # 對敏感端點進行額外記錄
        if request.url.path in self.SENSITIVE_ENDPOINTS:
            self.log_sensitive_endpoint_access(request, response, client_ip)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """獲取客戶端 IP（同上）"""
        ip_headers = [
            "X-Forwarded-For",
            "X-Real-IP", 
            "X-Client-IP",
            "CF-Connecting-IP",
            "True-Client-IP"
        ]
        
        for header in ip_headers:
            ip = request.headers.get(header)
            if ip:
                return ip.split(',')[0].strip()
        
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"
    
    def check_suspicious_activity(self, request: Request, client_ip: str, user_agent: str):
        """檢查可疑活動"""
        # 檢查可疑的用戶代理
        for suspicious_ua in self.SUSPICIOUS_USER_AGENTS:
            if suspicious_ua in user_agent:
                SecurityEventLogger.log_suspicious_activity(
                    ip_address=client_ip,
                    activity="可疑用戶代理",
                    details=f"User-Agent: {user_agent}"
                )
                break
        
        # 檢查可疑的查詢參數
        query_string = str(request.url.query).lower()
        suspicious_patterns = [
            'script',
            'alert(',
            'javascript:',
            'union select',
            'drop table',
            '../',
            '..\\',
            '<script'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in query_string:
                SecurityEventLogger.log_suspicious_activity(
                    ip_address=client_ip,
                    activity="可疑查詢參數",
                    details=f"Pattern: {pattern}, Query: {query_string[:200]}"
                )
                break
    
    def log_sensitive_endpoint_access(self, request: Request, response: Response, client_ip: str):
        """記錄敏感端點訪問"""
        endpoint = request.url.path
        method = request.method
        status = response.status_code
        
        # 記錄所有對敏感端點的訪問
        logging.getLogger('security').info(
            f"敏感端點訪問: {method} {endpoint} - Status: {status}",
            extra={
                'event_type': 'sensitive_endpoint_access',
                'method': method,
                'endpoint': endpoint,
                'ip_address': client_ip,
                'status_code': status
            }
        )