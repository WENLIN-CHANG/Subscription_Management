// 儀表板管理器組件測試
import { dashboardManager } from '../../../scripts/components/dashboardManager.js'

// 模擬依賴
jest.mock('../../../scripts/business/budgetManager.js', () => ({
  budgetManager: {
    saveBudget: jest.fn(),
    getBudgetUsagePercentage: jest.fn(() => 75),
    getBudgetStatus: jest.fn(() => 'warning'),
    getBudgetStatusText: jest.fn(() => '預算警告'),
    getBudgetStatusColor: jest.fn(() => 'text-warning'),
    getRemainingBudget: jest.fn(() => 500)
  }
}))

jest.mock('../../../scripts/business/statisticsManager.js', () => ({
  statisticsManager: {
    getUpcomingExpiry: jest.fn(() => []),
    getCategoryStats: jest.fn(() => [])
  }
}))

jest.mock('../../../scripts/utils/calculationUtils.js', () => ({
  calculationUtils: {
    formatCurrency: jest.fn((amount) => `NT$${amount}`),
    formatNumber: jest.fn((number) => number.toString())
  }
}))

jest.mock('../../../scripts/auth/authManager.js', () => ({
  authManager: {
    showAuthDialog: jest.fn(),
    logout: jest.fn(),
    showChangePasswordDialog: jest.fn()
  }
}))

jest.mock('../../../scripts/ui/themeManager.js', () => ({
  themeManager: {
    getCurrentThemeType: jest.fn(() => 'light'),
    toggleTheme: jest.fn(() => true),
    currentTheme: 'corporate'
  }
}))

import { budgetManager } from '../../../scripts/business/budgetManager.js'
import { statisticsManager } from '../../../scripts/business/statisticsManager.js'
import { calculationUtils } from '../../../scripts/utils/calculationUtils.js'
import { authManager } from '../../../scripts/auth/authManager.js'
import { themeManager } from '../../../scripts/ui/themeManager.js'

