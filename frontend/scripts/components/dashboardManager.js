// 儀表板管理器 - 負責儀表板顯示和預算管理
import { budgetManager } from '../business/budgetManager.js'
import { statisticsManager } from '../business/statisticsManager.js'
import { calculationUtils } from '../utils/calculationUtils.js'
import { authManager } from '../auth/authManager.js'
import { themeManager } from '../ui/themeManager.js'

export function dashboardManager() {
  return {
    // 獲取全局狀態
    get subscriptions() {
      return this.$store.app.subscriptions
    },
    
    get monthlyTotal() {
      return this.$store.app.monthlyTotal
    },
    
    get monthlyBudget() {
      return this.$store.app.monthlyBudget
    },
    
    get isLoggedIn() {
      return this.$store.app.isLoggedIn
    },
    
    get currentUser() {
      return this.$store.app.currentUser
    },
    
    get currentTheme() {
      return this.$store.app.currentTheme
    },
    
    get showBudgetSetting() {
      return this.$store.app.showBudgetSetting
    },
    
    get tempBudget() {
      return this.$store.app.tempBudget
    },
    
    set tempBudget(value) {
      this.$store.app.tempBudget = value
    },
    
    // 預算管理方法
    openBudgetSetting() {
      if (!this.isLoggedIn) {
        authManager.showAuthDialog('login')
        return
      }
      this.$store.app.openBudgetSetting()
    },
    
    closeBudgetSetting() {
      this.$store.app.closeBudgetSetting()
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
    
    // 格式化方法
    formatCurrency(amount) {
      return calculationUtils.formatCurrency(amount)
    },
    
    formatNumber(number) {
      return calculationUtils.formatNumber(number)
    },
    
    // 主題相關方法
    getCurrentThemeType() {
      return themeManager.getCurrentThemeType()
    },
    
    toggleTheme() {
      if (themeManager.toggleTheme()) {
        this.$store.app.setTheme(themeManager.currentTheme)
      }
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
    }
  }
}