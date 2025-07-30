// 訂閱操作模塊 - 訂閱的 CRUD 操作和表單驗證
import { dataManager } from './dataManager.js'
import { stateManager } from './stateManager.js'
import { SubscriptionFields } from './types.js'

export const subscriptionActions = {
  // 表單驗證
  validateForm(newSubscription) {
    if (!newSubscription.name.trim()) {
      stateManager.error.set('請輸入服務名稱', '表單驗證')
      return false
    }
    if (!newSubscription.originalPrice || newSubscription.originalPrice <= 0) {
      stateManager.error.set('請輸入有效的價格', '表單驗證')
      return false
    }
    if (!newSubscription.currency) {
      stateManager.error.set('請選擇貨幣', '表單驗證')
      return false
    }
    if (!newSubscription.category) {
      stateManager.error.set('請選擇服務分類', '表單驗證')
      return false
    }
    if (!newSubscription.startDate) {
      stateManager.error.set('請選擇開始日期', '表單驗證')
      return false
    }
    return true
  },

  // 重置表單
  resetForm(context) {
    context.newSubscription = {
      name: '',
      price: '',
      originalPrice: '',
      currency: 'TWD',
      cycle: 'monthly',
      category: '',
      startDate: ''
    }
  },

  // 新增訂閱
  async addSubscription(context) {
    if (!this.validateForm(context.newSubscription)) {
      return
    }

    try {
      await stateManager.withLoading('addSubscription', async () => {
        // 如果已登入，使用 API 創建
        if (dataManager.isLoggedIn()) {
          await dataManager.createSubscription({
            [SubscriptionFields.NAME]: context.newSubscription.name,
            [SubscriptionFields.ORIGINAL_PRICE]: parseFloat(context.newSubscription.originalPrice),
            [SubscriptionFields.CURRENCY]: context.newSubscription.currency,
            [SubscriptionFields.CYCLE]: context.newSubscription.cycle,
            [SubscriptionFields.CATEGORY]: context.newSubscription.category,
            [SubscriptionFields.START_DATE]: context.newSubscription.startDate
          })
          
          // 重新載入數據
          context.subscriptions = await dataManager.loadSubscriptions()
        } else {
          // 離線模式：直接添加到本地
          const subscription = {
            id: Date.now(),
            name: context.newSubscription.name,
            price: parseFloat(context.newSubscription.originalPrice), // 暫時用原始價格
            originalPrice: parseFloat(context.newSubscription.originalPrice),
            currency: context.newSubscription.currency,
            cycle: context.newSubscription.cycle,
            category: context.newSubscription.category,
            startDate: context.newSubscription.startDate
          }

          context.subscriptions.push(subscription)
          await dataManager.saveSubscriptions(context.subscriptions)
        }
        
        context.calculateMonthlyTotal()
      }, {
        errorContext: '添加訂閱',
        successMessage: `成功添加訂閱：${context.newSubscription.name}`,
        successContext: '訂閱管理'
      })
      
      this.resetForm(context)
      
    } catch (error) {
      console.error('添加訂閱失敗:', error)
    }
  },

  // 刪除訂閱
  async deleteSubscription(context, id) {
    const subscription = context.subscriptions.find(sub => sub.id === id)
    if (!subscription) return
    
    if (!confirm(`確定要刪除「${subscription.name}」這個訂閱嗎？`)) {
      return
    }

    try {
      await stateManager.withLoading('deleteSubscription', async () => {
        if (dataManager.isLoggedIn()) {
          await dataManager.deleteSubscription(id)
          // 重新載入數據
          context.subscriptions = await dataManager.loadSubscriptions()
        } else {
          // 離線模式：從本地刪除
          context.subscriptions = context.subscriptions.filter(sub => sub.id !== id)
          await dataManager.saveSubscriptions(context.subscriptions)
        }
        
        context.calculateMonthlyTotal()
      }, {
        errorContext: '刪除訂閱',
        successMessage: `成功刪除訂閱：${subscription.name}`,
        successContext: '訂閱管理'
      })
      
    } catch (error) {
      console.error('刪除訂閱失敗:', error)
    }
  },

  // 開始編輯訂閱
  editSubscription(context, id) {
    const subscription = context.subscriptions.find(sub => sub.id === id)
    if (subscription) {
      context.editingSubscription = { ...subscription }
      context.newSubscription = {
        name: subscription.name,
        price: subscription.price.toString(),
        originalPrice: subscription.originalPrice ? subscription.originalPrice.toString() : subscription.price.toString(),
        currency: subscription.currency || 'TWD',
        cycle: subscription.cycle,
        category: subscription.category,
        startDate: subscription.startDate ? subscription.startDate.split('T')[0].split(' ')[0] : ''
      }
      context.isEditing = true
      // 滾動到表單位置
      setTimeout(() => {
        document.querySelector('form').scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
  },

  // 取消編輯
  cancelEdit(context) {
    context.isEditing = false
    context.editingSubscription = null
    this.resetForm(context)
  },

  // 更新訂閱
  async updateSubscription(context) {
    if (!this.validateForm(context.newSubscription)) {
      return
    }

    try {
      await stateManager.withLoading('updateSubscription', async () => {
        if (dataManager.isLoggedIn()) {
          await dataManager.updateSubscription(context.editingSubscription.id, {
            [SubscriptionFields.NAME]: context.newSubscription.name,
            [SubscriptionFields.ORIGINAL_PRICE]: parseFloat(context.newSubscription.originalPrice),
            [SubscriptionFields.CURRENCY]: context.newSubscription.currency,
            [SubscriptionFields.CYCLE]: context.newSubscription.cycle,
            [SubscriptionFields.CATEGORY]: context.newSubscription.category,
            [SubscriptionFields.START_DATE]: context.newSubscription.startDate
          })
          
          // 重新載入數據
          context.subscriptions = await dataManager.loadSubscriptions()
        } else {
          // 離線模式：更新本地數據
          const index = context.subscriptions.findIndex(sub => sub.id === context.editingSubscription.id)
          if (index !== -1) {
            context.subscriptions[index] = {
              ...context.editingSubscription,
              name: context.newSubscription.name,
              price: parseFloat(context.newSubscription.originalPrice), // 暫時用原始價格
              originalPrice: parseFloat(context.newSubscription.originalPrice),
              currency: context.newSubscription.currency,
              cycle: context.newSubscription.cycle,
              category: context.newSubscription.category,
              startDate: context.newSubscription.startDate
            }
            await dataManager.saveSubscriptions(context.subscriptions)
          }
        }
        
        context.calculateMonthlyTotal()
      }, {
        errorContext: '更新訂閱',
        successMessage: `成功更新訂閱：${context.newSubscription.name}`,
        successContext: '訂閱管理'
      })
      
      this.cancelEdit(context)
      
    } catch (error) {
      console.error('更新訂閱失敗:', error)
    }
  }
}