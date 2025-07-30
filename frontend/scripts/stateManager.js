// 狀態管理模塊 - 處理載入狀態、錯誤狀態和通知
export const stateManager = {
  // 載入狀態管理
  loading: {
    states: new Map(),
    
    // 設置載入狀態
    set(key, isLoading) {
      this.states.set(key, isLoading)
      this.updateUI(key, isLoading)
    },
    
    // 獲取載入狀態
    get(key) {
      return this.states.get(key) || false
    },
    
    // 更新 UI 載入狀態
    updateUI(key, isLoading) {
      const loadingElements = document.querySelectorAll(`[data-loading="${key}"]`)
      loadingElements.forEach(element => {
        if (isLoading) {
          element.classList.add('loading')
          element.disabled = true
        } else {
          element.classList.remove('loading')
          element.disabled = false
        }
      })
      
      // 更新載入指示器
      const indicators = document.querySelectorAll(`[data-loading-indicator="${key}"]`)
      indicators.forEach(indicator => {
        indicator.style.display = isLoading ? 'block' : 'none'
      })
    }
  },

  // 錯誤處理管理
  error: {
    current: null,
    
    // 設置錯誤
    set(error, context = '') {
      this.current = {
        message: error.message || error,
        context,
        timestamp: new Date()
      }
      
      console.error(`[${context}] 錯誤:`, error)
      this.showError(this.current)
    },
    
    // 清除錯誤
    clear() {
      this.current = null
      this.hideError()
    },
    
    // 顯示錯誤訊息
    showError(error) {
      // 移除現有錯誤提示
      this.hideError()
      
      // 創建錯誤提示元素
      const errorAlert = document.createElement('div')
      errorAlert.id = 'error-alert'
      errorAlert.className = 'alert alert-error fixed top-4 right-4 z-50 max-w-md shadow-lg'
      errorAlert.innerHTML = `
        <div class="flex">
          <svg class="flex-shrink-0 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
          <div class="ml-3">
            <div class="text-sm font-medium text-red-800">
              ${error.context ? `[${error.context}] ` : ''}${error.message}
            </div>
          </div>
          <div class="ml-auto pl-3">
            <div class="-mx-1.5 -my-1.5">
              <button type="button" onclick="stateManager.error.clear()" class="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100">
                <span class="sr-only">關閉</span>
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      `
      
      document.body.appendChild(errorAlert)
      
      // 3秒後自動隱藏
      setTimeout(() => {
        if (document.getElementById('error-alert')) {
          this.clear()
        }
      }, 3000)
    },
    
    // 隱藏錯誤訊息
    hideError() {
      const existingAlert = document.getElementById('error-alert')
      if (existingAlert) {
        existingAlert.remove()
      }
    }
  },

  // 成功通知管理
  success: {
    // 顯示成功訊息
    show(message, context = '') {
      // 移除現有成功提示
      this.hide()
      
      const successAlert = document.createElement('div')
      successAlert.id = 'success-alert'
      successAlert.className = 'alert alert-success fixed top-4 right-4 z-50 max-w-md shadow-lg'
      successAlert.innerHTML = `
        <div class="flex">
          <svg class="flex-shrink-0 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
          </svg>
          <div class="ml-3">
            <div class="text-sm font-medium text-green-800">
              ${context ? `[${context}] ` : ''}${message}
            </div>
          </div>
          <div class="ml-auto pl-3">
            <div class="-mx-1.5 -my-1.5">
              <button type="button" onclick="stateManager.success.hide()" class="inline-flex bg-green-50 rounded-md p-1.5 text-green-500 hover:bg-green-100">
                <span class="sr-only">關閉</span>
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      `
      
      document.body.appendChild(successAlert)
      
      // 2秒後自動隱藏
      setTimeout(() => {
        this.hide()
      }, 2000)
    },
    
    // 隱藏成功訊息
    hide() {
      const existingAlert = document.getElementById('success-alert')
      if (existingAlert) {
        existingAlert.remove()
      }
    }
  },

  // 包裝異步操作的通用方法
  async withLoading(key, asyncFn, options = {}) {
    const { 
      errorContext = key, 
      successMessage = null,
      successContext = key 
    } = options
    
    try {
      this.loading.set(key, true)
      this.error.clear()
      
      const result = await asyncFn()
      
      if (successMessage) {
        this.success.show(successMessage, successContext)
      }
      
      return result
    } catch (error) {
      this.error.set(error, errorContext)
      throw error
    } finally {
      this.loading.set(key, false)
    }
  },

  // 初始化狀態管理器
  init() {
    // 將 stateManager 設為全局變量，方便在 HTML 中使用
    window.stateManager = this
    
    // 添加全局樣式
    const style = document.createElement('style')
    style.textContent = `
      .loading {
        position: relative;
        pointer-events: none;
      }
      
      .loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin: -10px 0 0 -10px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        z-index: 1000;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
      }
      
      .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
    `
    document.head.appendChild(style)
    
    console.log('狀態管理器初始化完成')
  }
}

// 自動初始化
document.addEventListener('DOMContentLoaded', () => {
  stateManager.init()
})