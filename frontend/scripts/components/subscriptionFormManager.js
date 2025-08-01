// 訂閱表單管理器 - 負責新增和編輯訂閱的表單邏輯
import { subscriptionActions } from '../business/subscriptionActions.js'
import { dataManager } from '../data/dataManager.js'

export function subscriptionFormManager() {
  return {
    // 表單狀態
    newSubscription: {
      name: '',
      price: '',
      originalPrice: '',
      currency: 'TWD',
      cycle: 'monthly',
      category: '',
      startDate: ''
    },
    
    // 驗證狀態
    validationErrors: {},
    isValidating: false,
    
    // 獲取全局狀態
    get isLoggedIn() {
      return this.$store.app.isLoggedIn
    },
    
    get isEditing() {
      return this.$store.app.isEditing
    },
    
    get editingSubscription() {
      return this.$store.app.editingSubscription
    },
    
    // 初始化方法
    init() {
      // 如果處於編輯狀態，填充表單
      if (this.isEditing && this.editingSubscription) {
        this.newSubscription = { ...this.editingSubscription }
      }
      
      // 監聽編輯狀態變化
      this.$watch('$store.app.isEditing', (isEditing) => {
        if (isEditing && this.$store.app.editingSubscription) {
          this.newSubscription = { ...this.$store.app.editingSubscription }
        } else {
          this.resetForm()
        }
      })
    },
    
    // 表單操作方法
    addSubscription() {
      if (!this.isLoggedIn) {
        // 保存表單資料以便登入後恢復
        this.saveFormDataForRestore()
        const { authManager } = window
        if (authManager) {
          authManager.showAuthDialog('login')
        }
        return
      }
      
      try {
        this.validateForm()
        this.clearValidationErrors()
        subscriptionActions.addSubscription(this)
      } catch (error) {
        this.handleValidationError(error)
      }
    },
    
    updateSubscription() {
      try {
        this.validateForm()
        this.clearValidationErrors()
        subscriptionActions.updateSubscription(this)
      } catch (error) {
        this.handleValidationError(error)
      }
    },
    
    cancelEdit() {
      subscriptionActions.cancelEdit(this)
    },
    
    resetForm() {
      this.newSubscription = {
        name: '',
        price: '',
        originalPrice: '',
        currency: 'TWD',
        cycle: 'monthly',
        category: '',
        startDate: ''
      }
    },
    
    // 保存表單資料以便登入後恢復
    saveFormDataForRestore() {
      // 只有當表單有內容時才保存
      if (this.newSubscription.name.trim() || this.newSubscription.originalPrice) {
        localStorage.setItem('restoreSubscriptionForm', JSON.stringify(this.newSubscription))
      }
    },
    
    // 檢查並恢復表單資料
    checkAndRestoreFormData() {
      if (this.isLoggedIn) {
        const restoreData = localStorage.getItem('restoreSubscriptionForm')
        if (restoreData) {
          try {
            const formData = JSON.parse(restoreData)
            this.newSubscription = { ...formData }
            localStorage.removeItem('restoreSubscriptionForm')
            
            // 顯示提示訊息
            const { stateManager } = window
            if (stateManager) {
              stateManager.success.show(
                `已恢復您之前填寫的「${formData.name}」訂閱資料，您可以直接提交或繼續編輯`, 
                '表單恢復'
              )
            }
            
            // 滾動到表單位置
            setTimeout(() => {
              const formElement = document.querySelector('form')
              if (formElement) {
                formElement.scrollIntoView({ behavior: 'smooth' })
                const submitButton = formElement.querySelector('button[type="submit"]')
                if (submitButton) {
                  submitButton.focus()
                }
              }
            }, 1000)
            
          } catch (error) {
            console.error('恢復表單資料失敗:', error)
            localStorage.removeItem('restoreSubscriptionForm')
          }
        }
      }
    },
    
    // 表單驗證
    validateForm() {
      const { name, originalPrice, category, startDate, currency, cycle } = this.newSubscription
      const errors = []
      
      // 服務名稱驗證
      if (!name || !name.trim()) {
        errors.push('請輸入服務名稱')
      } else if (name.trim().length < 2) {
        errors.push('服務名稱至少需要 2 個字符')
      } else if (name.trim().length > 50) {
        errors.push('服務名稱不能超過 50 個字符')
      }
      
      // 價格驗證
      if (!originalPrice) {
        errors.push('請輸入價格')
      } else {
        const price = parseFloat(originalPrice)
        if (isNaN(price)) {
          errors.push('價格必須是有效數字')
        } else if (price <= 0) {
          errors.push('價格必須大於 0')
        } else if (price > 999999) {
          errors.push('價格不能超過 999,999')
        }
      }
      
      // 貨幣驗證
      if (!currency) {
        errors.push('請選擇貨幣')
      } else if (!['TWD', 'USD'].includes(currency)) {
        errors.push('不支援的貨幣類型')
      }
      
      // 訂閱週期驗證
      if (!cycle) {
        errors.push('請選擇訂閱週期')
      } else if (!['monthly', 'quarterly', 'yearly'].includes(cycle)) {
        errors.push('不支援的訂閱週期')
      }
      
      // 分類驗證
      if (!category) {
        errors.push('請選擇服務分類')
      } else {
        const validCategories = ['streaming', 'software', 'news', 'gaming', 'music', 'education', 'productivity', 'other']
        if (!validCategories.includes(category)) {
          errors.push('不支援的服務分類')
        }
      }
      
      // 開始日期驗證
      if (!startDate) {
        errors.push('請選擇開始日期')
      } else {
        const date = new Date(startDate)
        const today = new Date()
        const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate())
        const oneYearFromNow = new Date(today.getFullYear() + 1, today.getMonth(), today.getDate())
        
        if (isNaN(date.getTime())) {
          errors.push('無效的日期格式')
        } else if (date < oneYearAgo) {
          errors.push('開始日期不能超過一年前')
        } else if (date > oneYearFromNow) {
          errors.push('開始日期不能超過一年後')
        }
      }
      
      if (errors.length > 0) {
        throw new Error(errors.join(', '))
      }
      
      return true
    },
    
    // 驗證相關方法
    clearValidationErrors() {
      this.validationErrors = {}
    },
    
    handleValidationError(error) {
      const { stateManager } = window
      if (stateManager) {
        stateManager.error.set(error.message, '表單驗證')
      }
      
      // 找到第一個錯誤欄位並聚焦
      setTimeout(() => {
        const firstErrorField = this.getFirstErrorField()
        if (firstErrorField) {
          firstErrorField.focus()
          firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 100)
    },
    
    getFirstErrorField() {
      const fieldOrder = ['name', 'originalPrice', 'currency', 'cycle', 'category', 'startDate']
      
      for (const field of fieldOrder) {
        const element = document.querySelector(`[data-testid="subscription-${field.toLowerCase()}-input"], [data-testid="subscription-${field.toLowerCase()}-select"]`)
        if (element) {
          return element
        }
      }
      
      return null
    },

    // 樣本資料相關
    isSampleDataMode() {
      return dataManager.isSampleDataMode()
    },
    
    getSampleDataInfo() {
      return dataManager.getSampleDataInfo()
    }
  }
}