// UI 工具模塊 - UI 樣式、動畫效果、顏色生成
import { calculationUtils } from './calculationUtils.js'

export const uiUtils = {
  // 獲取分類名稱
  getCategoryName(category) {
    const names = {
      entertainment: '娛樂影音',
      productivity: '生產力工具',
      storage: '雲端存儲',
      fitness: '健身運動',
      education: '教育學習',
      news: '新聞資訊',
      other: '其他'
    }
    return names[category] || category
  },

  // 獲取分類圖標
  getCategoryIcon(category) {
    const icons = {
      entertainment: '🎥',
      productivity: '⚙️',
      storage: '☁️',
      fitness: '🏋️',
      education: '📚',
      news: '📰',
      other: '📋'
    }
    return icons[category] || '📋'
  },

  // 獲取分類顏色
  getCategoryColor(category) {
    const colors = {
      entertainment: 'border-red-400',
      productivity: 'border-blue-400',
      storage: 'border-green-400',
      fitness: 'border-orange-400',
      education: 'border-purple-400',
      news: 'border-yellow-400',
      other: 'border-gray-400'
    }
    return colors[category] || 'border-gray-400'
  },

  // 獲取分類背景顏色
  getCategoryBgColor(category) {
    const colors = {
      entertainment: 'bg-red-100 text-red-800',
      productivity: 'bg-blue-100 text-blue-800',
      storage: 'bg-green-100 text-green-800',
      fitness: 'bg-orange-100 text-orange-800',
      education: 'bg-purple-100 text-purple-800',
      news: 'bg-yellow-100 text-yellow-800',
      other: 'bg-gray-100 text-gray-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  },

  // 獲取分類進度條顏色
  getCategoryProgressColor(category) {
    const colors = {
      entertainment: 'bg-red-400',
      productivity: 'bg-blue-400',
      storage: 'bg-green-400',
      fitness: 'bg-orange-400',
      education: 'bg-purple-400',
      news: 'bg-yellow-400',
      other: 'bg-gray-400'
    }
    return colors[category] || 'bg-gray-400'
  },

  // 獲取到期提醒樣式
  getExpiryWarningClass(subscription) {
    const days = calculationUtils.getDaysUntilPayment(subscription)
    if (days <= 3) {
      return 'text-red-600 font-semibold'
    } else if (days <= 7) {
      return 'text-orange-600 font-medium'
    }
    return 'text-gray-600'
  },

  // 獲取到期提醒文字
  getExpiryWarningText(subscription) {
    const days = calculationUtils.getDaysUntilPayment(subscription)
    if (days <= 0) {
      return '今天到期！'
    } else if (days === 1) {
      return '明天到期'
    } else if (days <= 3) {
      return `${days} 天後到期`
    } else if (days <= 7) {
      return `${days} 天後到期`
    }
    return `${days} 天後`
  },

  // 數字動畫效果
  animateNumber(from, to, callback, duration = 800) {
    const startTime = performance.now()
    const difference = to - from
    
    const step = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // 使用 easeOutCubic 緩動函數
      const easeProgress = 1 - Math.pow(1 - progress, 3)
      const currentValue = from + (difference * easeProgress)
      
      callback(currentValue)
      
      if (progress < 1) {
        requestAnimationFrame(step)
      } else {
        callback(to) // 確保最終值準確
      }
    }
    
    requestAnimationFrame(step)
  }
}