// 訂閱操作模塊 - 訂閱的 CRUD 操作和表單驗證
import { dataManager } from './dataManager.js'

export const subscriptionActions = {
  // 表單驗證
  validateForm(newSubscription) {
    if (!newSubscription.name.trim()) {
      alert('請輸入服務名稱')
      return false
    }
    if (!newSubscription.price || newSubscription.price <= 0) {
      alert('請輸入有效的價格')
      return false
    }
    if (!newSubscription.category) {
      alert('請選擇服務分類')
      return false
    }
    if (!newSubscription.startDate) {
      alert('請選擇開始日期')
      return false
    }
    return true
  },

  // 重置表單
  resetForm(context) {
    context.newSubscription = {
      name: '',
      price: '',
      cycle: 'monthly',
      category: '',
      startDate: ''
    }
  },

  // 新增訂閱
  addSubscription(context) {
    if (this.validateForm(context.newSubscription)) {
      const subscription = {
        id: Date.now(),
        name: context.newSubscription.name,
        price: parseFloat(context.newSubscription.price),
        cycle: context.newSubscription.cycle,
        category: context.newSubscription.category,
        startDate: context.newSubscription.startDate
      }
      
      context.subscriptions.push(subscription)
      this.resetForm(context)
      context.calculateMonthlyTotal()
      dataManager.saveSubscriptions(context.subscriptions)
    }
  },

  // 刪除訂閱
  deleteSubscription(context, id) {
    if (confirm('確定要刪除這個訂閱嗎？')) {
      context.subscriptions = context.subscriptions.filter(sub => sub.id !== id)
      context.calculateMonthlyTotal()
      dataManager.saveSubscriptions(context.subscriptions)
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
        cycle: subscription.cycle,
        category: subscription.category,
        startDate: subscription.startDate
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
  updateSubscription(context) {
    if (this.validateForm(context.newSubscription)) {
      const index = context.subscriptions.findIndex(sub => sub.id === context.editingSubscription.id)
      if (index !== -1) {
        context.subscriptions[index] = {
          ...context.editingSubscription,
          name: context.newSubscription.name,
          price: parseFloat(context.newSubscription.price),
          cycle: context.newSubscription.cycle,
          category: context.newSubscription.category,
          startDate: context.newSubscription.startDate
        }
        this.cancelEdit(context)
        context.calculateMonthlyTotal()
        dataManager.saveSubscriptions(context.subscriptions)
      }
    }
  }
}