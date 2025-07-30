import Alpine from 'alpinejs'

// 訂閱管理主要組件
Alpine.data('subscriptionManager', () => ({
  // 數據狀態
  subscriptions: [],
  monthlyTotal: 0,
  newSubscription: {
    name: '',
    price: '',
    cycle: 'monthly',
    category: '',
    startDate: ''
  },
  editingSubscription: null,
  isEditing: false,
  monthlyBudget: 0,
  showBudgetSetting: false,
  tempBudget: '',

  // 初始化
  init() {
    this.loadFromStorage()
    this.loadBudgetFromStorage()
    this.calculateMonthlyTotal()
  },

  // 新增訂閱
  addSubscription() {
    if (this.validateForm()) {
      const subscription = {
        id: Date.now(),
        name: this.newSubscription.name,
        price: parseFloat(this.newSubscription.price),
        cycle: this.newSubscription.cycle,
        category: this.newSubscription.category,
        startDate: this.newSubscription.startDate
      }
      
      this.subscriptions.push(subscription)
      this.resetForm()
      this.calculateMonthlyTotal()
      this.saveToStorage()
    }
  },

  // 刪除訂閱
  deleteSubscription(id) {
    if (confirm('確定要刪除這個訂閱嗎？')) {
      this.subscriptions = this.subscriptions.filter(sub => sub.id !== id)
      this.calculateMonthlyTotal()
      this.saveToStorage()
    }
  },

  // 開始編輯訂閱
  editSubscription(id) {
    const subscription = this.subscriptions.find(sub => sub.id === id)
    if (subscription) {
      this.editingSubscription = { ...subscription }
      this.newSubscription = {
        name: subscription.name,
        price: subscription.price.toString(),
        cycle: subscription.cycle,
        category: subscription.category,
        startDate: subscription.startDate
      }
      this.isEditing = true
      // 滾動到表單位置
      setTimeout(() => {
        document.querySelector('form').scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
  },

  // 取消編輯
  cancelEdit() {
    this.isEditing = false
    this.editingSubscription = null
    this.resetForm()
  },

  // 更新訂閱
  updateSubscription() {
    if (this.validateForm()) {
      const index = this.subscriptions.findIndex(sub => sub.id === this.editingSubscription.id)
      if (index !== -1) {
        this.subscriptions[index] = {
          ...this.editingSubscription,
          name: this.newSubscription.name,
          price: parseFloat(this.newSubscription.price),
          cycle: this.newSubscription.cycle,
          category: this.newSubscription.category,
          startDate: this.newSubscription.startDate
        }
        this.cancelEdit()
        this.calculateMonthlyTotal()
        this.saveToStorage()
      }
    }
  },

  // 表單驗證
  validateForm() {
    if (!this.newSubscription.name.trim()) {
      alert('請輸入服務名稱')
      return false
    }
    if (!this.newSubscription.price || this.newSubscription.price <= 0) {
      alert('請輸入有效的價格')
      return false
    }
    if (!this.newSubscription.category) {
      alert('請選擇服務分類')
      return false
    }
    if (!this.newSubscription.startDate) {
      alert('請選擇開始日期')
      return false
    }
    return true
  },

  // 重置表單
  resetForm() {
    this.newSubscription = {
      name: '',
      price: '',
      cycle: 'monthly',
      category: '',
      startDate: ''
    }
  },

  // 計算月支出總額
  calculateMonthlyTotal() {
    this.monthlyTotal = this.subscriptions.reduce((total, subscription) => {
      return total + this.getMonthlyPrice(subscription)
    }, 0)
  },

  // 獲取月費用
  getMonthlyPrice(subscription) {
    const price = parseFloat(subscription.price)
    switch (subscription.cycle) {
      case 'monthly':
        return price
      case 'quarterly':
        return price / 3
      case 'yearly':
        return price / 12
      default:
        return price
    }
  },

  // 獲取週期名稱
  getCycleName(cycle) {
    const names = {
      monthly: '每月',
      quarterly: '每季',
      yearly: '每年'
    }
    return names[cycle] || cycle
  },

  // 獲取分類名稱
  getCategoryName(category) {
    const names = {
      entertainment: '娛樂影音',
      productivity: '生產力工具',
      storage: '雲端存儲',
      fitness: '健身運動',
      education: '教育學習',
      news: '新聞資訊',
      other: '其他'
    }
    return names[category] || category
  },

  // 獲取分類顏色
  getCategoryColor(category) {
    const colors = {
      entertainment: 'border-red-400',
      productivity: 'border-blue-400',
      storage: 'border-green-400',
      fitness: 'border-orange-400',
      education: 'border-purple-400',
      news: 'border-yellow-400',
      other: 'border-gray-400'
    }
    return colors[category] || 'border-gray-400'
  },

  // 格式化日期
  formatDate(dateString) {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-TW')
  },

  // 獲取下次付款日期
  getNextPaymentDate(subscription) {
    const startDate = new Date(subscription.startDate)
    const today = new Date()
    
    let nextDate = new Date(startDate)
    
    switch (subscription.cycle) {
      case 'monthly':
        while (nextDate <= today) {
          nextDate.setMonth(nextDate.getMonth() + 1)
        }
        break
      case 'quarterly':
        while (nextDate <= today) {
          nextDate.setMonth(nextDate.getMonth() + 3)
        }
        break
      case 'yearly':
        while (nextDate <= today) {
          nextDate.setFullYear(nextDate.getFullYear() + 1)
        }
        break
    }
    
    return nextDate.toLocaleDateString('zh-TW')
  },

  // 計算距離下次付款的天數
  getDaysUntilPayment(subscription) {
    const startDate = new Date(subscription.startDate)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    let nextDate = new Date(startDate)
    
    switch (subscription.cycle) {
      case 'monthly':
        while (nextDate <= today) {
          nextDate.setMonth(nextDate.getMonth() + 1)
        }
        break
      case 'quarterly':
        while (nextDate <= today) {
          nextDate.setMonth(nextDate.getMonth() + 3)
        }
        break
      case 'yearly':
        while (nextDate <= today) {
          nextDate.setFullYear(nextDate.getFullYear() + 1)
        }
        break
    }
    
    const diffTime = nextDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  },

  // 獲取到期提醒樣式
  getExpiryWarningClass(subscription) {
    const days = this.getDaysUntilPayment(subscription)
    if (days <= 3) {
      return 'text-red-600 font-semibold'
    } else if (days <= 7) {
      return 'text-orange-600 font-medium'
    }
    return 'text-gray-600'
  },

  // 獲取到期提醒文字
  getExpiryWarningText(subscription) {
    const days = this.getDaysUntilPayment(subscription)
    if (days <= 0) {
      return '今天到期！'
    } else if (days === 1) {
      return '明天到期'
    } else if (days <= 3) {
      return `${days} 天後到期`
    } else if (days <= 7) {
      return `${days} 天後到期`
    }
    return `${days} 天後`
  },

  // 獲取即將到期的訂閱
  getUpcomingExpiry() {
    return this.subscriptions.filter(sub => this.getDaysUntilPayment(sub) <= 7)
  },

  // 獲取分類統計數據
  getCategoryStats() {
    const stats = {}
    let total = 0
    
    this.subscriptions.forEach(subscription => {
      const monthlyPrice = this.getMonthlyPrice(subscription)
      const category = subscription.category
      
      if (!stats[category]) {
        stats[category] = {
          name: this.getCategoryName(category),
          amount: 0,
          count: 0,
          color: this.getCategoryBgColor(category),
          progressColor: this.getCategoryProgressColor(category),
          originalCategory: category
        }
      }
      
      stats[category].amount += monthlyPrice
      stats[category].count += 1
      total += monthlyPrice
    })
    
    // 計算百分比
    Object.keys(stats).forEach(category => {
      stats[category].percentage = total > 0 ? (stats[category].amount / total * 100).toFixed(1) : 0
    })
    
    return Object.values(stats).sort((a, b) => b.amount - a.amount)
  },

  // 獲取分類背景顏色
  getCategoryBgColor(category) {
    const colors = {
      entertainment: 'bg-red-100 text-red-800',
      productivity: 'bg-blue-100 text-blue-800',
      storage: 'bg-green-100 text-green-800',
      fitness: 'bg-orange-100 text-orange-800',
      education: 'bg-purple-100 text-purple-800',
      news: 'bg-yellow-100 text-yellow-800',
      other: 'bg-gray-100 text-gray-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  },

  // 獲取分類進度條顏色
  getCategoryProgressColor(category) {
    const colors = {
      entertainment: 'bg-red-400',
      productivity: 'bg-blue-400',
      storage: 'bg-green-400',
      fitness: 'bg-orange-400',
      education: 'bg-purple-400',
      news: 'bg-yellow-400',
      other: 'bg-gray-400'
    }
    return colors[category] || 'bg-gray-400'
  },

  // 本地存儲
  saveToStorage() {
    localStorage.setItem('subscriptions', JSON.stringify(this.subscriptions))
  },

  loadFromStorage() {
    const stored = localStorage.getItem('subscriptions')
    if (stored) {
      this.subscriptions = JSON.parse(stored)
    }
  },

  // 預算相關方法
  loadBudgetFromStorage() {
    const stored = localStorage.getItem('monthlyBudget')
    if (stored) {
      this.monthlyBudget = parseFloat(stored)
    }
  },

  saveBudgetToStorage() {
    localStorage.setItem('monthlyBudget', this.monthlyBudget.toString())
  },

  openBudgetSetting() {
    this.tempBudget = this.monthlyBudget.toString()
    this.showBudgetSetting = true
  },

  closeBudgetSetting() {
    this.showBudgetSetting = false
    this.tempBudget = ''
  },

  saveBudget() {
    const budget = parseFloat(this.tempBudget)
    if (!isNaN(budget) && budget >= 0) {
      this.monthlyBudget = budget
      this.saveBudgetToStorage()
      this.closeBudgetSetting()
    } else {
      alert('請輸入有效的預算金額')
    }
  },

  // 預算相關計算
  getBudgetUsagePercentage() {
    if (this.monthlyBudget <= 0) return 0
    return Math.min((this.monthlyTotal / this.monthlyBudget * 100), 100)
  },

  getBudgetStatus() {
    if (this.monthlyBudget <= 0) return 'none'
    const percentage = this.getBudgetUsagePercentage()
    if (percentage >= 100) return 'over'
    if (percentage >= 80) return 'warning'
    return 'good'
  },

  getBudgetStatusText() {
    const status = this.getBudgetStatus()
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

  getBudgetStatusColor() {
    const status = this.getBudgetStatus()
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

  getRemainingBudget() {
    return Math.max(this.monthlyBudget - this.monthlyTotal, 0)
  },

  // 格式化貨幣顯示
  formatCurrency(amount) {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  },

  // 格式化數字（千分位分隔符）
  formatNumber(number) {
    return new Intl.NumberFormat('zh-TW').format(number)
  }
}))

window.Alpine = Alpine
Alpine.start()