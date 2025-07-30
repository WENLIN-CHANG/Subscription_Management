// 計算工具模塊 - 價格計算、日期計算、格式化工具
export const calculationUtils = {
  // 獲取月費用
  getMonthlyPrice(subscription) {
    const price = parseFloat(subscription.price)
    switch (subscription.cycle) {
      case 'monthly':
        return price
      case 'quarterly':
        return price / 3
      case 'yearly':
        return price / 12
      default:
        return price
    }
  },

  // 獲取週期名稱
  getCycleName(cycle) {
    const names = {
      monthly: '每月',
      quarterly: '每季',
      yearly: '每年'
    }
    return names[cycle] || cycle
  },

  // 格式化日期
  formatDate(dateString) {
    if (!dateString) return 'N/A'
    
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString)
      return 'Invalid Date'
    }
    
    return date.toLocaleDateString('zh-TW')
  },

  // 獲取下次付款日期
  getNextPaymentDate(subscription) {
    if (!subscription.startDate) return 'N/A'
    
    const startDate = new Date(subscription.startDate)
    if (isNaN(startDate.getTime())) {
      console.warn('Invalid start date:', subscription.startDate)
      return 'Invalid Date'
    }
    
    const today = new Date()
    let nextDate = new Date(startDate)
    
    switch (subscription.cycle) {
      case 'monthly':
        while (nextDate <= today) {
          nextDate.setMonth(nextDate.getMonth() + 1)
        }
        break
      case 'quarterly':
        while (nextDate <= today) {
          nextDate.setMonth(nextDate.getMonth() + 3)
        }
        break
      case 'yearly':
        while (nextDate <= today) {
          nextDate.setFullYear(nextDate.getFullYear() + 1)
        }
        break
      default:
        return 'N/A'
    }
    
    return nextDate.toLocaleDateString('zh-TW')
  },

  // 計算距離下次付款的天數
  getDaysUntilPayment(subscription) {
    if (!subscription.startDate) return 0
    
    const startDate = new Date(subscription.startDate)
    if (isNaN(startDate.getTime())) {
      console.warn('Invalid start date for days calculation:', subscription.startDate)
      return 0
    }
    
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    let nextDate = new Date(startDate)
    
    switch (subscription.cycle) {
      case 'monthly':
        while (nextDate <= today) {
          nextDate.setMonth(nextDate.getMonth() + 1)
        }
        break
      case 'quarterly':
        while (nextDate <= today) {
          nextDate.setMonth(nextDate.getMonth() + 3)
        }
        break
      case 'yearly':
        while (nextDate <= today) {
          nextDate.setFullYear(nextDate.getFullYear() + 1)
        }
        break
      default:
        return 0
    }
    
    const diffTime = nextDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays >= 0 ? diffDays : 0
  },

  // 格式化貨幣顯示
  formatCurrency(amount) {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  },

  // 格式化數字（千分位分隔符）
  formatNumber(number) {
    return new Intl.NumberFormat('zh-TW').format(number)
  }
}