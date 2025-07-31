import { describe, it, expect, beforeEach, vi } from 'vitest'

// 模擬依賴
vi.mock('../../frontend/scripts/auth/apiClient.js', () => ({
  apiClient: {
    getToken: vi.fn(),
    setToken: vi.fn(),
    clearToken: vi.fn(),
    auth: {
      login: vi.fn(),
      register: vi.fn(),
      getCurrentUser: vi.fn(),
      changePassword: vi.fn()
    }
  }
}))

vi.mock('../../frontend/scripts/ui/stateManager.js', () => ({
  stateManager: {
    withLoading: vi.fn(),
    error: {
      set: vi.fn()
    },
    success: {
      set: vi.fn()
    }
  }
}))

vi.mock('../../frontend/scripts/data/migrationManager.js', () => ({
  migrationManager: {
    checkAndPromptMigration: vi.fn()
  }
}))

vi.mock('../../frontend/scripts/data/dataManager.js', () => ({
  dataManager: {
    loadSubscriptions: vi.fn().mockResolvedValue([])
  }
}))

import { authManager } from '../../frontend/scripts/auth/authManager.js'
import { apiClient } from '../../frontend/scripts/auth/apiClient.js'
import { stateManager } from '../../frontend/scripts/ui/stateManager.js'

describe('authManager', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    authManager.currentUser = null
    authManager.loginForm = {
      username: '',
      password: ''
    }
    authManager.registerForm = {
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    }
    authManager.changePasswordForm = {
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: ''
    }
  })

  describe('isLoggedIn', () => {
    it('有 token 和用戶時應該返回 true', () => {
      apiClient.getToken.mockReturnValue('mock-token')
      authManager.currentUser = { username: 'testuser' }
      
      expect(authManager.isLoggedIn()).toBe(true)
    })

    it('沒有 token 時應該返回 false', () => {
      apiClient.getToken.mockReturnValue(null)
      authManager.currentUser = { username: 'testuser' }
      
      expect(authManager.isLoggedIn()).toBe(false)
    })

    it('沒有用戶時應該返回 false', () => {
      apiClient.getToken.mockReturnValue('mock-token')
      authManager.currentUser = null
      
      expect(authManager.isLoggedIn()).toBe(false)
    })
  })

  describe('validateLoginForm', () => {
    it('有效表單應該返回 true', () => {
      authManager.loginForm = {
        username: 'testuser',
        password: 'password123'
      }
      
      expect(authManager.validateLoginForm()).toBe(true)
    })

    it('缺少用戶名應該返回 false', () => {
      authManager.loginForm = {
        username: '',
        password: 'password123'
      }
      
      expect(authManager.validateLoginForm()).toBe(false)
      expect(stateManager.error.set).toHaveBeenCalledWith('請輸入用戶名', '登入驗證')
    })

    it('缺少密碼應該返回 false', () => {
      authManager.loginForm = {
        username: 'testuser',
        password: ''
      }
      
      expect(authManager.validateLoginForm()).toBe(false)
      expect(stateManager.error.set).toHaveBeenCalledWith('請輸入密碼', '登入驗證')
    })
  })

  describe('validateRegisterForm', () => {
    beforeEach(() => {
      authManager.registerForm = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
        confirmPassword: 'password123'
      }
    })

    it('有效表單應該返回 true', () => {
      expect(authManager.validateRegisterForm()).toBe(true)
    })

    it('密碼不匹配應該返回 false', () => {
      authManager.registerForm.confirmPassword = 'different'
      
      expect(authManager.validateRegisterForm()).toBe(false)
      expect(stateManager.error.set).toHaveBeenCalledWith('兩次輸入的密碼不一致', '註冊驗證')
    })

    it('無效 email 應該返回 false', () => {
      authManager.registerForm.email = 'invalid-email'
      
      expect(authManager.validateRegisterForm()).toBe(false)
      expect(stateManager.error.set).toHaveBeenCalledWith('請輸入有效的電子郵件地址', '註冊驗證')
    })

    it('短密碼應該返回 false', () => {
      authManager.registerForm.password = '123'
      authManager.registerForm.confirmPassword = '123'
      
      expect(authManager.validateRegisterForm()).toBe(false)
      expect(stateManager.error.set).toHaveBeenCalledWith('密碼長度至少需要 6 個字符', '註冊驗證')
    })
  })

  describe('validateChangePasswordForm', () => {
    beforeEach(() => {
      authManager.changePasswordForm = {
        currentPassword: 'oldpass',
        newPassword: 'newpass123',
        confirmNewPassword: 'newpass123'
      }
    })

    it('有效表單應該返回 true', () => {
      expect(authManager.validateChangePasswordForm()).toBe(true)
    })

    it('新密碼不匹配應該返回 false', () => {
      authManager.changePasswordForm.confirmNewPassword = 'different'
      
      expect(authManager.validateChangePasswordForm()).toBe(false)
      expect(stateManager.error.set).toHaveBeenCalledWith('兩次輸入的新密碼不一致', '密碼修改驗證')
    })

    it('新舊密碼相同應該返回 false', () => {
      authManager.changePasswordForm.newPassword = 'oldpass'
      authManager.changePasswordForm.confirmNewPassword = 'oldpass'
      
      expect(authManager.validateChangePasswordForm()).toBe(false)
      expect(stateManager.error.set).toHaveBeenCalledWith('新密碼不能與當前密碼相同', '密碼修改驗證')
    })
  })

  describe('login', () => {
    it('成功登入應該設置用戶資訊', async () => {
      const mockUser = { username: 'testuser', email: 'test@example.com' }
      const mockToken = 'mock-token'
      
      authManager.loginForm = {
        username: 'testuser',
        password: 'password123'
      }
      
      stateManager.withLoading.mockImplementation(async (key, fn) => await fn())
      apiClient.auth.login.mockResolvedValue({ access_token: mockToken })
      apiClient.auth.getCurrentUser.mockResolvedValue(mockUser)
      
      const result = await authManager.login()
      
      expect(result).toBe(true)
      expect(apiClient.setToken).toHaveBeenCalledWith(mockToken)
      expect(authManager.currentUser).toEqual(mockUser)
    })

    it('登入失敗應該返回 false', async () => {
      authManager.loginForm = {
        username: 'testuser',
        password: 'wrongpassword'
      }
      
      stateManager.withLoading.mockImplementation(async (key, fn) => {
        try {
          await fn()
        } catch (error) {
          throw error
        }
      })
      
      apiClient.auth.login.mockRejectedValue(new Error('登入失敗'))
      
      const result = await authManager.login()
      
      expect(result).toBe(false)
      expect(authManager.currentUser).toBe(null)
    })
  })

  describe('register', () => {
    it('成功註冊應該自動登入', async () => {
      const mockUser = { username: 'newuser', email: 'new@example.com' }
      const mockToken = 'mock-token'
      
      authManager.registerForm = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123',
        confirmPassword: 'password123'
      }
      
      stateManager.withLoading.mockImplementation(async (key, fn) => await fn())
      apiClient.auth.register.mockResolvedValue(mockUser)
      apiClient.auth.login.mockResolvedValue({ access_token: mockToken })
      apiClient.auth.getCurrentUser.mockResolvedValue(mockUser)
      
      const result = await authManager.register()
      
      expect(result).toBe(true)
      expect(apiClient.auth.register).toHaveBeenCalled()
      expect(authManager.currentUser).toEqual(mockUser)
    })
  })

  describe('logout', () => {
    it('登出應該清除用戶資訊和 token', () => {
      authManager.currentUser = { username: 'testuser' }
      
      authManager.logout()
      
      expect(apiClient.auth.logout).toHaveBeenCalled()
      expect(authManager.currentUser).toBe(null)
    })
  })

  describe('init', () => {
    it('有有效 token 時應該獲取用戶資訊', async () => {
      const mockUser = { username: 'testuser' }
      
      apiClient.getToken.mockReturnValue('valid-token')
      apiClient.auth.getCurrentUser.mockResolvedValue(mockUser)
      
      const result = await authManager.init()
      
      expect(result).toBe(true)
      expect(authManager.currentUser).toEqual(mockUser)
    })

    it('沒有 token 時應該返回 false', async () => {
      apiClient.getToken.mockReturnValue(null)
      
      const result = await authManager.init()
      
      expect(result).toBe(false)
      expect(authManager.currentUser).toBe(null)
    })

    it('token 無效時應該清除並返回 false', async () => {
      apiClient.getToken.mockReturnValue('invalid-token')
      apiClient.auth.getCurrentUser.mockRejectedValue(new Error('Unauthorized'))
      
      const result = await authManager.init()
      
      expect(result).toBe(false)
      expect(apiClient.clearToken).toHaveBeenCalled()
      expect(authManager.currentUser).toBe(null)
    })
  })
})