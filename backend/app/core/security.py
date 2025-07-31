"""
安全工具模塊 - 輸入驗證、清理和安全防護
"""
import re
import html
import unicodedata
from typing import Optional, Union, List
from pydantic import validator
import bleach


class SecurityValidator:
    """安全驗證器"""
    
    # 常見的惡意模式
    SUSPICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS script 標籤
        r'javascript:',                # JavaScript 協議
        r'vbscript:',                 # VBScript 協議
        r'onload\s*=',                # 事件處理器
        r'onerror\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'<iframe[^>]*>',             # iframe 標籤
        r'<embed[^>]*>',              # embed 標籤
        r'<object[^>]*>',             # object 標籤
        r'eval\s*\(',                 # eval 函數
        r'document\.cookie',          # Cookie 訪問
        r'document\.write',           # DOM 寫入
    ]
    
    # SQL 注入模式
    SQL_INJECTION_PATTERNS = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
        r'(\b(or|and)\s+\d+\s*=\s*\d+\b)',
        r'(--|#|\/\*|\*\/)',
        r'(\b(concat|char|ascii|substring|length|version|database|user|table_name)\b)',
        r'(\'|\"|`|;)',
    ]
    
    @classmethod
    def is_suspicious_input(cls, text: str) -> bool:
        """檢查輸入是否包含可疑模式"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def has_sql_injection(cls, text: str) -> bool:
        """檢查是否包含 SQL 注入模式"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """清理 HTML 內容"""
        if not text:
            return text
        
        # 允許的標籤和屬性
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        allowed_attributes = {}
        
        # 使用 bleach 清理 HTML
        cleaned = bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        return cleaned
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: Optional[int] = None) -> str:
        """清理文本輸入"""
        if not text:
            return text
        
        # 規範化 Unicode 字符
        text = unicodedata.normalize('NFKC', text)
        
        # HTML 轉義
        text = html.escape(text)
        
        # 移除控制字符（除了常見的空白字符）
        text = ''.join(char for char in text if not unicodedata.category(char).startswith('C') or char in '\t\n\r ')
        
        # 限制長度
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    @classmethod
    def validate_username(cls, username: str) -> str:
        """驗證和清理用戶名"""
        if not username:
            raise ValueError("用戶名不能為空")
        
        # 基本清理
        username = cls.sanitize_text(username, max_length=50)
        
        # 檢查可疑模式
        if cls.is_suspicious_input(username):
            raise ValueError("用戶名包含不允許的字符")
        
        # 用戶名格式驗證
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', username):
            raise ValueError("用戶名只能包含字母、數字、下劃線和中文字符")
        
        if len(username) < 3:
            raise ValueError("用戶名長度至少需要 3 個字符")
        
        if len(username) > 50:
            raise ValueError("用戶名長度不能超過 50 個字符")
        
        return username
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """驗證和清理電子郵件"""
        if not email:
            raise ValueError("電子郵件不能為空")
        
        # 基本清理
        email = cls.sanitize_text(email.lower(), max_length=320)
        
        # 檢查可疑模式
        if cls.is_suspicious_input(email):
            raise ValueError("電子郵件格式不正確")
        
        # 電子郵件格式驗證
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("電子郵件格式不正確")
        
        return email
    
    @classmethod
    def validate_subscription_name(cls, name: str) -> str:
        """驗證和清理訂閱服務名稱"""
        if not name:
            raise ValueError("服務名稱不能為空")
        
        # 基本清理
        name = cls.sanitize_text(name, max_length=100)
        
        # 檢查可疑模式
        if cls.is_suspicious_input(name):
            raise ValueError("服務名稱包含不允許的字符")
        
        if len(name) < 1:
            raise ValueError("服務名稱不能為空")
        
        if len(name) > 100:
            raise ValueError("服務名稱長度不能超過 100 個字符")
        
        return name
    
    @classmethod
    def validate_price(cls, price: Union[int, float]) -> float:
        """驗證價格"""
        if price is None:
            raise ValueError("價格不能為空")
        
        try:
            price = float(price)
        except (ValueError, TypeError):
            raise ValueError("價格必須是數字")
        
        if price < 0:
            raise ValueError("價格不能為負數")
        
        if price > 999999.99:
            raise ValueError("價格不能超過 999,999.99")
        
        # 保留兩位小數
        return round(price, 2)
    
    @classmethod
    def validate_category(cls, category: str) -> str:
        """驗證訂閱分類"""
        valid_categories = [
            "entertainment", "music", "productivity", "gaming", 
            "news", "education", "fitness", "food", "shopping", "other"
        ]
        
        if not category:
            raise ValueError("分類不能為空")
        
        category = category.lower().strip()
        
        if category not in valid_categories:
            raise ValueError(f"無效的分類，有效選項：{', '.join(valid_categories)}")
        
        return category
    
    @classmethod
    def validate_cycle(cls, cycle: str) -> str:
        """驗證計費週期"""
        valid_cycles = ["monthly", "yearly", "weekly", "daily"]
        
        if not cycle:
            raise ValueError("計費週期不能為空")
        
        cycle = cycle.lower().strip()
        
        if cycle not in valid_cycles:
            raise ValueError(f"無效的計費週期，有效選項：{', '.join(valid_cycles)}")
        
        return cycle
    
    @classmethod
    def validate_date_string(cls, date_str: str) -> str:
        """驗證日期字符串格式"""
        if not date_str:
            raise ValueError("日期不能為空")
        
        # 清理輸入
        date_str = cls.sanitize_text(date_str, max_length=10)
        
        # 驗證日期格式 YYYY-MM-DD
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, date_str):
            raise ValueError("日期格式必須為 YYYY-MM-DD")
        
        # 進一步驗證日期有效性
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError("無效的日期")
        
        return date_str


class InputSanitizer:
    """輸入清理器"""
    
    @staticmethod
    def clean_string_input(value: str, max_length: Optional[int] = None) -> str:
        """清理字符串輸入"""
        return SecurityValidator.sanitize_text(value, max_length)
    
    @staticmethod
    def clean_html_input(value: str) -> str:
        """清理 HTML 輸入"""
        return SecurityValidator.sanitize_html(value)
    
    @staticmethod
    def clean_search_query(query: str) -> str:
        """清理搜索查詢"""
        if not query:
            return ""
        
        # 基本清理
        query = SecurityValidator.sanitize_text(query, max_length=200)
        
        # 檢查 SQL 注入
        if SecurityValidator.has_sql_injection(query):
            raise ValueError("搜索查詢包含不允許的字符")
        
        return query


# Pydantic 驗證器函數
def validate_username_field(v):
    """用戶名字段驗證器"""
    return SecurityValidator.validate_username(v)


def validate_email_field(v):
    """電子郵件字段驗證器"""
    return SecurityValidator.validate_email(v)


def validate_subscription_name_field(v):
    """訂閱名稱字段驗證器"""
    return SecurityValidator.validate_subscription_name(v)


def validate_price_field(v):
    """價格字段驗證器"""
    return SecurityValidator.validate_price(v)


def validate_category_field(v):
    """分類字段驗證器"""
    return SecurityValidator.validate_category(v)


def validate_cycle_field(v):
    """週期字段驗證器"""
    return SecurityValidator.validate_cycle(v)