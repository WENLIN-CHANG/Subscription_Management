from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator
from datetime import datetime
import re

class ValidationRules:
    """驗證規則常量"""
    
    # 密碼規則
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]')
    
    # 用戶名規則
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 50
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    # 郵箱規則
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # 金額規則
    AMOUNT_MIN = 0.01
    AMOUNT_MAX = 999999.99
    
    # 訂閱名稱規則
    SUBSCRIPTION_NAME_MIN_LENGTH = 1
    SUBSCRIPTION_NAME_MAX_LENGTH = 100

class BaseValidator(BaseModel):
    """基礎驗證器"""
    
    @validator('*', pre=True)
    def strip_strings(cls, v):
        """去除字符串前後空格"""
        if isinstance(v, str):
            return v.strip()
        return v

class PasswordValidator:
    """密碼驗證器"""
    
    @staticmethod
    def validate_password(password: str) -> List[str]:
        """驗證密碼強度"""
        errors = []
        
        if len(password) < ValidationRules.PASSWORD_MIN_LENGTH:
            errors.append(f"密碼長度至少需要 {ValidationRules.PASSWORD_MIN_LENGTH} 個字符")
        
        if len(password) > ValidationRules.PASSWORD_MAX_LENGTH:
            errors.append(f"密碼長度不能超過 {ValidationRules.PASSWORD_MAX_LENGTH} 個字符")
        
        if not re.search(r'[a-z]', password):
            errors.append("密碼必須包含至少一個小寫字母")
        
        if not re.search(r'[A-Z]', password):
            errors.append("密碼必須包含至少一個大寫字母")
        
        if not re.search(r'\d', password):
            errors.append("密碼必須包含至少一個數字")
        
        if not re.search(r'[@$!%*?&]', password):
            errors.append("密碼必須包含至少一個特殊字符 (@$!%*?&)")
        
        return errors

class EmailValidator:
    """郵箱驗證器"""
    
    @staticmethod
    def validate_email(email: str) -> List[str]:
        """驗證郵箱格式"""
        errors = []
        
        if not ValidationRules.EMAIL_PATTERN.match(email):
            errors.append("郵箱格式不正確")
        
        if len(email) > 254:  # RFC 5321 限制
            errors.append("郵箱地址過長")
        
        return errors

class AmountValidator:
    """金額驗證器"""
    
    @staticmethod
    def validate_amount(amount: float, field_name: str = "金額") -> List[str]:
        """驗證金額"""
        errors = []
        
        if amount < ValidationRules.AMOUNT_MIN:
            errors.append(f"{field_name}必須大於 {ValidationRules.AMOUNT_MIN}")
        
        if amount > ValidationRules.AMOUNT_MAX:
            errors.append(f"{field_name}不能超過 {ValidationRules.AMOUNT_MAX}")
        
        # 檢查小數位數不超過2位
        if round(amount, 2) != amount:
            errors.append(f"{field_name}小數位數不能超過2位")
        
        return errors

class DateValidator:
    """日期驗證器"""
    
    @staticmethod
    def validate_future_date(date: datetime, field_name: str = "日期") -> List[str]:
        """驗證未來日期"""
        errors = []
        
        if date < datetime.now():
            errors.append(f"{field_name}不能是過去的時間")
        
        return errors
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> List[str]:
        """驗證日期範圍"""
        errors = []
        
        if start_date >= end_date:
            errors.append("開始日期必須早於結束日期")
        
        return errors

class SubscriptionValidator:
    """訂閱驗證器"""
    
    @staticmethod
    def validate_subscription_name(name: str) -> List[str]:
        """驗證訂閱名稱"""
        errors = []
        
        if len(name) < ValidationRules.SUBSCRIPTION_NAME_MIN_LENGTH:
            errors.append(f"訂閱名稱至少需要 {ValidationRules.SUBSCRIPTION_NAME_MIN_LENGTH} 個字符")
        
        if len(name) > ValidationRules.SUBSCRIPTION_NAME_MAX_LENGTH:
            errors.append(f"訂閱名稱不能超過 {ValidationRules.SUBSCRIPTION_NAME_MAX_LENGTH} 個字符")
        
        # 檢查是否包含特殊字符
        if re.search(r'[<>"\']', name):
            errors.append("訂閱名稱不能包含特殊字符 < > \" '")
        
        return errors

class BulkOperationValidator:
    """批量操作驗證器"""
    
    @staticmethod
    def validate_ids_list(ids: List[int], max_count: int = 100) -> List[str]:
        """驗證ID列表"""
        errors = []
        
        if not ids:
            errors.append("ID列表不能為空")
        
        if len(ids) > max_count:
            errors.append(f"一次最多只能操作 {max_count} 個項目")
        
        # 檢查重複ID
        if len(ids) != len(set(ids)):
            errors.append("ID列表中不能有重複項目")
        
        # 檢查ID是否都是正整數
        for id_val in ids:
            if not isinstance(id_val, int) or id_val <= 0:
                errors.append("所有ID必須是正整數")
                break
        
        return errors

class RequestSizeValidator:
    """請求大小驗證器"""
    
    @staticmethod
    def validate_content_length(content_length: int, max_size: int = 1024 * 1024) -> List[str]:
        """驗證請求內容大小"""
        errors = []
        
        if content_length > max_size:
            errors.append(f"請求內容大小不能超過 {max_size // 1024} KB")
        
        return errors