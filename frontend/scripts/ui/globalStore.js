// 全局狀態管理 - 使用 Alpine.js store
export function initializeGlobalStore(Alpine) {
  // 主要應用狀態
  Alpine.store('app', {
    // 數據狀態
    subscriptions: [],
    monthlyTotal: 0,
    monthlyBudget: 0,
    
    // 編輯狀態
    editingSubscription: null,
    isEditing: false,
    
    // 認證狀態
    isLoggedIn: false,
    currentUser: null,
    
    // 主題狀態
    currentTheme: 'corporate',
    
    // UI 狀態
    mobileMenuOpen: false,
    showBudgetSetting: false,
    tempBudget: '',
    
    // 數據更新方法
    setSubscriptions(subscriptions) {
      this.subscriptions = subscriptions
      this.calculateMonthlyTotal()
    },
    
    addSubscription(subscription) {
      this.subscriptions.push(subscription)
      this.calculateMonthlyTotal()
    },
    
    updateSubscription(updatedSubscription) {
      const index = this.subscriptions.findIndex(s => s.id === updatedSubscription.id)
      if (index !== -1) {
        this.subscriptions[index] = updatedSubscription
        this.calculateMonthlyTotal()
      }
    },
    
    removeSubscription(id) {
      this.subscriptions = this.subscriptions.filter(s => s.id !== id)
      this.calculateMonthlyTotal()
    },
    
    calculateMonthlyTotal() {
      const { calculationUtils } = window
      if (!calculationUtils) return
      
      const newTotal = this.subscriptions.reduce((total, subscription) => {
        return total + calculationUtils.getMonthlyPrice(subscription)
      }, 0)
      
      // 數字動畫效果
      const { uiUtils } = window
      if (uiUtils) {
        uiUtils.animateNumber(this.monthlyTotal, newTotal, (value) => {
          this.monthlyTotal = value
        })
      } else {
        this.monthlyTotal = newTotal
      }
    },
    
    // 編輯狀態管理
    startEditing(subscription) {
      this.editingSubscription = { ...subscription }
      this.isEditing = true
    },
    
    stopEditing() {
      this.editingSubscription = null
      this.isEditing = false
    },
    
    // 認證狀態管理
    setAuth(isLoggedIn, user = null) {
      this.isLoggedIn = isLoggedIn
      this.currentUser = user
    },
    
    // 主題管理
    setTheme(theme) {
      this.currentTheme = theme
    },
    
    // UI 狀態管理
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen
    },
    
    closeMobileMenu() {
      this.mobileMenuOpen = false
    },
    
    openBudgetSetting() {
      this.showBudgetSetting = true
      this.tempBudget = this.monthlyBudget.toString()
    },
    
    closeBudgetSetting() {
      this.showBudgetSetting = false
      this.tempBudget = ''
    },
    
    setBudget(budget) {
      this.monthlyBudget = budget
    }
  })
}