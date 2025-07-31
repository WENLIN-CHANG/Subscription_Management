import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.auth import verify_password, get_password_hash


@pytest.mark.api
@pytest.mark.auth
class TestAuthAPI:
    """認證 API 測試"""

    def test_register_success(self, client: TestClient, db_session: Session):
        """測試成功註冊"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        
        # 驗證用戶已保存到資料庫
        user = db_session.query(User).filter(User.username == user_data["username"]).first()
        assert user is not None
        assert user.email == user_data["email"]
        assert verify_password(user_data["password"], user.hashed_password)

    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """測試重複用戶名註冊"""
        user_data = {
            "username": test_user.username,
            "email": "different@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """測試重複電子郵件註冊"""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """測試無效電子郵件格式"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """測試密碼過短"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, test_user: User):
        """測試成功登入"""
        login_data = {
            "username": test_user.username,
            "password": "testpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client: TestClient):
        """測試無效用戶名登入"""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "用戶名或密碼錯誤" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """測試無效密碼登入"""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "用戶名或密碼錯誤" in response.json()["detail"]

    def test_login_empty_credentials(self, client: TestClient):
        """測試空憑證登入"""
        login_data = {
            "username": "",
            "password": ""
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 422

    def test_get_current_user_success(self, client: TestClient, auth_headers: dict, test_user: User):
        """測試獲取當前用戶成功"""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    def test_get_current_user_unauthorized(self, client: TestClient):
        """測試未授權獲取用戶資訊"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """測試無效 token 獲取用戶資訊"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401

    def test_change_password_success(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """測試成功修改密碼"""
        password_data = {
            "current_password": "testpassword",
            "new_password": "newtestpassword123"
        }
        
        response = client.put("/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert "密碼修改成功" in response.json()["message"]
        
        # 驗證密碼已更新
        db_session.refresh(test_user)
        assert verify_password(password_data["new_password"], test_user.hashed_password)

    def test_change_password_wrong_current(self, client: TestClient, auth_headers: dict):
        """測試錯誤的當前密碼"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newtestpassword123"
        }
        
        response = client.put("/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "當前密碼錯誤" in response.json()["detail"]

    def test_change_password_empty_new(self, client: TestClient, auth_headers: dict):
        """測試空的新密碼"""
        password_data = {
            "current_password": "testpassword",
            "new_password": ""
        }
        
        response = client.put("/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "新密碼不能為空" in response.json()["detail"]

    def test_change_password_unauthorized(self, client: TestClient):
        """測試未授權修改密碼"""
        password_data = {
            "current_password": "testpassword",
            "new_password": "newtestpassword123"
        }
        
        response = client.put("/auth/change-password", json=password_data)
        
        assert response.status_code == 401