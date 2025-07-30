// API 客戶端 - 處理與後端的通信
export const apiClient = {
  baseURL: '/api',
  token: null,

  // 設置認證令牌
  setToken(token) {
    this.token = token
    localStorage.setItem('auth_token', token)
  },

  // 獲取認證令牌
  getToken() {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token')
    }
    return this.token
  },

  // 清除認證令牌
  clearToken() {
    this.token = null
    localStorage.removeItem('auth_token')
  },

  // 通用請求方法
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const token = this.getToken()
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    }

    const config = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers
      }
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }

    try {
      const response = await fetch(url, config)
      
      if (response.status === 401) {
        // 認證失敗，清除令牌
        this.clearToken()
        throw new Error('請重新登入')
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '請求失敗' }))
        throw new Error(error.detail || '請求失敗')
      }

      // 處理無內容響應
      if (response.status === 204) {
        return null
      }

      return await response.json()
    } catch (error) {
      console.error('API 請求錯誤:', error)
      throw error
    }
  },

  // 用戶認證 API
  auth: {
    // 用戶註冊
    async register(userData) {
      return await apiClient.request('/auth/register', {
        method: 'POST',
        body: userData
      })
    },

    // 用戶登入
    async login(credentials) {
      const response = await apiClient.request('/auth/login', {
        method: 'POST',
        body: credentials
      })
      
      if (response.access_token) {
        apiClient.setToken(response.access_token)
      }
      
      return response
    },

    // 獲取當前用戶信息
    async getCurrentUser() {
      return await apiClient.request('/auth/me')
    },

    // 登出
    logout() {
      apiClient.clearToken()
    }
  },

  // 訂閱管理 API
  subscriptions: {
    // 獲取所有訂閱
    async getAll() {
      return await apiClient.request('/subscriptions/')
    },

    // 創建訂閱
    async create(subscriptionData) {
      return await apiClient.request('/subscriptions/', {
        method: 'POST',
        body: subscriptionData
      })
    },

    // 獲取單個訂閱
    async getById(id) {
      return await apiClient.request(`/subscriptions/${id}`)
    },

    // 更新訂閱
    async update(id, updateData) {
      return await apiClient.request(`/subscriptions/${id}`, {
        method: 'PUT',
        body: updateData
      })
    },

    // 刪除訂閱
    async delete(id) {
      return await apiClient.request(`/subscriptions/${id}`, {
        method: 'DELETE'
      })
    }
  },

  // 預算管理 API
  budget: {
    // 獲取預算
    async get() {
      return await apiClient.request('/budget/')
    },

    // 設置預算
    async set(budgetData) {
      return await apiClient.request('/budget/', {
        method: 'POST',
        body: budgetData
      })
    },

    // 更新預算
    async update(budgetData) {
      return await apiClient.request('/budget/', {
        method: 'PUT',
        body: budgetData
      })
    }
  }
}