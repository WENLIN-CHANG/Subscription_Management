// 範例資料管理
export const sampleData = {
  // 精選的範例訂閱服務
  subscriptions: [
    {
      id: 'sample-netflix',
      name: 'Netflix',
      price: 390,
      originalPrice: 390,
      currency: 'TWD',
      cycle: 'monthly',
      category: 'streaming',
      startDate: '2024-01-15'
    },
    {
      id: 'sample-spotify',
      name: 'Spotify Premium',
      price: 149,
      originalPrice: 149,
      currency: 'TWD',
      cycle: 'monthly',
      category: 'music',
      startDate: '2024-02-01'
    },
    {
      id: 'sample-adobe',
      name: 'Adobe Creative Suite',
      price: 1680,
      originalPrice: 1680,
      currency: 'TWD',
      cycle: 'monthly',
      category: 'software',
      startDate: '2024-01-01'
    },
    {
      id: 'sample-youtube',
      name: 'YouTube Premium',
      price: 179,
      originalPrice: 179,
      currency: 'TWD',
      cycle: 'monthly',
      category: 'streaming',
      startDate: '2024-03-10'
    },
    {
      id: 'sample-notion',
      name: 'Notion Pro',
      price: 320,
      originalPrice: 8,
      currency: 'USD',
      cycle: 'monthly',
      category: 'productivity',
      startDate: '2024-02-15'
    },
    {
      id: 'sample-office365',
      name: 'Microsoft 365',
      price: 2190,
      originalPrice: 2190,
      currency: 'TWD',
      cycle: 'yearly',
      category: 'productivity',
      startDate: '2024-01-20'
    }
  ],

  // 範例預算
  budget: 3000,

  // 獲取範例訂閱
  getSampleSubscriptions() {
    // 為每個範例訂閱生成更真實的開始日期（在過去3-6個月內）
    const today = new Date()
    return this.subscriptions.map(sub => ({
      ...sub,
      startDate: this.generateRealisticStartDate(today)
    }))
  },

  // 生成真實的開始日期
  generateRealisticStartDate(today) {
    const daysBack = Math.floor(Math.random() * 180) + 30 // 30-210天前
    const startDate = new Date(today)
    startDate.setDate(startDate.getDate() - daysBack)
    return startDate.toISOString().split('T')[0]
  },

  // 獲取範例預算
  getSampleBudget() {
    return this.budget
  },

  // 檢查是否為範例資料
  isSampleData(subscriptionId) {
    return subscriptionId && subscriptionId.startsWith('sample-')
  },

  // 獲取範例資料說明
  getSampleDataInfo() {
    return {
      isDemo: true,
      message: '這些是範例資料，用於展示系統功能。登入後可以建立您的真實訂閱記錄。',
      totalServices: this.subscriptions.length,
      estimatedMonthly: this.subscriptions.reduce((total, sub) => {
        const monthlyPrice = sub.cycle === 'yearly' ? sub.price / 12 : 
                           sub.cycle === 'quarterly' ? sub.price / 3 : sub.price
        return total + monthlyPrice
      }, 0)
    }
  }
}