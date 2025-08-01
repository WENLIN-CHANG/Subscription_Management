// 全局狀態管理測試
import { initializeGlobalStore } from '../../scripts/ui/globalStore.js'

describe('globalStore', () => {
  let mockAlpine
  let store

  beforeEach(() => {
    // 模擬 Alpine.js
    mockAlpine = {
      store: jest.fn()
    }
    
    // 模擬全局變數
    global.window = {
      calculationUtils: {
        getMonthlyPrice: jest.fn(() => 100)
      },
      uiUtils: {
        animateNumber: jest.fn((from, to, callback) => callback(to))
      }
    }

    // 初始化 store
    initializeGlobalStore(mockAlpine)
    
    // 獲取傳給 Alpine.store 的 store 物件
    store = mockAlpine.store.mock.calls[0][1]
  })

  describe('數據狀態管理', () => {
    test('初始狀態應該正確', () => {
      expect(store.subscriptions).toEqual([])
      expect(store.monthlyTotal).toBe(0)
      expect(store.monthlyBudget).toBe(0)
      expect(store.isLoggedIn).toBe(false)
      expect(store.currentUser).toBe(null)
    })

    test('setSubscriptions 應該更新訂閱列表並計算總金額', () => {
      const mockSubscriptions = [
        { id: 1, name: 'Netflix', price: 390 },
        { id: 2, name: 'Spotify', price: 149 }
      ]

      store.setSubscriptions(mockSubscriptions)

      expect(store.subscriptions).toEqual(mockSubscriptions)
      expect(store.calculateMonthlyTotal).toHaveBeenCalled()
    })

    test('addSubscription 應該添加新訂閱', () => {
      const newSubscription = { id: 3, name: 'Disney+', price: 270 }
      
      store.addSubscription(newSubscription)
      
      expect(store.subscriptions).toContain(newSubscription)
      expect(store.calculateMonthlyTotal).toHaveBeenCalled()
    })

    test('updateSubscription 應該更新指定訂閱', () => {
      // 先添加一個訂閱
      const originalSubscription = { id: 1, name: 'Netflix', price: 390 }
      store.subscriptions = [originalSubscription]
      
      const updatedSubscription = { id: 1, name: 'Netflix Premium', price: 490 }
      store.updateSubscription(updatedSubscription)
      
      expect(store.subscriptions[0]).toEqual(updatedSubscription)
      expect(store.calculateMonthlyTotal).toHaveBeenCalled()
    })

    test('removeSubscription 應該移除指定訂閱', () => {
      // 先添加訂閱
      store.subscriptions = [
        { id: 1, name: 'Netflix', price: 390 },
        { id: 2, name: 'Spotify', price: 149 }
      ]
      
      store.removeSubscription(1)
      
      expect(store.subscriptions).toHaveLength(1)
      expect(store.subscriptions[0].id).toBe(2)
      expect(store.calculateMonthlyTotal).toHaveBeenCalled()
    })
  })

  describe('編輯狀態管理', () => {
    test('startEditing 應該設置編輯狀態', () => {
      const subscription = { id: 1, name: 'Netflix', price: 390 }
      
      store.startEditing(subscription)
      
      expect(store.isEditing).toBe(true)
      expect(store.editingSubscription).toEqual(subscription)
    })

    test('stopEditing 應該清除編輯狀態', () => {
      // 先設置編輯狀態
      store.isEditing = true
      store.editingSubscription = { id: 1, name: 'Netflix' }
      
      store.stopEditing()
      
      expect(store.isEditing).toBe(false)
      expect(store.editingSubscription).toBe(null)
    })
  })

  describe('認證狀態管理', () => {
    test('setAuth 應該更新認證狀態', () => {
      const user = { id: 1, username: 'testuser' }
      
      store.setAuth(true, user)
      
      expect(store.isLoggedIn).toBe(true)
      expect(store.currentUser).toEqual(user)
    })
  })

  describe('UI 狀態管理', () => {
    test('toggleMobileMenu 應該切換選單狀態', () => {
      expect(store.mobileMenuOpen).toBe(false)
      
      store.toggleMobileMenu()
      expect(store.mobileMenuOpen).toBe(true)
      
      store.toggleMobileMenu()
      expect(store.mobileMenuOpen).toBe(false)
    })

    test('預算設定彈窗操作', () => {
      store.monthlyBudget = 3000
      
      store.openBudgetSetting()
      expect(store.showBudgetSetting).toBe(true)
      expect(store.tempBudget).toBe('3000')
      
      store.closeBudgetSetting()
      expect(store.showBudgetSetting).toBe(false)
      expect(store.tempBudget).toBe('')
    })
  })

  describe('月度總計算', () => {
    test('calculateMonthlyTotal 應該正確計算總金額', () => {
      store.subscriptions = [
        { id: 1, name: 'Netflix' },
        { id: 2, name: 'Spotify' }
      ]
      
      store.calculateMonthlyTotal()
      
      expect(global.window.calculationUtils.getMonthlyPrice).toHaveBeenCalledTimes(2)
      expect(store.monthlyTotal).toBe(200) // 100 * 2
    })

    test('calculateMonthlyTotal 沒有 calculationUtils 時應該安全處理', () => {
      global.window.calculationUtils = undefined
      
      store.calculateMonthlyTotal()
      
      // 不應該拋出錯誤
      expect(store.monthlyTotal).toBe(200) // 保持原值
    })
  })
})