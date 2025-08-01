// 訂閱操作測試
import { subscriptionActions } from '../../scripts/business/subscriptionActions.js'

// 模擬依賴
jest.mock('../../scripts/data/dataManager.js', () => ({
  dataManager: {
    saveSubscription: jest.fn(),
    updateSubscription: jest.fn(),
    deleteSubscription: jest.fn()
  }
}))

jest.mock('../../scripts/ui/stateManager.js', () => ({
  stateManager: {
    withLoading: jest.fn((key, action, options) => action()),
    success: {
      show: jest.fn()
    },
    error: {
      set: jest.fn()
    }
  }
}))

import { dataManager } from '../../scripts/data/dataManager.js'
import { stateManager } from '../../scripts/ui/stateManager.js'

describe('subscriptionActions', () => {
  let mockComponent

  beforeEach(() => {
    // 模擬組件
    mockComponent = {
      $store: {
        app: {
          subscriptions: [],
          addSubscription: jest.fn(),
          updateSubscription: jest.fn(),
          removeSubscription: jest.fn(),
          startEditing: jest.fn(),
          stopEditing: jest.fn(),
          isLoggedIn: true
        }
      },
      newSubscription: {
        id: undefined,
        name: 'Test Service',
        originalPrice: '100',
        currency: 'TWD',
        cycle: 'monthly',
        category: 'streaming',
        startDate: '2024-01-01'
      },
      validateForm: jest.fn(() => true),
      resetForm: jest.fn()
    }

    // 重置所有 mocks
    jest.clearAllMocks()
  })

  describe('addSubscription', () => {
    test('應該成功添加訂閱', async () => {
      const expectedSubscription = {
        id: 'generated-id',
        ...mockComponent.newSubscription,
        price: 100
      }

      dataManager.saveSubscription.mockResolvedValue(expectedSubscription)

      await subscriptionActions.addSubscription(mockComponent)

      expect(mockComponent.validateForm).toHaveBeenCalled()
      expect(dataManager.saveSubscription).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Test Service',
          originalPrice: '100',
          currency: 'TWD',
          cycle: 'monthly',
          category: 'streaming',
          startDate: '2024-01-01'
        })
      )
      expect(mockComponent.$store.app.addSubscription).toHaveBeenCalledWith(expectedSubscription)
      expect(mockComponent.resetForm).toHaveBeenCalled()
      expect(stateManager.success.show).toHaveBeenCalledWith(
        '新增訂閱「Test Service」成功！',
        '新增成功'
      )
    })

    test('表單驗證失敗時應該拋出錯誤', async () => {
      const validationError = new Error('請輸入服務名稱')
      mockComponent.validateForm.mockImplementation(() => {
        throw validationError
      })

      await expect(subscriptionActions.addSubscription(mockComponent))
        .rejects.toThrow('請輸入服務名稱')

      expect(dataManager.saveSubscription).not.toHaveBeenCalled()
      expect(mockComponent.$store.app.addSubscription).not.toHaveBeenCalled()
    })

    test('保存失敗時應該拋出錯誤', async () => {
      const saveError = new Error('保存失敗')
      dataManager.saveSubscription.mockRejectedValue(saveError)

      await expect(subscriptionActions.addSubscription(mockComponent))
        .rejects.toThrow('保存失敗')

      expect(mockComponent.$store.app.addSubscription).not.toHaveBeenCalled()
    })
  })

  describe('updateSubscription', () => {
    test('應該成功更新訂閱', async () => {
      mockComponent.newSubscription.id = 1
      const updatedSubscription = {
        id: 1,
        ...mockComponent.newSubscription,
        price: 150
      }

      dataManager.updateSubscription.mockResolvedValue(updatedSubscription)

      await subscriptionActions.updateSubscription(mockComponent)

      expect(mockComponent.validateForm).toHaveBeenCalled()
      expect(dataManager.updateSubscription).toHaveBeenCalledWith(
        expect.objectContaining({
          id: 1,
          name: 'Test Service'
        })
      )
      expect(mockComponent.$store.app.updateSubscription).toHaveBeenCalledWith(updatedSubscription)
      expect(mockComponent.$store.app.stopEditing).toHaveBeenCalled()
      expect(mockComponent.resetForm).toHaveBeenCalled()
      expect(stateManager.success.show).toHaveBeenCalledWith(
        '更新訂閱「Test Service」成功！',
        '更新成功'
      )
    })
  })

  describe('deleteSubscription', () => {
    test('應該成功刪除訂閱', async () => {
      const subscriptionId = 1
      mockComponent.$store.app.subscriptions = [
        { id: 1, name: 'Test Service' },
        { id: 2, name: 'Other Service' }
      ]

      // 模擬確認對話框
      global.window.confirm = jest.fn(() => true)
      dataManager.deleteSubscription.mockResolvedValue()

      await subscriptionActions.deleteSubscription(mockComponent, subscriptionId)

      expect(global.window.confirm).toHaveBeenCalledWith(
        '確定要刪除「Test Service」嗎？此操作無法復原。'
      )
      expect(dataManager.deleteSubscription).toHaveBeenCalledWith(subscriptionId)
      expect(mockComponent.$store.app.removeSubscription).toHaveBeenCalledWith(subscriptionId)
      expect(stateManager.success.show).toHaveBeenCalledWith(
        '刪除訂閱「Test Service」成功！',
        '刪除成功'
      )
    })

    test('用戶取消刪除時不應該執行刪除', async () => {
      global.window.confirm = jest.fn(() => false)

      await subscriptionActions.deleteSubscription(mockComponent, 1)

      expect(dataManager.deleteSubscription).not.toHaveBeenCalled()
      expect(mockComponent.$store.app.removeSubscription).not.toHaveBeenCalled()
    })

    test('找不到訂閱時應該拋出錯誤', async () => {
      mockComponent.$store.app.subscriptions = []

      await expect(subscriptionActions.deleteSubscription(mockComponent, 999))
        .rejects.toThrow('找不到要刪除的訂閱')

      expect(dataManager.deleteSubscription).not.toHaveBeenCalled()
    })
  })

  describe('editSubscription', () => {
    test('應該開始編輯指定訂閱', () => {
      const subscriptionId = 1
      const subscription = { id: 1, name: 'Test Service', price: 100 }
      mockComponent.$store.app.subscriptions = [subscription]

      subscriptionActions.editSubscription(mockComponent, subscriptionId)

      expect(mockComponent.$store.app.startEditing).toHaveBeenCalledWith(subscription)

      // 應該滾動到表單
      expect(global.window.scrollTo).toHaveBeenCalledWith({
        top: expect.any(Number),
        behavior: 'smooth'
      })
    })

    test('找不到訂閱時應該拋出錯誤', () => {
      mockComponent.$store.app.subscriptions = []

      expect(() => subscriptionActions.editSubscription(mockComponent, 999))
        .toThrow('找不到要編輯的訂閱')
    })
  })

  describe('cancelEdit', () => {
    test('應該取消編輯狀態', () => {
      subscriptionActions.cancelEdit(mockComponent)

      expect(mockComponent.$store.app.stopEditing).toHaveBeenCalled()
      expect(mockComponent.resetForm).toHaveBeenCalled()
    })
  })

  describe('未登入狀態處理', () => {
    beforeEach(() => {
      mockComponent.$store.app.isLoggedIn = false
      global.window.authManager = {
        showAuthDialog: jest.fn()
      }
    })

    test('未登入時添加訂閱應該提示登入', async () => {
      await expect(subscriptionActions.addSubscription(mockComponent))
        .rejects.toThrow('請先登入才能新增訂閱')

      expect(global.window.authManager.showAuthDialog).toHaveBeenCalledWith('login')
    })

    test('未登入時更新訂閱應該提示登入', async () => {
      await expect(subscriptionActions.updateSubscription(mockComponent))
        .rejects.toThrow('請先登入才能更新訂閱')
    })

    test('未登入時刪除訂閱應該提示登入', async () => {
      await expect(subscriptionActions.deleteSubscription(mockComponent, 1))
        .rejects.toThrow('請先登入才能刪除訂閱')
    })
  })
})