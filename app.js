import Alpine from 'alpinejs'
import { dataManager } from './scripts/dataManager.js'
import { calculationUtils } from './scripts/calculationUtils.js'
import { uiUtils } from './scripts/uiUtils.js'
import { subscriptionActions } from './scripts/subscriptionActions.js'
import { budgetManager } from './scripts/budgetManager.js'
import { statisticsManager } from './scripts/statisticsManager.js'
import { stateManager } from './scripts/stateManager.js'
import { migrationManager } from './scripts/migrationManager.js'

// 訂閱管理主要組件
Alpine.data('subscriptionManager', () => ({
  // 數據狀態
  subscriptions: [],
  monthlyTotal: 0,
  newSubscription: {
    name: '',
    price: '',
    cycle: 'monthly',
    category: '',
    startDate: ''
  },
  editingSubscription: null,
  isEditing: false,
  monthlyBudget: 0,
  showBudgetSetting: false,
  tempBudget: '',

  // 初始化
  async init() {
    try {
      // 初始化狀態管理器
      if (!window.stateManager) {
        stateManager.init()
      }
      
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
      
    } catch (error) {
      console.error('初始化失敗:', error)
      stateManager.error.set(error, '初始化')
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
  }
}))

window.Alpine = Alpine
Alpine.start()