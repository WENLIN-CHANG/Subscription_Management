// Jest 測試環境設定
import '@testing-library/jest-dom'

// 模擬 Alpine.js
global.Alpine = {
  data: jest.fn(),
  store: jest.fn(() => ({
    app: {
      subscriptions: [],
      monthlyTotal: 0,
      monthlyBudget: 0,
      isLoggedIn: false,
      currentUser: null,
      isEditing: false,
      editingSubscription: null,
      currentTheme: 'corporate',
      mobileMenuOpen: false,
      showBudgetSetting: false,
      tempBudget: '',
      setSubscriptions: jest.fn(),
      addSubscription: jest.fn(),
      updateSubscription: jest.fn(),
      removeSubscription: jest.fn(),
      calculateMonthlyTotal: jest.fn(),
      startEditing: jest.fn(),
      stopEditing: jest.fn(),
      setAuth: jest.fn(),
      setTheme: jest.fn(),
      toggleMobileMenu: jest.fn(),
      closeMobileMenu: jest.fn(),
      openBudgetSetting: jest.fn(),
      closeBudgetSetting: jest.fn(),
      setBudget: jest.fn()
    }
  })),
  start: jest.fn()
}

// 模擬全局對象
global.window = Object.create(window)
global.document = document
global.localStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
}

// 模擬 DOM 方法
global.document.getElementById = jest.fn()
global.document.querySelector = jest.fn()
global.document.querySelectorAll = jest.fn()

// 模擬 window 方法
global.window.scrollTo = jest.fn()
global.window.alert = jest.fn()
global.window.confirm = jest.fn()

// 在每個測試前重置 mocks
beforeEach(() => {
  jest.clearAllMocks()
  global.localStorage.getItem.mockReturnValue(null)
  global.localStorage.setItem.mockImplementation(() => {})
  global.localStorage.removeItem.mockImplementation(() => {})
})