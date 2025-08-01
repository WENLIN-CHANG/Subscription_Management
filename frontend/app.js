import Alpine from 'alpinejs'
import { dataManager } from './scripts/data/dataManager.js'
import { calculationUtils } from './scripts/utils/calculationUtils.js'
import { uiUtils } from './scripts/ui/uiUtils.js'
import { stateManager } from './scripts/ui/stateManager.js'
import { migrationManager } from './scripts/data/migrationManager.js'
import { authManager } from './scripts/auth/authManager.js'
import { themeManager } from './scripts/ui/themeManager.js'
import { initializeGlobalStore } from './scripts/ui/globalStore.js'
import { dashboardManager } from './scripts/components/dashboardManager.js'
import { subscriptionListManager } from './scripts/components/subscriptionListManager.js'
import { subscriptionFormManager } from './scripts/components/subscriptionFormManager.js'
import { navigationManager } from './scripts/components/navigationManager.js'

// 主應用初始化組件
Alpine.data('appManager', () => ({
  // 初始化
  async init() {
    try {
      // 初始化狀態管理器
      if (!window.stateManager) {
        stateManager.init()
      }
      
      // 初始化認證狀態
      const isLoggedIn = await authManager.init()
      const currentUser = authManager.currentUser
      this.$store.app.setAuth(isLoggedIn, currentUser)
      
      // 初始化主題管理器
      themeManager.init()
      this.$store.app.setTheme(themeManager.currentTheme)
      
      // 載入數據
      await stateManager.withLoading('init', async () => {
        const subscriptions = await dataManager.loadSubscriptions()
        const monthlyBudget = await dataManager.loadBudget()
        
        this.$store.app.setSubscriptions(subscriptions)
        this.$store.app.setBudget(monthlyBudget)
      }, {
        errorContext: '初始化',
        successMessage: null // 不顯示成功訊息
      })
      
      // 檢查是否需要數據遷移
      migrationManager.checkAndPromptMigration()
      
    } catch (error) {
      console.error('初始化失敗:', error)
      stateManager.error.set(error, '初始化')
    }
  },

  // 監聽認證狀態變化
  authStateChanged(isLoggedIn, user) {
    this.$store.app.setAuth(isLoggedIn, user)
    
    // 如果登入成功，重新載入數據
    if (isLoggedIn) {
      this.loadUserData()
    }
  },
  
  // 載入用戶數據
  async loadUserData() {
    try {
      await stateManager.withLoading('loadData', async () => {
        const subscriptions = await dataManager.loadSubscriptions()
        const monthlyBudget = await dataManager.loadBudget()
        
        this.$store.app.setSubscriptions(subscriptions)
        this.$store.app.setBudget(monthlyBudget)
      })
    } catch (error) {
      console.error('載入用戶資料失敗:', error)
      stateManager.error.set(error, '載入資料')
    }
  }
}))

// 註冊組件
Alpine.data('dashboardManager', dashboardManager)
Alpine.data('subscriptionListManager', subscriptionListManager)
Alpine.data('subscriptionFormManager', subscriptionFormManager)
Alpine.data('navigationManager', navigationManager)

// 初始化全局狀態
initializeGlobalStore(Alpine)

// 將工具模組設為全局變量供組件使用
window.calculationUtils = calculationUtils
window.uiUtils = uiUtils
window.authManager = authManager
window.themeManager = themeManager
window.dataManager = dataManager

window.Alpine = Alpine
Alpine.start()