// 統計分析模塊 - 統計分析和到期提醒
import { calculationUtils } from '../utils/calculationUtils.js'
import { uiUtils } from '../ui/uiUtils.js'

export const statisticsManager = {
  // 獲取即將到期的訂閱
  getUpcomingExpiry(subscriptions) {
    return subscriptions
      .filter(sub => calculationUtils.getDaysUntilPayment(sub) <= 7)
      .sort((a, b) => calculationUtils.getDaysUntilPayment(a) - calculationUtils.getDaysUntilPayment(b))
  },

  // 獲取分類統計數據
  getCategoryStats(subscriptions) {
    const stats = {}
    let total = 0
    
    subscriptions.forEach(subscription => {
      const monthlyPrice = calculationUtils.getMonthlyPrice(subscription)
      const category = subscription.category
      
      if (!stats[category]) {
        stats[category] = {
          name: uiUtils.getCategoryName(category),
          amount: 0,
          count: 0,
          color: uiUtils.getCategoryBgColor(category),
          progressColor: uiUtils.getCategoryProgressColor(category),
          originalCategory: category
        }
      }
      
      stats[category].amount += monthlyPrice
      stats[category].count += 1
      total += monthlyPrice
    })
    
    // 計算百分比
    Object.keys(stats).forEach(category => {
      stats[category].percentage = total > 0 ? (stats[category].amount / total * 100).toFixed(1) : 0
    })
    
    return Object.values(stats).sort((a, b) => b.amount - a.amount)
  }
}