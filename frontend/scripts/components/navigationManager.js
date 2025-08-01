// 導航管理器 - 負責導航欄和響應式選單
export function navigationManager() {
  return {
    // 獲取全局狀態
    get mobileMenuOpen() {
      return this.$store.app.mobileMenuOpen
    },
    
    get isLoggedIn() {
      return this.$store.app.isLoggedIn
    },
    
    get currentUser() {
      return this.$store.app.currentUser
    },
    
    get currentTheme() {
      return this.$store.app.currentTheme
    },
    
    // 響應式導航方法
    toggleMobileMenu() {
      this.$store.app.toggleMobileMenu()
    },
    
    closeMobileMenu() {
      this.$store.app.closeMobileMenu()
    },
    
    // 選單項目點擊時關閉選單並滾動到指定區域
    navigateAndCloseMobile(sectionId) {
      this.closeMobileMenu()
      this.scrollToSection(sectionId)
    },
    
    // 導航滾動功能
    scrollToSection(sectionId) {
      // 如果是未登入用戶且點擊需要登入的功能，顯示登入提示
      if (!this.isLoggedIn && (sectionId === 'subscriptions')) {
        const { authManager } = window
        if (authManager) {
          authManager.showAuthDialog('login')
        }
        return
      }
      
      const element = document.getElementById(sectionId)
      if (element) {
        // 考慮固定導航欄的高度 (約80px)
        const navbarHeight = 80
        const elementPosition = element.offsetTop - navbarHeight
        
        window.scrollTo({
          top: elementPosition,
          behavior: 'smooth'
        })
      }
    },
    
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    
    // 主題相關方法
    getCurrentThemeType() {
      const { themeManager } = window
      return themeManager ? themeManager.getCurrentThemeType() : 'light'
    },
    
    toggleTheme() {
      const { themeManager } = window
      if (themeManager && themeManager.toggleTheme()) {
        this.$store.app.setTheme(themeManager.currentTheme)
      }
    },
    
    // 認證相關方法
    showLogin() {
      const { authManager } = window
      if (authManager) {
        authManager.showAuthDialog('login')
      }
    },
    
    showRegister() {
      const { authManager } = window
      if (authManager) {
        authManager.showAuthDialog('register')
      }
    },
    
    logout() {
      const { authManager } = window
      if (authManager) {
        authManager.logout()
      }
    },
    
    showChangePasswordDialog() {
      const { authManager } = window
      if (authManager) {
        authManager.showChangePasswordDialog()
      }
    }
  }
}