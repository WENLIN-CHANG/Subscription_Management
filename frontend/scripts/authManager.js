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
    email: '',
    password: '',
    confirmPassword: ''
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
    if (!this.registerForm.email.trim()) {
      stateManager.error.set('請輸入郵箱地址', '註冊驗證')
      return false
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.registerForm.email)) {
      stateManager.error.set('請輸入有效的郵箱地址', '註冊驗證')
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
          email: this.registerForm.email,
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
      email: '',
      password: '',
      confirmPassword: ''
    }
  },

  // 登入成功回調
  onLoginSuccess() {
    // 隱藏認證對話框
    this.hideAuthDialog()
    
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
      <div class="bg-white rounded-lg w-full max-w-md mx-4">
        <!-- 標籤頁 -->
        <div class="flex border-b">
          <button id="login-tab" class="flex-1 py-3 px-4 text-center font-medium transition-colors ${mode === 'login' ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' : 'text-gray-500 hover:text-gray-700'}">
            登入
          </button>
          <button id="register-tab" class="flex-1 py-3 px-4 text-center font-medium transition-colors ${mode === 'register' ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' : 'text-gray-500 hover:text-gray-700'}">
            註冊
          </button>
          <button onclick="authManager.hideAuthDialog()" class="p-3 text-gray-400 hover:text-gray-600">
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
                <label class="block text-sm font-medium text-gray-700 mb-1">用戶名</label>
                <input 
                  type="text" 
                  id="login-username"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="請輸入用戶名"
                  value="${this.loginForm.username}"
                  oninput="authManager.loginForm.username = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">密碼</label>
                <input 
                  type="password" 
                  id="login-password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="請輸入密碼"
                  value="${this.loginForm.password}"
                  oninput="authManager.loginForm.password = this.value"
                >
              </div>
              <button 
                type="submit" 
                data-loading="login"
                class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
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
                <label class="block text-sm font-medium text-gray-700 mb-1">用戶名</label>
                <input 
                  type="text" 
                  id="register-username"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="請輸入用戶名（至少3個字符）"
                  value="${this.registerForm.username}"
                  oninput="authManager.registerForm.username = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">郵箱</label>
                <input 
                  type="email" 
                  id="register-email"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="請輸入郵箱地址"
                  value="${this.registerForm.email}"
                  oninput="authManager.registerForm.email = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">密碼</label>
                <input 
                  type="password" 
                  id="register-password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="請輸入密碼（至少6個字符）"
                  value="${this.registerForm.password}"
                  oninput="authManager.registerForm.password = this.value"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">確認密碼</label>
                <input 
                  type="password" 
                  id="register-confirm"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="請再次輸入密碼"
                  value="${this.registerForm.confirmPassword}"
                  oninput="authManager.registerForm.confirmPassword = this.value"
                >
              </div>
              <button 
                type="submit" 
                data-loading="register"
                class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors"
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
      loginTab.className = 'flex-1 py-3 px-4 text-center font-medium transition-colors text-blue-600 border-b-2 border-blue-600 bg-blue-50'
      registerTab.className = 'flex-1 py-3 px-4 text-center font-medium transition-colors text-gray-500 hover:text-gray-700'
      loginForm.classList.remove('hidden')
      registerForm.classList.add('hidden')
      
      // 設置焦點
      setTimeout(() => {
        document.getElementById('login-username').focus()
      }, 100)
    } else {
      loginTab.className = 'flex-1 py-3 px-4 text-center font-medium transition-colors text-gray-500 hover:text-gray-700'
      registerTab.className = 'flex-1 py-3 px-4 text-center font-medium transition-colors text-blue-600 border-b-2 border-blue-600 bg-blue-50'
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
  }
}

// 導出到全局
window.authManager = authManager