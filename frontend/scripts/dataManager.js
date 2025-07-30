import { apiClient } from './apiClient.js'

// 數據管理模塊 - 處理數據存儲操作
export const dataManager = {
  // 檢查是否已登入
  isLoggedIn() {
    return !!apiClient.getToken()
  },

  // 訂閱數據管理
  async saveSubscriptions(subscriptions) {
    if (this.isLoggedIn()) {
      // 如果已登入，同步到後端
      try {
        // 這裡暫時只保存到本地，因為後端是通過單個 API 調用管理的
        localStorage.setItem('subscriptions', JSON.stringify(subscriptions))
      } catch (error) {
        console.error('保存訂閱數據失敗:', error)
        // 備用方案：保存到本地
        localStorage.setItem('subscriptions', JSON.stringify(subscriptions))
      }
    } else {
      // 未登入時使用本地存儲
      localStorage.setItem('subscriptions', JSON.stringify(subscriptions))
    }
  },

  async loadSubscriptions() {
    if (this.isLoggedIn()) {
      try {
        // 從後端獲取數據
        const subscriptions = await apiClient.subscriptions.getAll()
        // 轉換後端格式到前端格式
        return (subscriptions || []).map(sub => ({
          ...sub,
          startDate: sub.start_date // 將後端的 start_date 轉換為前端的 startDate
        }))
      } catch (error) {
        console.error('從後端載入訂閱失敗:', error)
        // 備用方案：從本地存儲載入
        const stored = localStorage.getItem('subscriptions')
        return stored ? JSON.parse(stored) : []
      }
    } else {
      // 未登入時從本地存儲載入
      const stored = localStorage.getItem('subscriptions')
      return stored ? JSON.parse(stored) : []
    }
  },

  // 單個訂閱操作
  async createSubscription(subscriptionData) {
    if (this.isLoggedIn()) {
      try {
        // 轉換前端數據格式到後端格式
        const backendData = {
          name: subscriptionData.name,
          price: parseFloat(subscriptionData.price),
          cycle: subscriptionData.cycle,
          category: subscriptionData.category || 'other',
          start_date: new Date(subscriptionData.startDate).toISOString()
        }
        return await apiClient.subscriptions.create(backendData)
      } catch (error) {
        console.error('創建訂閱失敗:', error)
        throw error
      }
    } else {
      throw new Error('請先登入')
    }
  },

  async updateSubscription(id, updateData) {
    if (this.isLoggedIn()) {
      try {
        const backendData = {}
        if (updateData.name !== undefined) backendData.name = updateData.name
        if (updateData.price !== undefined) backendData.price = parseFloat(updateData.price)
        if (updateData.cycle !== undefined) backendData.cycle = updateData.cycle
        if (updateData.category !== undefined) backendData.category = updateData.category
        if (updateData.startDate !== undefined) backendData.start_date = new Date(updateData.startDate).toISOString()
        if (updateData.is_active !== undefined) backendData.is_active = updateData.is_active

        return await apiClient.subscriptions.update(id, backendData)
      } catch (error) {
        console.error('更新訂閱失敗:', error)
        throw error
      }
    } else {
      throw new Error('請先登入')
    }
  },

  async deleteSubscription(id) {
    if (this.isLoggedIn()) {
      try {
        await apiClient.subscriptions.delete(id)
      } catch (error) {
        console.error('刪除訂閱失敗:', error)
        throw error
      }
    } else {
      throw new Error('請先登入')
    }
  },

  // 預算數據管理
  async saveBudget(budget) {
    if (this.isLoggedIn()) {
      try {
        await apiClient.budget.update({ monthly_amount: parseFloat(budget) })
      } catch (error) {
        console.error('保存預算失敗:', error)
        // 備用方案：保存到本地
        localStorage.setItem('monthlyBudget', budget.toString())
      }
    } else {
      localStorage.setItem('monthlyBudget', budget.toString())
    }
  },

  async loadBudget() {
    if (this.isLoggedIn()) {
      try {
        const budget = await apiClient.budget.get()
        return budget ? budget.monthly_amount : 0
      } catch (error) {
        console.error('從後端載入預算失敗:', error)
        // 備用方案：從本地存儲載入
        const stored = localStorage.getItem('monthlyBudget')
        return stored ? parseFloat(stored) : 0
      }
    } else {
      const stored = localStorage.getItem('monthlyBudget')
      return stored ? parseFloat(stored) : 0
    }
  },

  // 數據遷移工具
  async migrateLocalDataToBackend() {
    if (!this.isLoggedIn()) {
      throw new Error('請先登入再進行數據遷移')
    }

    try {
      // 遷移訂閱數據
      const localSubscriptions = JSON.parse(localStorage.getItem('subscriptions') || '[]')
      for (const subscription of localSubscriptions) {
        try {
          await this.createSubscription(subscription)
        } catch (error) {
          console.warn('遷移訂閱失敗:', subscription.name, error)
        }
      }

      // 遷移預算數據
      const localBudget = localStorage.getItem('monthlyBudget')
      if (localBudget) {
        await this.saveBudget(parseFloat(localBudget))
      }

      console.log('數據遷移完成')
    } catch (error) {
      console.error('數據遷移失敗:', error)
      throw error
    }
  }
}