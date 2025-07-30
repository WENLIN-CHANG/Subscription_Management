// 數據管理模塊 - 處理本地存儲操作
export const dataManager = {
  // 訂閱數據存儲
  saveSubscriptions(subscriptions) {
    localStorage.setItem('subscriptions', JSON.stringify(subscriptions))
  },

  loadSubscriptions() {
    const stored = localStorage.getItem('subscriptions')
    return stored ? JSON.parse(stored) : []
  },

  // 預算數據存儲
  saveBudget(budget) {
    localStorage.setItem('monthlyBudget', budget.toString())
  },

  loadBudget() {
    const stored = localStorage.getItem('monthlyBudget')
    return stored ? parseFloat(stored) : 0
  }
}