// 狀態管理模塊 - 處理載入狀態、錯誤狀態和通知
export const stateManager = {
  // 載入狀態管理
  loading: {
    states: new Map(),
    timers: new Map(),
    
    // 設置載入狀態
    set(key, isLoading, options = {}) {
      const { 
        minDuration = 300, // 最小顯示時間，避免閨爍
        showSpinner = true,
        showOverlay = false,
        message = '載入中...'
      } = options
      
      if (isLoading) {
        this.states.set(key, { 
          isLoading: true, 
          startTime: Date.now(),
          options: { showSpinner, showOverlay, message }
        })
        this.updateUI(key, true, { showSpinner, showOverlay, message })
      } else {
        const state = this.states.get(key)
        if (state) {
          const elapsed = Date.now() - state.startTime
          const remainingTime = Math.max(0, minDuration - elapsed)
          
          if (remainingTime > 0) {
            // 延遲關閉，確保最小顯示時間
            setTimeout(() => {
              this.states.set(key, { isLoading: false })
              this.updateUI(key, false)
            }, remainingTime)
          } else {
            this.states.set(key, { isLoading: false })
            this.updateUI(key, false)
          }
        }
      }
    },
    
    // 獲取載入狀態
    get(key) {
      const state = this.states.get(key)
      return state ? state.isLoading : false
    },
    
    // 更新 UI 載入狀態
    updateUI(key, isLoading, options = {}) {
      // 更新按鈕和表單元素
      const loadingElements = document.querySelectorAll(`[data-loading="${key}"]`)
      loadingElements.forEach(element => {
        if (isLoading) {
          element.classList.add('loading')
          element.disabled = true
          
          // 添加載入指示器
          if (options.showSpinner && !element.querySelector('.loading-spinner')) {
            this.addSpinner(element)
          }
        } else {
          element.classList.remove('loading')
          element.disabled = false
          
          // 移除載入指示器
          this.removeSpinner(element)
        }
      })
      
      // 更新獨立的載入指示器
      const indicators = document.querySelectorAll(`[data-loading-indicator="${key}"]`)
      indicators.forEach(indicator => {
        indicator.style.display = isLoading ? 'flex' : 'none'
        if (isLoading && options.message) {
          const messageEl = indicator.querySelector('.loading-message')
          if (messageEl) {
            messageEl.textContent = options.message
          }
        }
      })
      
      // 全局載入遮罩
      if (options.showOverlay) {
        this.toggleGlobalLoading(isLoading, options.message)
      }
    },
    
    // 添加載入旋轉器
    addSpinner(element) {
      const spinner = document.createElement('div')
      spinner.className = 'loading-spinner'
      spinner.innerHTML = `
        <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      `
      element.appendChild(spinner)
    },
    
    // 移除載入旋轉器
    removeSpinner(element) {
      const spinner = element.querySelector('.loading-spinner')
      if (spinner) {
        spinner.remove()
      }
    },
    
    // 切換全局載入遮罩
    toggleGlobalLoading(show, message = '載入中...') {
      let overlay = document.getElementById('global-loading-overlay')
      
      if (show) {
        if (!overlay) {
          overlay = document.createElement('div')
          overlay.id = 'global-loading-overlay'
          overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
          overlay.setAttribute('data-testid', 'global-loading-overlay')
          overlay.innerHTML = `
            <div class="bg-base-100 rounded-lg p-6 shadow-xl">
              <div class="flex items-center space-x-3">
                <div class="loading-spinner">
                  <svg class="animate-spin h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <span class="loading-message text-lg">${message}</span>
              </div>
            </div>
          `
          document.body.appendChild(overlay)
        } else {
          const messageEl = overlay.querySelector('.loading-message')
          if (messageEl) {
            messageEl.textContent = message
          }
          overlay.style.display = 'flex'
        }
      } else {
        if (overlay) {
          overlay.style.display = 'none'
        }
      }
    }
  },

  // 錯誤處理管理
  error: {
    current: null,
    history: [],
    
    // 設置錯誤
    set(error, context = '') {
      let message = error
      let errorType = 'unknown'
      let severity = 'error'
      
      // 處理不同類型的錯誤
      if (error instanceof Error) {
        message = error.message
        errorType = error.name || 'Error'
      } else if (typeof error === 'object') {
        if (error.response) {
          // HTTP 錯誤
          errorType = 'HTTPError'
          severity = error.response.status >= 500 ? 'critical' : 'error'
          message = error.response.data?.message || error.message || `HTTP ${error.response.status}: ${error.response.statusText}`
        } else {
          message = error.message || error.detail || JSON.stringify(error)
        }
      } else if (typeof error === 'string') {
        message = error
      } else {
        message = String(error)
      }
      
      const errorData = {
        message,
        context,
        type: errorType,
        severity,
        timestamp: new Date(),
        stack: error instanceof Error ? error.stack : null
      }
      
      this.current = errorData
      this.history.push(errorData)
      
      // 保持歷史記錄在合理範圍內
      if (this.history.length > 50) {
        this.history = this.history.slice(-30)
      }
      
      console.error(`[${context}] ${severity.toUpperCase()}:`, error)
      
      // 關鍵錯誤需要特殊處理
      if (severity === 'critical') {
        this.handleCriticalError(errorData)
      } else {
        this.showError(errorData)
      }
    },
    
    // 清除錯誤
    clear() {
      this.current = null
      this.hideError()
    },
    
    // 處理關鍵錯誤
    handleCriticalError(error) {
      // 關鍵錯誤需要特殊處理，例如更長時間顯示、日誌上傳等
      this.showError(error, 10000) // 10秒顯示
      
      // 可以在這裡添加日誌上傳逻輯
      this.logError(error)
    },
    
    // 記錄錯誤日誌
    logError(error) {
      // 可以在這裡實現日誌上傳逻輯
      console.group(`🔴 Critical Error [${error.context}]`)
      console.error('Message:', error.message)
      console.error('Stack:', error.stack)
      console.error('Timestamp:', error.timestamp)
      console.groupEnd()
    },
    
    // 顯示錯誤訊息
    showError(error, duration = 3000) {
      // 移除現有錯誤提示
      this.hideError()
      
      // 根據嚴重程度選擇樣式
      const alertClass = this.getAlertClass(error.severity)
      const iconSvg = this.getErrorIcon(error.severity)
      
      // 創建錯誤提示元素
      const errorAlert = document.createElement('div')
      errorAlert.id = 'error-alert'
      errorAlert.className = `alert ${alertClass} fixed top-4 right-4 z-50 max-w-md shadow-lg`
      errorAlert.setAttribute('data-testid', 'error-alert')
      
      const contextText = error.context ? `[${error.context}] ` : ''
      const severityBadge = error.severity !== 'error' ? `<span class="badge badge-xs ml-2">${error.severity}</span>` : ''
      
      errorAlert.innerHTML = `
        <div class="flex">
          ${iconSvg}
          <div class="ml-3 flex-1">
            <div class="text-sm font-medium">
              ${contextText}${error.message}${severityBadge}
            </div>
            ${error.type !== 'unknown' ? `<div class="text-xs opacity-75 mt-1">${error.type}</div>` : ''}
          </div>
          <div class="ml-auto pl-3">
            <div class="-mx-1.5 -my-1.5">
              <button type="button" onclick="stateManager.error.clear()" class="btn btn-ghost btn-xs" data-testid="close-error-btn">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      `
      
      document.body.appendChild(errorAlert)
      
      // 根據嚴重程度自動隱藏
      if (duration > 0) {
        setTimeout(() => {
          if (document.getElementById('error-alert')) {
            this.clear()
          }
        }, duration)
      }
    },
    
    // 獲取警告樣式
    getAlertClass(severity) {
      switch (severity) {
        case 'critical': return 'alert-error'
        case 'error': return 'alert-error'
        case 'warning': return 'alert-warning'
        case 'info': return 'alert-info'
        default: return 'alert-error'
      }
    },
    
    // 獲取錯誤圖示
    getErrorIcon(severity) {
      switch (severity) {
        case 'critical':
          return `<svg class="flex-shrink-0 w-5 h-5 text-error" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
          </svg>`
        case 'warning':
          return `<svg class="flex-shrink-0 w-4 h-4 text-warning" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
          </svg>`
        default:
          return `<svg class="flex-shrink-0 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>`
      }
    },
    
    // 隱藏錯誤訊息
    hideError() {
      const existingAlert = document.getElementById('error-alert')
      if (existingAlert) {
        existingAlert.remove()
      }
    },
    
    // 獲取錯誤歷史
    getHistory() {
      return [...this.history]
    },
    
    // 清除錯誤歷史
    clearHistory() {
      this.history = []
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
      successContext = key,
      loadingMessage = '載入中...',
      showOverlay = false,
      minDuration = 300
    } = options
    
    try {
      this.loading.set(key, true, { 
        message: loadingMessage, 
        showOverlay,
        minDuration
      })
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
        opacity: 0.7;
      }
      
      .loading .loading-spinner {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1000;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .animate-spin {
        animation: spin 1s linear infinite;
      }
      
      .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
        backdrop-filter: blur(2px);
      }
      
      .loading-spinner {
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
      
      /* 按鈕載入狀態 */
      .btn.loading {
        background-color: var(--btn-color, currentColor);
        cursor: not-allowed;
      }
      
      .btn.loading .loading-spinner {
        position: static;
        transform: none;
        margin-right: 8px;
      }
      
      /* 全局載入遮罩動畫 */
      #global-loading-overlay {
        animation: fadeIn 0.2s ease-out;
      }
      
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      
      /* 載入指示器樣式 */
      [data-loading-indicator] {
        display: none;
        align-items: center;
        justify-content: center;
        padding: 1rem;
      }
      
      .loading-message {
        margin-left: 0.5rem;
        font-size: 0.875rem;
        color: var(--text-color, currentColor);
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