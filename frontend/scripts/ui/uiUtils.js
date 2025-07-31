// UI 工具模塊 - UI 樣式、動畫效果、顏色生成
import { calculationUtils } from '../utils/calculationUtils.js'

export const uiUtils = {
  // 獲取分類名稱
  getCategoryName(category) {
    const names = {
      streaming: '影音串流',
      software: '軟體工具',
      news: '新聞資訊',
      gaming: '遊戲娛樂',
      music: '音樂',
      education: '教育學習',
      productivity: '生產力工具',
      other: '其他'
    }
    return names[category] || category
  },

  // 獲取分類圖標
  getCategoryIcon(category) {
    const icons = {
      streaming: '🎥',
      software: '💻',
      news: '📰',
      gaming: '🎮',
      music: '🎵',
      education: '📚',
      productivity: '⚙️',
      other: '📋'
    }
    return icons[category] || '📋'
  },

  // 獲取分類顏色
  getCategoryColor(category) {
    const colors = {
      streaming: 'border-red-400',
      software: 'border-blue-400',
      news: 'border-yellow-400',
      gaming: 'border-purple-400',
      music: 'border-pink-400',
      education: 'border-indigo-400',
      productivity: 'border-green-400',
      other: 'border-gray-400'
    }
    return colors[category] || 'border-gray-400'
  },

  // 獲取分類背景顏色
  getCategoryBgColor(category) {
    const colors = {
      streaming: 'bg-red-100 text-red-800',
      software: 'bg-blue-100 text-blue-800',
      news: 'bg-yellow-100 text-yellow-800',
      gaming: 'bg-purple-100 text-purple-800',
      music: 'bg-pink-100 text-pink-800',
      education: 'bg-indigo-100 text-indigo-800',
      productivity: 'bg-green-100 text-green-800',
      other: 'bg-gray-100 text-gray-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  },

  // 獲取分類進度條顏色
  getCategoryProgressColor(category) {
    const colors = {
      streaming: 'bg-red-400',
      software: 'bg-blue-400',
      news: 'bg-yellow-400',
      gaming: 'bg-purple-400',
      music: 'bg-pink-400',
      education: 'bg-indigo-400',
      productivity: 'bg-green-400',
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