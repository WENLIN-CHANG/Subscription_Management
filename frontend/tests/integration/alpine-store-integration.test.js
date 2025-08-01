// Alpine.js Store 集成測試
import { initializeGlobalStore } from '../../scripts/ui/globalStore.js'

describe('Alpine.js Store 集成測試', () => {
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
        getMonthlyPrice: jest.fn((subscription) => {
          // 簡化的月費計算邏輯
          const multiplier = subscription.cycle === 'yearly' ? 1/12 : 
                            subscription.cycle === 'quarterly' ? 1/3 : 1
          return subscription.price * multiplier
        })
      },
      uiUtils: {
        animateNumber: jest.fn((from, to, callback) => {
          // 模擬動畫，直接調用回調
          setTimeout(() => callback(to), 100)
        })
      }
    }

    // 初始化全局 store
    initializeGlobalStore(mockAlpine)
    store = mockAlpine.store.mock.calls[0][1]
  })

  describe('跨組件狀態同步', () => {
    test('多個組件應該共享相同的狀態', () => {
      // 模擬兩個組件實例
      const component1 = { $store: { app: store } }
      const component2 = { $store: { app: store } }

      // 在組件1中更新訂閱
      const subscription = { id: 1, name: 'Netflix', price: 390, cycle: 'monthly' }
      component1.$store.app.addSubscription(subscription)

      // 組件2應該能看到更新
      expect(component2.$store.app.subscriptions).toContain(subscription)
      expect(component2.$store.app.subscriptions.length).toBe(1)
    })

    test('編輯狀態應該在組件間同步', () => {
      const subscription = { id: 1, name: 'Netflix', price: 390 }
      
      // 模擬多個組件
      const listComponent = { $store: { app: store } }
      const formComponent = { $store: { app: store } }

      // 在列表組件中開始編輯
      listComponent.$store.app.startEditing(subscription)

      // 表單組件應該看到編輯狀態
      expect(formComponent.$store.app.isEditing).toBe(true)
      expect(formComponent.$store.app.editingSubscription).toEqual(subscription)

      // 在表單組件中停止編輯
      formComponent.$store.app.stopEditing()

      // 列表組件應該看到狀態變化
      expect(listComponent.$store.app.isEditing).toBe(false)
      expect(listComponent.$store.app.editingSubscription).toBe(null)
    })

    test('認證狀態變化應該影響所有組件', () => {
      const dashboardComponent = { $store: { app: store } }
      const navigationComponent = { $store: { app: store } }
      const formComponent = { $store: { app: store } }

      const user = { id: 1, username: 'testuser' }

      // 設置認證狀態
      dashboardComponent.$store.app.setAuth(true, user)

      // 所有組件都應該看到認證狀態
      expect(navigationComponent.$store.app.isLoggedIn).toBe(true)
      expect(formComponent.$store.app.currentUser).toEqual(user)
      expect(dashboardComponent.$store.app.isLoggedIn).toBe(true)
    })
  })

  describe('狀態變化的副作用', () => {
    test('添加訂閱應該觸發月度總計重新計算', (done) => {
      const subscription = { id: 1, name: 'Netflix', price: 390, cycle: 'monthly' }
      
      // 添加訂閱
      store.addSubscription(subscription)

      // 等待動畫完成
      setTimeout(() => {
        expect(global.window.calculationUtils.getMonthlyPrice).toHaveBeenCalledWith(subscription)
        expect(store.monthlyTotal).toBe(390)
        done()
      }, 150)
    })

    test('更新訂閱應該觸發月度總計重新計算', (done) => {
      // 先添加訂閱
      const originalSubscription = { id: 1, name: 'Netflix', price: 390, cycle: 'monthly' }
      store.subscriptions = [originalSubscription]
      
      // 更新訂閱
      const updatedSubscription = { id: 1, name: 'Netflix', price: 490, cycle: 'monthly' }
      store.updateSubscription(updatedSubscription)

      // 等待動畫完成
      setTimeout(() => {
        expect(global.window.calculationUtils.getMonthlyPrice).toHaveBeenCalledWith(updatedSubscription)
        expect(store.monthlyTotal).toBe(490)
        done()
      }, 150)
    })

    test('移除訂閱應該觸發月度總計重新計算', (done) => {
      // 先添加兩個訂閱
      store.subscriptions = [
        { id: 1, name: 'Netflix', price: 390, cycle: 'monthly' },
        { id: 2, name: 'Spotify', price: 149, cycle: 'monthly' }
      ]
      
      // 移除一個訂閱
      store.removeSubscription(1)

      // 等待動畫完成
      setTimeout(() => {
        expect(store.subscriptions.length).toBe(1)
        expect(store.monthlyTotal).toBe(149)
        done()
      }, 150)
    })
  })

  describe('UI 狀態管理', () => {
    test('手機選單狀態應該正確切換', () => {
      expect(store.mobileMenuOpen).toBe(false)

      // 切換開啟
      store.toggleMobileMenu()
      expect(store.mobileMenuOpen).toBe(true)

      // 直接關閉
      store.closeMobileMenu()
      expect(store.mobileMenuOpen).toBe(false)

      // 再次切換
      store.toggleMobileMenu()
      expect(store.mobileMenuOpen).toBe(true)
    })

    test('預算設定彈窗狀態管理', () => {
      store.monthlyBudget = 3000

      // 開啟預算設定
      store.openBudgetSetting()
      expect(store.showBudgetSetting).toBe(true)
      expect(store.tempBudget).toBe('3000')

      // 修改臨時預算
      store.tempBudget = '5000'
      expect(store.tempBudget).toBe('5000')

      // 關閉預算設定
      store.closeBudgetSetting()
      expect(store.showBudgetSetting).toBe(false)
      expect(store.tempBudget).toBe('')
      
      // 原預算不應該變化
      expect(store.monthlyBudget).toBe(3000)
    })
  })

  describe('數據一致性', () => {
    test('setSubscriptions 應該完全替換訂閱列表', (done) => {
      // 先設置一些訂閱
      store.subscriptions = [
        { id: 1, name: 'Old Service', price: 100 }
      ]

      // 設置新的訂閱列表
      const newSubscriptions = [
        { id: 2, name: 'New Service 1', price: 200, cycle: 'monthly' },
        { id: 3, name: 'New Service 2', price: 300, cycle: 'monthly' }
      ]

      store.setSubscriptions(newSubscriptions)

      expect(store.subscriptions).toEqual(newSubscriptions)
      expect(store.subscriptions.length).toBe(2)

      // 等待月度總計計算完成
      setTimeout(() => {
        expect(store.monthlyTotal).toBe(500)
        done()
      }, 150)
    })

    test('重複的訂閱 ID 更新應該正確處理', () => {
      // 添加訂閱
      store.subscriptions = [
        { id: 1, name: 'Service 1', price: 100 },
        { id: 2, name: 'Service 2', price: 200 },
        { id: 3, name: 'Service 3', price: 300 }
      ]

      // 更新中間的訂閱
      const updatedSubscription = { id: 2, name: 'Updated Service 2', price: 250 }
      store.updateSubscription(updatedSubscription)

      expect(store.subscriptions.length).toBe(3)
      expect(store.subscriptions[1]).toEqual(updatedSubscription)
      expect(store.subscriptions[0].name).toBe('Service 1')
      expect(store.subscriptions[2].name).toBe('Service 3')
    })

    test('移除不存在的訂閱應該不影響列表', () => {
      const originalSubscriptions = [
        { id: 1, name: 'Service 1', price: 100 },
        { id: 2, name: 'Service 2', price: 200 }
      ]
      
      store.subscriptions = [...originalSubscriptions]

      // 嘗試移除不存在的訂閱
      store.removeSubscription(999)

      expect(store.subscriptions).toEqual(originalSubscriptions)
    })
  })

  describe('邊界情況處理', () => {
    test('calculationUtils 不可用時應該安全處理', () => {
      global.window.calculationUtils = undefined

      const subscription = { id: 1, name: 'Test', price: 100 }
      
      // 不應該拋出錯誤
      expect(() => store.addSubscription(subscription)).not.toThrow()
      expect(store.subscriptions).toContain(subscription)
    })

    test('uiUtils 不可用時應該回退到直接設置', (done) => {
      global.window.uiUtils = undefined

      const subscription = { id: 1, name: 'Test', price: 100, cycle: 'monthly' }
      store.addSubscription(subscription)

      // 應該直接設置值而不是使用動畫
      setTimeout(() => {
        expect(store.monthlyTotal).toBe(100)
        done()
      }, 50)
    })

    test('空訂閱列表的月度總計應該為 0', (done) => {
      store.subscriptions = []
      store.calculateMonthlyTotal()

      setTimeout(() => {
        expect(store.monthlyTotal).toBe(0)
        done()
      }, 150)
    })
  })
})