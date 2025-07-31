import { apiClient } from './apiClient.js'
import { stateManager } from './stateManager.js'
import { migrationManager } from './migrationManager.js'
import { dataManager } from './dataManager.js'

// 認證管理器
export const authManager = {
  // 當前用戶信息
  currentUser: null,
  
  // 表單數據
  loginForm: {
    username: '',
    password: ''
  },
  
  registerForm: {
    username: '',
    password: '',
    confirmPassword: ''
  },

  changePasswordForm: {
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: ''
  },

  // 檢查是否已登入
  isLoggedIn() {
    return !!apiClient.getToken() && !!this.currentUser
  },

  // 初始化認證狀態
  async init() {
    const token = apiClient.getToken()
    if (token) {
      try {
        this.currentUser = await apiClient.auth.getCurrentUser()
        return true
      } catch (error) {
        console.warn('Token 已過期或無效:', error)
        this.logout()
        return false
      }
    }
    return false
  },

  // 驗證登入表單
  validateLoginForm() {
    if (!this.loginForm.username.trim()) {
      stateManager.error.set('請輸入用戶名', '登入驗證')
      return false
    }
    if (!this.loginForm.password) {
      stateManager.error.set('請輸入密碼', '登入驗證')
      return false
    }
    return true
  },

  // 驗證註冊表單
  validateRegisterForm() {
    if (!this.registerForm.username.trim()) {
      stateManager.error.set('請輸入用戶名', '註冊驗證')
      return false
    }
    if (this.registerForm.username.length < 3) {
      stateManager.error.set('用戶名至少需要3個字符', '註冊驗證')
      return false
    }
    if (!this.registerForm.password) {
      stateManager.error.set('請輸入密碼', '註冊驗證')
      return false
    }
    if (this.registerForm.password.length < 6) {
      stateManager.error.set('密碼至少需要6個字符', '註冊驗證')
      return false
    }
    if (this.registerForm.password !== this.registerForm.confirmPassword) {
      stateManager.error.set('兩次輸入的密碼不一致', '註冊驗證')
      return false
    }
    return true
  },

  // 驗證密碼修改表單
  validateChangePasswordForm() {
    if (!this.changePasswordForm.currentPassword) {
      stateManager.error.set('請輸入當前密碼', '密碼修改驗證')
      return false
    }
    if (!this.changePasswordForm.newPassword) {
      stateManager.error.set('請輸入新密碼', '密碼修改驗證')
      return false
    }
    if (this.changePasswordForm.newPassword !== this.changePasswordForm.confirmNewPassword) {
      stateManager.error.set('兩次輸入的新密碼不一致', '密碼修改驗證')
      return false
    }
    if (this.changePasswordForm.currentPassword === this.changePasswordForm.newPassword) {
      stateManager.error.set('新密碼不能與當前密碼相同', '密碼修改驗證')
      return false
    }
    return true
  },

  // 用戶登入
  async login() {
    if (!this.validateLoginForm()) {
      return false
    }

    try {
      const result = await stateManager.withLoading('login', async () => {
        const response = await apiClient.auth.login({
          username: this.loginForm.username,
          password: this.loginForm.password
        })
        
        // 獲取用戶信息
        this.currentUser = await apiClient.auth.getCurrentUser()
        
        return response
      }, {
        errorContext: '用戶登入',
        successMessage: `歡迎回來，${this.loginForm.username}！`,
        successContext: '登入'
      })

      // 清空表單
      this.resetLoginForm()
      
      // 觸發登入成功事件
      this.onLoginSuccess()
      
      return true

    } catch (error) {
      console.error('登入失敗:', error)
      
      // 根據錯誤類型提供更好的用戶提示
      let errorMessage = error.message
      
      // 如果是用戶不存在，提供註冊引導
      if (error.message && error.message.includes('用戶不存在')) {
        // 自動切換到註冊頁面的提示
        setTimeout(() => {
          const shouldSwitch = confirm('是否切換到註冊頁面？')
          if (shouldSwitch) {
            this.switchAuthMode('register')
          }
        }, 1500)
      }
      
      stateManager.error.set(errorMessage, '用戶登入')
      return false
    }
  },

  // 用戶註冊
  async register() {
    if (!this.validateRegisterForm()) {
      return false
    }

    try {
      const result = await stateManager.withLoading('register', async () => {
        const response = await apiClient.auth.register({
          username: this.registerForm.username,
          password: this.registerForm.password
        })
        
        // 註冊成功後自動登入
        await apiClient.auth.login({
          username: this.registerForm.username,
          password: this.registerForm.password
        })
        
        // 獲取用戶信息
        this.currentUser = await apiClient.auth.getCurrentUser()
        
        return response
      }, {
        errorContext: '用戶註冊',
        successMessage: `註冊成功！歡迎加入，${this.registerForm.username}！`,
        successContext: '註冊'
      })

      // 清空表單
      this.resetRegisterForm()
      
      // 觸發登入成功事件
      this.onLoginSuccess()
      
      return true

    } catch (error) {
      console.error('註冊失敗:', error)
      return false
    }
  },

  // 修改密碼
  async changePassword() {
    if (!this.validateChangePasswordForm()) {
      return false
    }

    try {
      await stateManager.withLoading('changePassword', async () => {
        await apiClient.auth.changePassword({
          current_password: this.changePasswordForm.currentPassword,
          new_password: this.changePasswordForm.newPassword
        })
      }, {
        errorContext: '密碼修改',
        successMessage: '密碼修改成功！',
        successContext: '密碼修改'
      })

      // 清空表單
      this.resetChangePasswordForm()
      
      // 隱藏對話框
      this.hideChangePasswordDialog()
      
      return true

    } catch (error) {
      console.error('密碼修改失敗:', error)
      return false
    }
  },

  // 用戶登出
  logout() {
    apiClient.auth.logout()
    this.currentUser = null
    this.resetLoginForm()
    this.resetRegisterForm()
    
    stateManager.success.show('已成功登出', '登出')
    
    // 觸發登出事件
    this.onLogout()
  },

  // 重置登入表單
  resetLoginForm() {
    this.loginForm = {
      username: '',
      password: ''
    }
  },

  // 重置註冊表單
  resetRegisterForm() {
    this.registerForm = {
      username: '',
      password: '',
      confirmPassword: ''
    }
  },

  // 重置密碼修改表單
  resetChangePasswordForm() {
    this.changePasswordForm = {
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: ''
    }
  },

  // 登入成功回調
  onLoginSuccess() {
    // 隱藏認證對話框
    this.hideAuthDialog()
    
    // 檢查是否有待處理的訂閱資料
    const pendingSubscription = localStorage.getItem('pendingSubscription')
    if (pendingSubscription) {
      // 清除待處理資料
      localStorage.removeItem('pendingSubscription')
      
      // 存儲到一個特殊的鍵，讓頁面重新載入後可以恢復
      localStorage.setItem('restoreSubscriptionForm', pendingSubscription)
    }
    
    // 重新載入數據
    window.location.reload()
  },

  // 登出回調
  onLogout() {
    // 重新載入頁面以重置狀態
    window.location.reload()
  },

  // 顯示認證對話框
  showAuthDialog(mode = 'login') {
    // 移除現有對話框
    this.hideAuthDialog()

    const dialog = document.createElement('div')
    dialog.id = 'auth-dialog'
    dialog.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
    dialog.innerHTML = `
      <div class="bg-base-100 rounded-lg w-full max-w-md mx-4 shadow-2xl">
        <!-- 標籤頁 -->
        <div class="flex border-b border-base-300">
          <button id="login-tab" class="flex-1 py-3 px-4 text-center font-medium transition-colors ${mode === 'login' ? 'text-primary border-b-2 border-primary bg-primary/10' : 'text-base-content/60 hover:text-base-content'}">
            登入
          </button>
          <button id="register-tab" class="flex-1 py-3 px-4 text-center font-medium transition-colors ${mode === 'register' ? 'text-primary border-b-2 border-primary bg-primary/10' : 'text-base-content/60 hover:text-base-content'}">
            註冊
          </button>
          <button onclick="authManager.hideAuthDialog()" class="p-3 text-base-content/40 hover:text-base-content/60">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- 登入表單 -->
        <div id="login-form" class="p-6 ${mode === 'login' ? '' : 'hidden'}">
          <form onsubmit="event.preventDefault(); authManager.login()">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-base-content mb-1">用戶名</label>
                <input 
                  type="text" 
                  id="login-username"
                  class="input input-bordered w-full focus:input-primary"
                  placeholder="請輸入用戶名"
                  value="${this.loginForm.username}"
                  oninput="authManager.loginForm.username = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-base-content mb-1">密碼</label>
                <input 
                  type="password" 
                  id="login-password"
                  class="input input-bordered w-full focus:input-primary"
                  placeholder="請輸入密碼"
                  value="${this.loginForm.password}"
                  oninput="authManager.loginForm.password = this.value"
                >
              </div>
              <button 
                type="submit" 
                data-loading="login"
                class="btn btn-primary w-full"
              >
                登入
              </button>
            </div>
          </form>
        </div>

        <!-- 註冊表單 -->
        <div id="register-form" class="p-6 ${mode === 'register' ? '' : 'hidden'}">
          <form onsubmit="event.preventDefault(); authManager.register()">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-base-content mb-1">用戶名</label>
                <input 
                  type="text" 
                  id="register-username"
                  class="input input-bordered w-full focus:input-primary"
                  placeholder="請輸入用戶名（至少3個字符）"
                  value="${this.registerForm.username}"
                  oninput="authManager.registerForm.username = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-base-content mb-1">密碼</label>
                <input 
                  type="password" 
                  id="register-password"
                  class="input input-bordered w-full focus:input-primary"
                  placeholder="請輸入密碼（至少6個字符）"
                  value="${this.registerForm.password}"
                  oninput="authManager.registerForm.password = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-base-content mb-1">確認密碼</label>
                <input 
                  type="password" 
                  id="register-confirm"
                  class="input input-bordered w-full focus:input-primary"
                  placeholder="請再次輸入密碼"
                  value="${this.registerForm.confirmPassword}"
                  oninput="authManager.registerForm.confirmPassword = this.value"
                >
              </div>
              <button 
                type="submit" 
                data-loading="register"
                class="btn btn-success w-full"
              >
                註冊
              </button>
            </div>
          </form>
        </div>
      </div>
    `

    document.body.appendChild(dialog)

    // 綁定標籤切換事件
    document.getElementById('login-tab').onclick = () => this.switchAuthMode('login')
    document.getElementById('register-tab').onclick = () => this.switchAuthMode('register')

    // 設置焦點
    setTimeout(() => {
      const firstInput = dialog.querySelector('input')
      if (firstInput) firstInput.focus()
    }, 100)
  },

  // 切換認證模式
  switchAuthMode(mode) {
    const loginTab = document.getElementById('login-tab')
    const registerTab = document.getElementById('register-tab')
    const loginForm = document.getElementById('login-form')
    const registerForm = document.getElementById('register-form')

    if (mode === 'login') {
      loginTab.className = 'flex-1 py-3 px-4 text-center font-medium transition-colors text-primary border-b-2 border-primary bg-primary/10'
      registerTab.className = 'flex-1 py-3 px-4 text-center font-medium transition-colors text-base-content/60 hover:text-base-content'
      loginForm.classList.remove('hidden')
      registerForm.classList.add('hidden')
      
      // 設置焦點
      setTimeout(() => {
        document.getElementById('login-username').focus()
      }, 100)
    } else {
      loginTab.className = 'flex-1 py-3 px-4 text-center font-medium transition-colors text-base-content/60 hover:text-base-content'
      registerTab.className = 'flex-1 py-3 px-4 text-center font-medium transition-colors text-primary border-b-2 border-primary bg-primary/10'
      loginForm.classList.add('hidden')
      registerForm.classList.remove('hidden')
      
      // 設置焦點
      setTimeout(() => {
        document.getElementById('register-username').focus()
      }, 100)
    }
  },

  // 隱藏認證對話框
  hideAuthDialog() {
    const dialog = document.getElementById('auth-dialog')
    if (dialog) {
      dialog.remove()
    }
  },

  // 顯示密碼修改對話框
  showChangePasswordDialog() {
    // 移除現有對話框
    this.hideChangePasswordDialog()

    const dialog = document.createElement('div')
    dialog.id = 'change-password-dialog'
    dialog.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
    dialog.innerHTML = `
      <div class="bg-base-100 rounded-lg w-full max-w-md mx-4 shadow-2xl">
        <!-- 標題 -->
        <div class="flex justify-between items-center p-6 border-b border-base-300">
          <h3 class="text-xl font-bold">修改密碼</h3>
          <button onclick="authManager.hideChangePasswordDialog()" class="btn btn-ghost btn-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- 表單 -->
        <div class="p-6">
          <form onsubmit="event.preventDefault(); authManager.changePassword()">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-base-content mb-1">當前密碼</label>
                <input 
                  type="password" 
                  id="current-password"
                  class="input input-bordered w-full focus:input-primary"
                  placeholder="請輸入當前密碼"
                  value="${this.changePasswordForm.currentPassword}"
                  oninput="authManager.changePasswordForm.currentPassword = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-base-content mb-1">新密碼</label>
                <input 
                  type="password" 
                  id="new-password"
                  class="input input-bordered w-full focus:input-primary"
                  placeholder="請輸入新密碼"
                  value="${this.changePasswordForm.newPassword}"
                  oninput="authManager.changePasswordForm.newPassword = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-base-content mb-1">確認新密碼</label>
                <input 
                  type="password" 
                  id="confirm-new-password"
                  class="input input-bordered w-full focus:input-primary"
                  placeholder="請再次輸入新密碼"
                  value="${this.changePasswordForm.confirmNewPassword}"
                  oninput="authManager.changePasswordForm.confirmNewPassword = this.value"
                >
              </div>
              <button 
                type="submit" 
                data-loading="changePassword"
                class="btn btn-primary w-full"
              >
                修改密碼
              </button>
            </div>
          </form>
        </div>
      </div>
    `

    document.body.appendChild(dialog)

    // 設置焦點
    setTimeout(() => {
      const firstInput = dialog.querySelector('#current-password')
      if (firstInput) firstInput.focus()
    }, 100)
  },

  // 隱藏密碼修改對話框
  hideChangePasswordDialog() {
    const dialog = document.getElementById('change-password-dialog')
    if (dialog) {
      dialog.remove()
    }
  }
}

// 導出到全局
window.authManager = authManager