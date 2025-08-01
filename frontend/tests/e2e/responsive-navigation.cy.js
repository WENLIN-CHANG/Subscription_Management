// 響應式導航測試
describe('響應式導航和選單', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForAlpine()
  })

  describe('桌面版導航', () => {
    beforeEach(() => {
      cy.viewport(1280, 720) // 桌面尺寸
    })

    it('應該顯示完整的導航選單', () => {
      // 應該顯示標題
      cy.get('[data-testid="site-title"]').should('be.visible').should('contain', '訂閱管理系統')
      
      // 應該顯示桌面版導航選單
      cy.get('[data-testid="desktop-nav"]').should('be.visible')
      cy.get('[data-testid="nav-dashboard"]').should('be.visible').should('contain', '儀表板')
      cy.get('[data-testid="nav-subscriptions"]').should('be.visible').should('contain', '我的訂閱')
      
      // 不應該顯示漢堡選單按鈕
      cy.get('[data-testid="mobile-menu-button"]').should('not.be.visible')
    })

    it('應該顯示主題切換器', () => {
      cy.get('[data-testid="theme-toggle"]').should('be.visible')
    })

    it('點擊導航項目應該滾動到對應區域', () => {
      // 點擊儀表板
      cy.get('[data-testid="nav-dashboard"]').click()
      
      // 應該滾動到儀表板區域
      cy.get('[data-testid="dashboard-section"]').should('be.visible')
      
      // 點擊我的訂閱
      cy.get('[data-testid="nav-subscriptions"]').click()
      
      // 應該滾動到訂閱區域
      cy.get('[data-testid="subscriptions-section"]').should('be.visible')
    })

    it('點擊標題應該滾動到頂部', () => {
      // 先滾動到底部
      cy.scrollTo('bottom')
      
      // 點擊標題
      cy.get('[data-testid="site-title"]').click()
      
      // 應該回到頂部
      cy.window().its('scrollY').should('equal', 0)
    })
  })

  describe('平板版導航', () => {
    beforeEach(() => {
      cy.viewport(768, 1024) // 平板尺寸
    })

    it('應該顯示縮短的標題', () => {
      cy.get('[data-testid="site-title-mobile"]').should('be.visible').should('contain', '訂閱管理')
      cy.get('[data-testid="site-title-desktop"]').should('not.be.visible')
    })

    it('應該仍然顯示桌面版導航', () => {
      cy.get('[data-testid="desktop-nav"]').should('be.visible')
      cy.get('[data-testid="mobile-menu-button"]').should('not.be.visible')
    })
  })

  describe('手機版導航', () => {
    beforeEach(() => {
      cy.viewport(375, 667) // 手機尺寸
    })

    it('應該顯示漢堡選單按鈕並隱藏桌面版導航', () => {
      // 應該顯示漢堡選單按鈕
      cy.get('[data-testid="mobile-menu-button"]').should('be.visible')
      
      // 應該隱藏桌面版導航
      cy.get('[data-testid="desktop-nav"]').should('not.be.visible')
      
      // 選單應該初始為關閉狀態
      cy.get('[data-testid="mobile-menu"]').should('not.be.visible')
    })

    it('點擊漢堡選單按鈕應該開啟/關閉選單', () => {
      // 點擊開啟選單
      cy.get('[data-testid="mobile-menu-button"]').click()
      
      // 選單應該顯示
      cy.get('[data-testid="mobile-menu"]').should('be.visible')
      
      // 漢堡圖示應該變成關閉圖示
      cy.get('[data-testid="hamburger-icon"]').should('not.be.visible')
      cy.get('[data-testid="close-icon"]').should('be.visible')
      
      // 再次點擊應該關閉選單
      cy.get('[data-testid="mobile-menu-button"]').click()
      
      // 選單應該隱藏
      cy.get('[data-testid="mobile-menu"]').should('not.be.visible')
      
      // 關閉圖示應該變回漢堡圖示
      cy.get('[data-testid="close-icon"]').should('not.be.visible')
      cy.get('[data-testid="hamburger-icon"]').should('be.visible')
    })

    it('手機選單應該包含所有導航項目', () => {
      // 開啟選單
      cy.get('[data-testid="mobile-menu-button"]').click()
      
      // 檢查選單項目
      cy.get('[data-testid="mobile-nav-dashboard"]').should('be.visible').should('contain', '儀表板')
      cy.get('[data-testid="mobile-nav-subscriptions"]').should('be.visible').should('contain', '我的訂閱')
    })

    it('點擊手機選單項目應該關閉選單並滾動', () => {
      // 開啟選單
      cy.get('[data-testid="mobile-menu-button"]').click()
      
      // 點擊儀表板
      cy.get('[data-testid="mobile-nav-dashboard"]').click()
      
      // 選單應該關閉
      cy.get('[data-testid="mobile-menu"]').should('not.be.visible')
      
      // 應該滾動到儀表板區域
      cy.get('[data-testid="dashboard-section"]').should('be.visible')
    })

    it('點擊遮罩應該關閉選單', () => {
      // 開啟選單
      cy.get('[data-testid="mobile-menu-button"]').click()
      
      // 點擊遮罩
      cy.get('[data-testid="mobile-menu-overlay"]').click({ force: true })
      
      // 選單應該關閉
      cy.get('[data-testid="mobile-menu"]').should('not.be.visible')
    })

    it('選單開啟時應該有適當的動畫效果', () => {
      // 開啟選單
      cy.get('[data-testid="mobile-menu-button"]').click()
      
      // 檢查動畫相關的 CSS 類
      cy.get('[data-testid="mobile-menu"]')
        .should('have.class', 'transition-opacity')
        .should('have.class', 'transition-transform')
    })
  })

  describe('認證狀態顯示', () => {
    it('未登入時應該顯示登入/註冊按鈕', () => {
      cy.get('[data-testid="auth-buttons"]').should('be.visible')
      cy.get('[data-testid="login-button"]').should('be.visible').should('contain', '登入')
      cy.get('[data-testid="register-button"]').should('be.visible').should('contain', '註冊')
      
      // 不應該顯示用戶資訊
      cy.get('[data-testid="user-info"]').should('not.be.visible')
    })

    it('登入後應該顯示用戶資訊和下拉選單', () => {
      // 模擬登入
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
      })

      // 應該顯示用戶資訊
      cy.get('[data-testid="user-info"]').should('be.visible')
      cy.get('[data-testid="user-avatar"]').should('be.visible').should('contain', 'T')
      cy.get('[data-testid="username"]').should('be.visible').should('contain', 'testuser')
      
      // 不應該顯示登入/註冊按鈕
      cy.get('[data-testid="auth-buttons"]').should('not.be.visible')
    })

    it('用戶下拉選單應該正常工作', () => {
      // 模擬登入
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
      })

      // 點擊下拉選單按鈕
      cy.get('[data-testid="user-dropdown-button"]').click()
      
      // 應該顯示下拉選單項目
      cy.get('[data-testid="change-password-button"]').should('be.visible').should('contain', '修改密碼')
      cy.get('[data-testid="logout-button"]').should('be.visible').should('contain', '登出')
    })
  })

  describe('主題切換功能', () => {
    it('主題切換器應該在所有裝置尺寸下可見', () => {
      const sizes = [
        [375, 667],   // 手機
        [768, 1024],  // 平板
        [1280, 720]   // 桌面
      ]

      sizes.forEach(([width, height]) => {
        cy.viewport(width, height)
        cy.get('[data-testid="theme-toggle"]').should('be.visible')
      })
    })

    it('點擊主題切換器應該切換主題', () => {
      // 初始主題應該是亮色
      cy.get('html').should('have.attr', 'data-theme', 'corporate')
      
      // 點擊切換到暗色主題
      cy.get('[data-testid="theme-toggle-input"]').check({ force: true })
      
      // 主題應該變更
      cy.get('html').should('have.attr', 'data-theme', 'dark')
      
      // 再次點擊切換回亮色主題
      cy.get('[data-testid="theme-toggle-input"]').uncheck({ force: true })
      
      // 主題應該變回亮色
      cy.get('html').should('have.attr', 'data-theme', 'corporate')
    })

    it('主題切換器應該顯示適當的圖示', () => {
      // 亮色主題時應該顯示太陽圖示
      cy.get('[data-testid="sun-icon"]').should('be.visible')
      cy.get('[data-testid="moon-icon"]').should('not.be.visible')
      
      // 切換到暗色主題
      cy.get('[data-testid="theme-toggle-input"]').check({ force: true })
      
      // 暗色主題時應該顯示月亮圖示
      cy.get('[data-testid="moon-icon"]').should('be.visible')
      cy.get('[data-testid="sun-icon"]').should('not.be.visible')
    })
  })

  describe('無障礙功能', () => {
    it('所有互動元素應該可以用鍵盤操作', () => {
      // 檢查標題可以聚焦
      cy.get('[data-testid="site-title"]').should('have.attr', 'tabindex').or('be.focusable')
      
      // 檢查導航按鈕可以聚焦
      cy.get('[data-testid="nav-dashboard"]').should('be.focusable')
      cy.get('[data-testid="nav-subscriptions"]').should('be.focusable')
      
      // 檢查主題切換器可以聚焦
      cy.get('[data-testid="theme-toggle-input"]').should('be.focusable')
      
      // 檢查認證按鈕可以聚焦
      cy.get('[data-testid="login-button"]').should('be.focusable')
      cy.get('[data-testid="register-button"]').should('be.focusable')
    })

    it('應該有適當的 ARIA 標籤', () => {
      cy.viewport(375, 667) // 手機尺寸

      // 漢堡選單按鈕應該有適當的標籤
      cy.get('[data-testid="mobile-menu-button"]')
        .should('have.attr', 'aria-label')
        .or('have.attr', 'title')
      
      // 主題切換器應該有標籤
      cy.get('[data-testid="theme-toggle-input"]')
        .should('have.attr', 'aria-label')
        .or('have.attr', 'title')
    })
  })
})