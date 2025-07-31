// 預算管理模塊 - 預算管理相關功能
import { dataManager } from '../data/dataManager.js' 
import { stateManager } from '../ui/stateManager.js'

export const budgetManager = {
  // 打開預算設定
  openBudgetSetting(context) {
    // 檢查是否已登入
    if (!dataManager.isLoggedIn()) {
      stateManager.success.show('請先登入以設定個人化的月度預算', '預算設定')
      setTimeout(() => {
        context.showLogin()
      }, 1500)
      return
    }
    
    context.tempBudget = context.monthlyBudget.toString()
    context.showBudgetSetting = true
  },

  // 關閉預算設定
  closeBudgetSetting(context) {
    context.showBudgetSetting = false
    context.tempBudget = ''
  },

  // 保存預算
  async saveBudget(context) {
    const budget = parseFloat(context.tempBudget)
    if (isNaN(budget) || budget < 0) {
      stateManager.error.set('請輸入有效的預算金額', '預算設定')
      return
    }

    try {
      await stateManager.withLoading('saveBudget', async () => {
        await dataManager.saveBudget(budget)
        context.monthlyBudget = budget
      }, {
        errorContext: '保存預算',
        successMessage: `成功設定月度預算：$${budget}`,
        successContext: '預算管理'
      })
      
      this.closeBudgetSetting(context)
      
    } catch (error) {
      console.error('保存預算失敗:', error)
    }
  },

  // 預算相關計算
  getBudgetUsagePercentage(context) {
    if (context.monthlyBudget <= 0) return 0
    return Math.min((context.monthlyTotal / context.monthlyBudget * 100), 100)
  },

  getBudgetStatus(context) {
    if (context.monthlyBudget <= 0) return 'none'
    const percentage = this.getBudgetUsagePercentage(context)
    if (percentage >= 100) return 'over'
    if (percentage >= 80) return 'warning'
    return 'good'
  },

  getBudgetStatusText(context) {
    const status = this.getBudgetStatus(context)
    switch (status) {
      case 'over':
        return '已超支！'
      case 'warning':
        return '接近預算上限'
      case 'good':
        return '預算充足'
      default:
        return '未設定預算'
    }
  },

  getBudgetStatusColor(context) {
    const status = this.getBudgetStatus(context)
    switch (status) {
      case 'over':
        return 'text-red-600'
      case 'warning':
        return 'text-orange-600'
      case 'good':
        return 'text-green-600'
      default:
        return 'text-gray-600'
    }
  },

  getRemainingBudget(context) {
    return Math.max(context.monthlyBudget - context.monthlyTotal, 0)
  }
}