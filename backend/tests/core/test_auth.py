import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.core.auth import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password
)
from app.core.config import settings


@pytest.mark.unit
class TestAuthCore:
    """認證核心功能測試"""

    def test_password_hashing(self):
        """測試密碼哈希功能"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # 哈希後的密碼不應該等於原密碼
        assert hashed != password
        
        # 應該能夠驗證密碼
        assert verify_password(password, hashed) is True
        
        # 錯誤密碼應該驗證失敗
        assert verify_password("wrong_password", hashed) is False

    def test_password_hashing_different_results(self):
        """測試相同密碼產生不同哈希值"""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # 相同密碼應該產生不同的哈希值（由於鹽值不同）
        assert hash1 != hash2
        
        # 但都應該能夠驗證原密碼
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_create_access_token_default_expiry(self):
        """測試創建訪問令牌（默認過期時間）"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # 解碼令牌驗證內容
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        assert payload["sub"] == "testuser"
        assert "exp" in payload
        
        # 驗證過期時間大約是預期的時間
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        time_diff = abs((exp_time - expected_time).total_seconds())
        
        # 允許 10 秒的誤差
        assert time_diff < 10

    def test_create_access_token_custom_expiry(self):
        """測試創建訪問令牌（自定義過期時間）"""
        data = {"sub": "testuser"}
        custom_expiry = timedelta(hours=2)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        assert payload["sub"] == "testuser"
        
        # 驗證自定義過期時間
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + custom_expiry
        time_diff = abs((exp_time - expected_time).total_seconds())
        
        # 允許 10 秒的誤差
        assert time_diff < 10

    def test_create_access_token_additional_data(self):
        """測試創建包含額外數據的訪問令牌"""
        data = {
            "sub": "testuser",
            "user_id": 123,
            "role": "admin"
        }
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == 123
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_verify_token_valid(self):
        """測試驗證有效令牌"""
        username = "testuser"
        data = {"sub": username}
        token = create_access_token(data)
        
        verified_username = verify_token(token)
        
        assert verified_username == username

    def test_verify_token_invalid_signature(self):
        """測試驗證無效簽名的令牌"""
        # 創建一個用錯誤密鑰簽名的令牌
        data = {"sub": "testuser"}
        wrong_key = "wrong_secret_key"
        token = jwt.encode(data, wrong_key, algorithm=settings.algorithm)
        
        result = verify_token(token)
        
        assert result is None

    def test_verify_token_expired(self):
        """測試驗證過期令牌"""
        data = {"sub": "testuser"}
        # 創建一個已過期的令牌
        expired_delta = timedelta(seconds=-1)  # 1秒前過期
        token = create_access_token(data, expires_delta=expired_delta)
        
        result = verify_token(token)
        
        assert result is None

    def test_verify_token_no_subject(self):
        """測試驗證沒有主題的令牌"""
        data = {"user_id": 123}  # 沒有 "sub" 字段
        token = jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
        
        result = verify_token(token)
        
        assert result is None

    def test_verify_token_malformed(self):
        """測試驗證格式錯誤的令牌"""
        malformed_token = "invalid.token.format"
        
        result = verify_token(malformed_token)
        
        assert result is None

    def test_verify_token_empty(self):
        """測試驗證空令牌"""
        result = verify_token("")
        assert result is None
        
        result = verify_token(None)
        assert result is None

    def test_password_verification_edge_cases(self):
        """測試密碼驗證的邊界情況"""
        password = "test123"
        hashed = get_password_hash(password)
        
        # 測試空密碼
        assert verify_password("", hashed) is False
        
        # 測試 None 密碼
        assert verify_password(None, hashed) is False
        
        # 測試對空哈希值的驗證
        with pytest.raises(Exception):
            verify_password(password, "")
        
        with pytest.raises(Exception):
            verify_password(password, None)

    def test_token_algorithm_consistency(self):
        """測試令牌算法一致性"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # 手動解碼以檢查算法
        header = jwt.get_unverified_header(token)
        assert header["alg"] == settings.algorithm
        
        # 使用不同算法應該失敗
        with pytest.raises(JWTError):
            jwt.decode(token, settings.secret_key, algorithms=["HS512"])

    def test_special_characters_in_password(self):
        """測試包含特殊字符的密碼"""
        special_passwords = [
            "password!@#$%^&*()",
            "密碼中文测试",
            "пароль кириллица",
            "🔐🔑🛡️ emojis",
            "tabs\tand\nnewlines"
        ]
        
        for password in special_passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True
            assert verify_password(password + "wrong", hashed) is False

    def test_long_password_handling(self):
        """測試長密碼處理"""
        # 測試非常長的密碼
        long_password = "a" * 1000
        hashed = get_password_hash(long_password)
        
        assert verify_password(long_password, hashed) is True
        assert verify_password(long_password[:-1], hashed) is False

    def test_token_with_unicode_username(self):
        """測試包含 Unicode 字符的用戶名令牌"""
        unicode_usernames = [
            "用戶名",
            "пользователь",
            "ユーザー名",
            "🦄unicorn_user"
        ]
        
        for username in unicode_usernames:
            data = {"sub": username}
            token = create_access_token(data)
            verified_username = verify_token(token)
            
            assert verified_username == username