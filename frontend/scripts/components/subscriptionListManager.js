// 訂閱列表管理器 - 負責訂閱項目的顯示和操作
import { subscriptionActions } from '../business/subscriptionActions.js'
import { calculationUtils } from '../utils/calculationUtils.js'
import { uiUtils } from '../ui/uiUtils.js'

export function subscriptionListManager() {
  return {
    // 獲取全局狀態
    get subscriptions() {
      return this.$store.app.subscriptions
    },
    
    get isLoggedIn() {
      return this.$store.app.isLoggedIn
    },
    
    // 訂閱操作方法
    editSubscription(id) {
      subscriptionActions.editSubscription(this, id)
    },
    
    deleteSubscription(id) {
      subscriptionActions.deleteSubscription(this, id)
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
    
    // 導航功能
    scrollToAddForm() {
      if (!this.isLoggedIn) {
        const { authManager } = window
        if (authManager) {
          authManager.showAuthDialog('login')
        }
        return
      }
      
      const formElement = document.querySelector('form')
      if (formElement) {
        formElement.scrollIntoView({ behavior: 'smooth' })
        const firstInput = formElement.querySelector('input')
        if (firstInput) {
          setTimeout(() => firstInput.focus(), 500)
        }
      }
    }
  }
}