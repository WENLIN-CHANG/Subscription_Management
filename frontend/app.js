import Alpine from 'alpinejs'
import { dataManager } from './scripts/dataManager.js'
import { calculationUtils } from './scripts/calculationUtils.js'
import { uiUtils } from './scripts/uiUtils.js'
import { subscriptionActions } from './scripts/subscriptionActions.js'
import { budgetManager } from './scripts/budgetManager.js'
import { statisticsManager } from './scripts/statisticsManager.js'
import { stateManager } from './scripts/stateManager.js'
import { migrationManager } from './scripts/migrationManager.js'
import { authManager } from './scripts/authManager.js'
import { themeManager } from './scripts/themeManager.js'

// 訂閱管理主要組件
Alpine.data('subscriptionManager', () => ({
  // 數據狀態
  subscriptions: [],
  monthlyTotal: 0,
  newSubscription: {
    name: '',
    price: '',  // 這個會由後端計算 (台幣)
    originalPrice: '',  // 原始價格
    currency: 'TWD',  // 預設台幣
    cycle: 'monthly',
    category: '',
    startDate: ''
  },
  editingSubscription: null,
  isEditing: false,
  monthlyBudget: 0,
  showBudgetSetting: false,
  tempBudget: '',
  
  // 認證狀態
  isLoggedIn: false,
  currentUser: null,
  
  // 主題管理狀態
  currentTheme: 'corporate',
  
  // 響應式導航狀態
  mobileMenuOpen: false,

  // 初始化
  async init() {
    try {
      // 初始化狀態管理器
      if (!window.stateManager) {
        stateManager.init()
      }
      
      // 初始化認證狀態
      this.isLoggedIn = await authManager.init()
      this.currentUser = authManager.currentUser
      
      // 初始化主題管理器
      themeManager.init()
      this.currentTheme = themeManager.currentTheme
      
      // 載入數據
      await stateManager.withLoading('init', async () => {
        this.subscriptions = await dataManager.loadSubscriptions()
        this.monthlyBudget = await dataManager.loadBudget()
        this.calculateMonthlyTotal()
      }, {
        errorContext: '初始化',
        successMessage: null // 不顯示成功訊息
      })
      
      // 檢查是否需要數據遷移
      migrationManager.checkAndPromptMigration()
      
      // 檢查是否有需要恢復的表單資料（登入後）
      this.checkAndRestoreFormData()
      
    } catch (error) {
      console.error('初始化失敗:', error)
      stateManager.error.set(error, '初始化')
    }
  },

  // 檢查並恢復表單資料
  checkAndRestoreFormData() {
    if (this.isLoggedIn) {
      const restoreData = localStorage.getItem('restoreSubscriptionForm')
      if (restoreData) {
        try {
          const formData = JSON.parse(restoreData)
          
          // 恢復表單資料
          this.newSubscription = { ...formData }
          
          // 清除恢復資料
          localStorage.removeItem('restoreSubscriptionForm')
          
          // 顯示提示訊息
          stateManager.success.show(`已恢復您之前填寫的「${formData.name}」訂閱資料，您可以直接提交或繼續編輯`, '表單恢復')
          
          // 滾動到表單位置
          setTimeout(() => {
            const formElement = document.querySelector('form')
            if (formElement) {
              formElement.scrollIntoView({ behavior: 'smooth' })
              // 聚焦到提交按鈕
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

  // 訂閱操作方法
  addSubscription() {
    subscriptionActions.addSubscription(this)
  },

  deleteSubscription(id) {
    subscriptionActions.deleteSubscription(this, id)
  },

  editSubscription(id) {
    subscriptionActions.editSubscription(this, id)
  },

  cancelEdit() {
    subscriptionActions.cancelEdit(this)
  },

  updateSubscription() {
    subscriptionActions.updateSubscription(this)
  },

  // 計算月支出總額
  calculateMonthlyTotal() {
    const newTotal = this.subscriptions.reduce((total, subscription) => {
      return total + calculationUtils.getMonthlyPrice(subscription)
    }, 0)
    
    // 數字動畫效果
    uiUtils.animateNumber(this.monthlyTotal, newTotal, (value) => {
      this.monthlyTotal = value
    })
  },

  // 計算工具方法
  getMonthlyPrice(subscription) {
    return calculationUtils.getMonthlyPrice(subscription)
  },

  getCycleName(cycle) {
    return calculationUtils.getCycleName(cycle)
  },

  formatDate(dateString) {
    return calculationUtils.formatDate(dateString)
  },

  getNextPaymentDate(subscription) {
    return calculationUtils.getNextPaymentDate(subscription)
  },

  getDaysUntilPayment(subscription) {
    return calculationUtils.getDaysUntilPayment(subscription)
  },

  formatCurrency(amount) {
    return calculationUtils.formatCurrency(amount)
  },

  formatNumber(number) {
    return calculationUtils.formatNumber(number)
  },

  formatOriginalCurrency(amount, currency) {
    return calculationUtils.formatOriginalCurrency(amount, currency)
  },

  // UI 工具方法
  getCategoryName(category) {
    return uiUtils.getCategoryName(category)
  },

  getCategoryIcon(category) {
    return uiUtils.getCategoryIcon(category)
  },

  getCategoryColor(category) {
    return uiUtils.getCategoryColor(category)
  },

  getCategoryBgColor(category) {
    return uiUtils.getCategoryBgColor(category)
  },

  getCategoryProgressColor(category) {
    return uiUtils.getCategoryProgressColor(category)
  },

  getExpiryWarningClass(subscription) {
    return uiUtils.getExpiryWarningClass(subscription)
  },

  getExpiryWarningText(subscription) {
    return uiUtils.getExpiryWarningText(subscription)
  },

  // 預算管理方法
  openBudgetSetting() {
    budgetManager.openBudgetSetting(this)
  },

  closeBudgetSetting() {
    budgetManager.closeBudgetSetting(this)
  },

  saveBudget() {
    budgetManager.saveBudget(this)
  },

  getBudgetUsagePercentage() {
    return budgetManager.getBudgetUsagePercentage(this)
  },

  getBudgetStatus() {
    return budgetManager.getBudgetStatus(this)
  },

  getBudgetStatusText() {
    return budgetManager.getBudgetStatusText(this)
  },

  getBudgetStatusColor() {
    return budgetManager.getBudgetStatusColor(this)
  },

  getRemainingBudget() {
    return budgetManager.getRemainingBudget(this)
  },

  // 統計分析方法
  getUpcomingExpiry() {
    return statisticsManager.getUpcomingExpiry(this.subscriptions)
  },

  getCategoryStats() {
    return statisticsManager.getCategoryStats(this.subscriptions)
  },

  // 認證相關方法
  showLogin() {
    authManager.showAuthDialog('login')
  },

  showRegister() {
    authManager.showAuthDialog('register')
  },

  logout() {
    authManager.logout()
  },

  showChangePasswordDialog() {
    authManager.showChangePasswordDialog()
  },

  // 主題管理方法
  changeTheme(themeName) {
    if (themeManager.setTheme(themeName)) {
      this.currentTheme = themeManager.currentTheme
    }
  },

  toggleTheme() {
    if (themeManager.toggleTheme()) {
      this.currentTheme = themeManager.currentTheme
    }
  },

  getCurrentThemeType() {
    return themeManager.getCurrentThemeType()
  },

  getAvailableThemes() {
    return themeManager.getAvailableThemes()
  },

  // 響應式導航方法
  toggleMobileMenu() {
    this.mobileMenuOpen = !this.mobileMenuOpen
  },

  closeMobileMenu() {
    this.mobileMenuOpen = false
  },

  // 選單項目點擊時關閉選單並滾動到指定區域
  navigateAndCloseMobile(sectionId) {
    this.closeMobileMenu()
    this.scrollToSection(sectionId)
  },

  getCurrentThemeInfo() {
    return themeManager.getCurrentThemeInfo()
  },

  isDarkTheme() {
    return themeManager.isDarkTheme()
  },

  isLightTheme() {
    return themeManager.isLightTheme()
  },

  // 導航滾動功能
  scrollToSection(sectionId) {
    // 如果是未登入用戶且點擊需要登入的功能，顯示登入提示
    if (!this.isLoggedIn && (sectionId === 'subscriptions')) {
      this.showLogin()
      return
    }
    
    const element = document.getElementById(sectionId)
    if (element) {
      // 考慮固定導航欄的高度 (約80px)
      const navbarHeight = 80
      const elementPosition = element.offsetTop - navbarHeight
      
      window.scrollTo({
        top: elementPosition,
        behavior: 'smooth'
      })
    }
  },

  // 範例資料相關方法
  isSampleDataMode() {
    return dataManager.isSampleDataMode()
  },

  getSampleDataInfo() {
    return dataManager.getSampleDataInfo()
  }
}))

window.Alpine = Alpine
Alpine.start()