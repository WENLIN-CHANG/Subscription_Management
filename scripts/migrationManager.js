import { dataManager } from './dataManager.js'
import { stateManager } from './stateManager.js'

// 數據遷移管理器
export const migrationManager = {
  // 檢查是否需要遷移
  needsMigration() {
    const hasLocalData = this.hasLocalData()
    const isLoggedIn = dataManager.isLoggedIn()
    const migrationCompleted = localStorage.getItem('migration_completed')
    
    return hasLocalData && isLoggedIn && !migrationCompleted
  },

  // 檢查是否有本地數據
  hasLocalData() {
    const subscriptions = localStorage.getItem('subscriptions')
    const budget = localStorage.getItem('monthlyBudget')
    
    const hasSubscriptions = subscriptions && JSON.parse(subscriptions).length > 0
    const hasBudget = budget && parseFloat(budget) > 0
    
    return hasSubscriptions || hasBudget
  },

  // 獲取本地數據統計
  getLocalDataStats() {
    const subscriptions = JSON.parse(localStorage.getItem('subscriptions') || '[]')
    const budget = parseFloat(localStorage.getItem('monthlyBudget') || '0')
    
    return {
      subscriptionCount: subscriptions.length,
      budgetAmount: budget,
      subscriptions: subscriptions.map(sub => ({
        name: sub.name,
        price: sub.price,
        cycle: sub.cycle
      }))
    }
  },

  // 執行數據遷移
  async performMigration() {
    if (!dataManager.isLoggedIn()) {
      throw new Error('請先登入再進行數據遷移')
    }

    const stats = this.getLocalDataStats()
    console.log('開始數據遷移:', stats)

    const results = {
      subscriptions: { success: 0, failed: 0, errors: [] },
      budget: { success: false, error: null },
      totalItems: stats.subscriptionCount + (stats.budgetAmount > 0 ? 1 : 0)
    }

    try {
      // 遷移訂閱數據
      const localSubscriptions = JSON.parse(localStorage.getItem('subscriptions') || '[]')
      
      for (let i = 0; i < localSubscriptions.length; i++) {
        const subscription = localSubscriptions[i]
        try {
          // 檢查必要字段
          if (!subscription.name || !subscription.price) {
            throw new Error('缺少必要字段')
          }

          const subscriptionData = {
            name: subscription.name,
            price: subscription.price,
            cycle: subscription.cycle || 'monthly',
            category: subscription.category || 'other',
            startDate: subscription.startDate || new Date().toISOString().split('T')[0]
          }

          await dataManager.createSubscription(subscriptionData)
          results.subscriptions.success++
          
          // 更新進度
          const progress = Math.round(((results.subscriptions.success + results.subscriptions.failed) / results.totalItems) * 100)
          this.updateMigrationProgress(progress, `已遷移訂閱: ${subscription.name}`)
          
        } catch (error) {
          console.warn('遷移訂閱失敗:', subscription.name, error)
          results.subscriptions.failed++
          results.subscriptions.errors.push({
            item: subscription.name,
            error: error.message
          })
        }
      }

      // 遷移預算數據
      const localBudget = localStorage.getItem('monthlyBudget')
      if (localBudget && parseFloat(localBudget) > 0) {
        try {
          await dataManager.saveBudget(parseFloat(localBudget))
          results.budget.success = true
          this.updateMigrationProgress(100, '預算數據遷移完成')
        } catch (error) {
          console.warn('遷移預算失敗:', error)
          results.budget.error = error.message
        }
      }

      // 標記遷移完成
      localStorage.setItem('migration_completed', 'true')
      localStorage.setItem('migration_results', JSON.stringify(results))
      
      return results
      
    } catch (error) {
      console.error('數據遷移失敗:', error)
      throw error
    }
  },

  // 更新遷移進度
  updateMigrationProgress(percentage, message) {
    const progressBar = document.getElementById('migration-progress-bar')
    const progressText = document.getElementById('migration-progress-text')
    
    if (progressBar) {
      progressBar.style.width = `${percentage}%`
      progressBar.setAttribute('aria-valuenow', percentage)
    }
    
    if (progressText) {
      progressText.textContent = message
    }

    // 觸發自定義事件
    window.dispatchEvent(new CustomEvent('migrationProgress', {
      detail: { percentage, message }
    }))
  },

  // 顯示遷移對話框
  showMigrationDialog() {
    const stats = this.getLocalDataStats()
    
    // 移除現有對話框
    const existingDialog = document.getElementById('migration-dialog')
    if (existingDialog) {
      existingDialog.remove()
    }

    const dialog = document.createElement('div')
    dialog.id = 'migration-dialog'
    dialog.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
    dialog.innerHTML = `
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">數據遷移</h3>
          <button onclick="migrationManager.hideMigrationDialog()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="mb-4">
          <p class="text-gray-600 mb-2">發現本地數據，是否要遷移到雲端？</p>
          <div class="text-sm text-gray-500">
            <p>• 訂閱記錄: ${stats.subscriptionCount} 項</p>
            <p>• 月度預算: $${stats.budgetAmount}</p>
          </div>
        </div>

        <div id="migration-progress" class="mb-4 hidden">
          <div class="bg-gray-200 rounded-full h-2 mb-2">
            <div id="migration-progress-bar" class="bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
          </div>
          <p id="migration-progress-text" class="text-sm text-gray-600 text-center">準備中...</p>
        </div>

        <div class="flex space-x-3">
          <button onclick="migrationManager.startMigration()" 
                  data-loading="migration"
                  class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50">
            開始遷移
          </button>
          <button onclick="migrationManager.skipMigration()" 
                  class="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400">
            暫時跳過
          </button>
        </div>

        <div class="mt-3 text-xs text-gray-500 text-center">
          遷移完成後，本地數據仍會保留作為備份
        </div>
      </div>
    `
    
    document.body.appendChild(dialog)
    
    // 將 migrationManager 設為全局變量
    window.migrationManager = this
  },

  // 隱藏遷移對話框
  hideMigrationDialog() {
    const dialog = document.getElementById('migration-dialog')
    if (dialog) {
      dialog.remove()
    }
  },

  // 開始遷移
  async startMigration() {
    const progressContainer = document.getElementById('migration-progress')
    if (progressContainer) {
      progressContainer.classList.remove('hidden')
    }

    try {
      const results = await stateManager.withLoading('migration', 
        () => this.performMigration(),
        {
          errorContext: '數據遷移',
          successMessage: '數據遷移完成！',
          successContext: '遷移'
        }
      )

      // 顯示遷移結果
      this.showMigrationResults(results)
      
    } catch (error) {
      console.error('遷移失敗:', error)
      
      // 顯示錯誤詳情
      const progressText = document.getElementById('migration-progress-text')
      if (progressText) {
        progressText.textContent = `遷移失敗: ${error.message}`
        progressText.className = 'text-sm text-red-600 text-center'
      }
    }
  },

  // 跳過遷移
  skipMigration() {
    localStorage.setItem('migration_skipped', 'true')
    this.hideMigrationDialog()
    stateManager.success.show('已跳過數據遷移', '遷移')
  },

  // 顯示遷移結果
  showMigrationResults(results) {
    const dialog = document.getElementById('migration-dialog')
    if (!dialog) return

    const successCount = results.subscriptions.success + (results.budget.success ? 1 : 0)
    const failCount = results.subscriptions.failed + (results.budget.error ? 1 : 0)

    dialog.innerHTML = `
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">遷移完成</h3>
          <button onclick="migrationManager.hideMigrationDialog()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="mb-4">
          <div class="text-center mb-4">
            <div class="w-16 h-16 mx-auto mb-2 rounded-full ${successCount > failCount ? 'bg-green-100' : 'bg-yellow-100'} flex items-center justify-center">
              <svg class="w-8 h-8 ${successCount > failCount ? 'text-green-600' : 'text-yellow-600'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <p class="text-lg font-medium text-gray-900">遷移結果</p>
          </div>
          
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span>成功項目:</span>
              <span class="text-green-600 font-medium">${successCount}</span>
            </div>
            <div class="flex justify-between">
              <span>失敗項目:</span>
              <span class="text-red-600 font-medium">${failCount}</span>
            </div>
            <div class="border-t pt-2 mt-2">
              <p class="text-gray-600">訂閱: ${results.subscriptions.success}/${results.subscriptions.success + results.subscriptions.failed}</p>
              <p class="text-gray-600">預算: ${results.budget.success ? '成功' : '失敗'}</p>
            </div>
          </div>
          
          ${results.subscriptions.errors.length > 0 ? `
            <details class="mt-3">
              <summary class="text-sm text-red-600 cursor-pointer">查看錯誤詳情</summary>
              <div class="mt-1 text-xs text-gray-500 max-h-20 overflow-y-auto">
                ${results.subscriptions.errors.map(err => `<p>• ${err.item}: ${err.error}</p>`).join('')}
              </div>
            </details>
          ` : ''}
        </div>

        <button onclick="migrationManager.hideMigrationDialog()" 
                class="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
          完成
        </button>
      </div>
    `

    // 5秒後自動關閉
    setTimeout(() => {
      this.hideMigrationDialog()
    }, 5000)
  },

  // 重置遷移狀態（用於測試）
  resetMigrationState() {
    localStorage.removeItem('migration_completed')
    localStorage.removeItem('migration_skipped')
    localStorage.removeItem('migration_results')
    console.log('遷移狀態已重置')
  },

  // 檢查並提示遷移
  checkAndPromptMigration() {
    // 延遲檢查，確保頁面完全載入
    setTimeout(() => {
      if (this.needsMigration()) {
        this.showMigrationDialog()
      }
    }, 1000)
  }
}

// 導出到全局
window.migrationManager = migrationManager