describe('dashboardManager', () => {
  let component
  let mockStore

  beforeEach(() => {
    // 模擬 Alpine store
    mockStore = {
      app: {
        subscriptions: [
          { id: 1, name: 'Netflix', price: 390 },
          { id: 2, name: 'Spotify', price: 149 }
        ],
        monthlyTotal: 539,
        monthlyBudget: 1000,
        isLoggedIn: true,
        currentUser: { id: 1, username: 'testuser' },
        currentTheme: 'corporate',
        showBudgetSetting: false,
        tempBudget: '',
        openBudgetSetting: jest.fn(),
        closeBudgetSetting: jest.fn(),
        setTheme: jest.fn()
      }
    }

    // 建立組件實例
    component = dashboardManager.call({ $store: mockStore })

    // 重置 mocks
    jest.clearAllMocks()
  })

  describe('狀態獲取', () => {
    test('應該正確獲取全局狀態', () => {
      expect(component.subscriptions).toEqual(mockStore.app.subscriptions)
      expect(component.monthlyTotal).toBe(539)
      expect(component.monthlyBudget).toBe(1000)
      expect(component.isLoggedIn).toBe(true)
      expect(component.currentUser).toEqual({ id: 1, username: 'testuser' })
      expect(component.currentTheme).toBe('corporate')
      expect(component.showBudgetSetting).toBe(false)
    })

    test('tempBudget setter 應該更新 store', () => {
      component.tempBudget = '1500'
      expect(mockStore.app.tempBudget).toBe('1500')
    })
  })

  describe('預算管理功能', () => {
    test('已登入用戶可以開啟預算設定', () => {
      component.openBudgetSetting()
      expect(mockStore.app.openBudgetSetting).toHaveBeenCalled()
    })

    test('未登入用戶開啟預算設定時應該顯示登入對話框', () => {
      mockStore.app.isLoggedIn = false
      component.openBudgetSetting()
      
      expect(authManager.showAuthDialog).toHaveBeenCalledWith('login')
      expect(mockStore.app.openBudgetSetting).not.toHaveBeenCalled()
    })

    test('關閉預算設定', () => {
      component.closeBudgetSetting()
      expect(mockStore.app.closeBudgetSetting).toHaveBeenCalled()
    })

    test('保存預算', () => {
      component.saveBudget()
      expect(budgetManager.saveBudget).toHaveBeenCalledWith(component)
    })

    test('預算相關計算方法', () => {
      expect(component.getBudgetUsagePercentage()).toBe(75)
      expect(component.getBudgetStatus()).toBe('warning')
      expect(component.getBudgetStatusText()).toBe('預算警告')
      expect(component.getBudgetStatusColor()).toBe('text-warning')
      expect(component.getRemainingBudget()).toBe(500)

      expect(budgetManager.getBudgetUsagePercentage).toHaveBeenCalledWith(component)
      expect(budgetManager.getBudgetStatus).toHaveBeenCalledWith(component)
      expect(budgetManager.getBudgetStatusText).toHaveBeenCalledWith(component)
      expect(budgetManager.getBudgetStatusColor).toHaveBeenCalledWith(component)
      expect(budgetManager.getRemainingBudget).toHaveBeenCalledWith(component)
    })
  })

  describe('統計分析功能', () => {
    test('取得即將到期的訂閱', () => {
      const upcomingExpiry = [{ id: 1, name: 'Netflix', daysUntil: 3 }]
      statisticsManager.getUpcomingExpiry.mockReturnValue(upcomingExpiry)

      const result = component.getUpcomingExpiry()

      expect(result).toEqual(upcomingExpiry)
      expect(statisticsManager.getUpcomingExpiry).toHaveBeenCalledWith(component.subscriptions)
    })

    test('取得分類統計', () => {
      const categoryStats = [
        { category: 'streaming', amount: 390, count: 1 },
        { category: 'music', amount: 149, count: 1 }
      ]
      statisticsManager.getCategoryStats.mockReturnValue(categoryStats)

      const result = component.getCategoryStats()

      expect(result).toEqual(categoryStats)
      expect(statisticsManager.getCategoryStats).toHaveBeenCalledWith(component.subscriptions)
    })
  })

  describe('格式化方法', () => {
    test('格式化貨幣', () => {
      const result = component.formatCurrency(1000)
      expect(result).toBe('NT$1000')
      expect(calculationUtils.formatCurrency).toHaveBeenCalledWith(1000)
    })

    test('格式化數字', () => {
      const result = component.formatNumber(1234)
      expect(result).toBe('1234')
      expect(calculationUtils.formatNumber).toHaveBeenCalledWith(1234)
    })
  })

  describe('主題管理', () => {
    test('取得當前主題類型', () => {
      const result = component.getCurrentThemeType()
      expect(result).toBe('light')
      expect(themeManager.getCurrentThemeType).toHaveBeenCalled()
    })

    test('切換主題', () => {
      component.toggleTheme()

      expect(themeManager.toggleTheme).toHaveBeenCalled()
      expect(mockStore.app.setTheme).toHaveBeenCalledWith('corporate')
    })

    test('主題切換失敗時不更新 store', () => {
      themeManager.toggleTheme.mockReturnValue(false)

      component.toggleTheme()

      expect(themeManager.toggleTheme).toHaveBeenCalled()
      expect(mockStore.app.setTheme).not.toHaveBeenCalled()
    })
  })

  describe('認證相關功能', () => {
    test('顯示登入對話框', () => {
      component.showLogin()
      expect(authManager.showAuthDialog).toHaveBeenCalledWith('login')
    })

    test('顯示註冊對話框', () => {
      component.showRegister()
      expect(authManager.showAuthDialog).toHaveBeenCalledWith('register')
    })

    test('登出', () => {
      component.logout()
      expect(authManager.logout).toHaveBeenCalled()
    })

    test('顯示修改密碼對話框', () => {
      component.showChangePasswordDialog()
      expect(authManager.showChangePasswordDialog).toHaveBeenCalled()
    })
  })
})