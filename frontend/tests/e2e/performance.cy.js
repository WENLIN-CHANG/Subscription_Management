// 性能測試
describe('性能測試', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForAlpine()
  })

  describe('頁面載入性能', () => {
    it('頁面應該在合理時間內載入完成', () => {
      cy.window().then((win) => {
        // 檢查 Alpine.js 是否正確載入
        expect(win.Alpine).to.exist
        
        // 檢查全局工具是否載入
        expect(win.calculationUtils).to.exist
        expect(win.uiUtils).to.exist
        expect(win.authManager).to.exist
        expect(win.themeManager).to.exist
        expect(win.dataManager).to.exist
      })

      // 主要 UI 元素應該快速顯示
      cy.get('[data-testid="site-title"]', { timeout: 1000 }).should('be.visible')
      cy.get('[data-testid="monthly-total"]', { timeout: 1000 }).should('be.visible')
      cy.get('[data-testid="theme-toggle"]', { timeout: 1000 }).should('be.visible')
    })

    it('Alpine.js 初始化應該快速完成', () => {
      cy.window().then((win) => {
        // 檢查 store 是否已初始化
        expect(win.Alpine.store('app')).to.exist
        
        // 檢查 store 的基本狀態
        const store = win.Alpine.store('app')
        expect(store.subscriptions).to.be.an('array')
        expect(store.monthlyTotal).to.be.a('number')
        expect(store.isLoggedIn).to.be.a('boolean')
      })
    })

    it('樣式載入不應該造成 FOUC (Flash of Unstyled Content)', () => {
      // 檢查關鍵元素是否有正確的樣式
      cy.get('[data-testid="site-title"]').should('have.css', 'font-weight', '700')
      cy.get('body').should('have.css', 'margin', '0px')
    })
  })

  describe('操作響應時間', () => {
    beforeEach(() => {
      // 模擬登入以測試操作
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
      })
    })

    it('新增訂閱操作應該快速響應', () => {
      const startTime = Date.now()

      cy.addSubscription({
        name: 'Performance Test Service',
        price: '299'
      })

      cy.get('[data-testid="subscription-card"]')
        .contains('Performance Test Service')
        .should('be.visible')
        .then(() => {
          const endTime = Date.now()
          const operationTime = endTime - startTime
          
          // 操作應該在 2 秒內完成
          expect(operationTime).to.be.lessThan(2000)
        })
    })

    it('月度總計更新應該即時', () => {
      // 記錄初始總計
      cy.get('[data-testid="monthly-total"]').invoke('text').then((initialTotal) => {
        // 添加訂閱
        cy.addSubscription({
          name: 'Quick Test',
          price: '100'
        })

        // 總計應該立即更新（考慮動畫時間）
        cy.get('[data-testid="monthly-total"]', { timeout: 1000 })
          .should('not.contain', initialTotal)
          .should('contain', '100')
      })
    })

    it('主題切換應該即時響應', () => {
      // 記錄初始主題
      cy.get('html').invoke('attr', 'data-theme').then((initialTheme) => {
        // 切換主題
        cy.get('[data-testid="theme-toggle-input"]').check({ force: true })

        // 主題應該立即更新
        cy.get('html').should('not.have.attr', 'data-theme', initialTheme)
      })
    })

    it('手機選單切換應該流暢', () => {
      cy.viewport(375, 667) // 手機尺寸

      // 測試選單開啟
      const startTime = Date.now()
      cy.get('[data-testid="mobile-menu-button"]').click()
      
      cy.get('[data-testid="mobile-menu"]')
        .should('be.visible')
        .then(() => {
          const endTime = Date.now()
          const toggleTime = endTime - startTime
          
          // 切換應該在 500ms 內完成
          expect(toggleTime).to.be.lessThan(500)
        })
    })
  })

  describe('大量數據性能', () => {
    it('應該能處理大量訂閱數據', () => {
      // 模擬登入
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
        
        // 添加大量訂閱數據
        const largeDataset = []
        for (let i = 1; i <= 50; i++) {
          largeDataset.push({
            id: i,
            name: `Service ${i}`,
            price: Math.floor(Math.random() * 500) + 100,
            cycle: 'monthly',
            category: 'streaming',
            startDate: '2024-01-01'
          })
        }
        
        const startTime = Date.now()
        
        // 一次性設置大量數據
        win.Alpine.store('app').setSubscriptions(largeDataset)
        
        const endTime = Date.now()
        const processTime = endTime - startTime
        
        // 處理 50 個項目應該在 1 秒內完成
        expect(processTime).to.be.lessThan(1000)
      })

      // 檢查渲染性能
      cy.get('[data-testid="subscription-card"]').should('have.length', 50)
      
      // 滾動性能應該良好
      cy.scrollTo('bottom', { duration: 500 })
      cy.scrollTo('top', { duration: 500 })
    })

    it('分類統計計算應該快速', () => {
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
        
        // 添加多種分類的訂閱
        const mixedDataset = []
        const categories = ['streaming', 'software', 'music', 'gaming', 'education']
        
        for (let i = 1; i <= 30; i++) {
          mixedDataset.push({
            id: i,
            name: `Service ${i}`,
            price: Math.floor(Math.random() * 300) + 50,
            cycle: 'monthly',
            category: categories[i % categories.length],
            startDate: '2024-01-01'
          })
        }
        
        win.Alpine.store('app').setSubscriptions(mixedDataset)
      })

      // 分類統計圖表應該顯示
      cy.get('[data-testid="category-stats"]').should('be.visible')
      
      // 所有分類都應該渲染
      cy.get('[data-testid="category-stat-item"]').should('have.length.at.least', 5)
    })
  })

  describe('記憶體使用', () => {
    it('不應該有明顯的記憶體洩漏', () => {
      // 模擬重複操作來檢查記憶體洩漏
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
        
        const initialMemory = win.performance.memory?.usedJSHeapSize || 0
        
        // 重複添加和刪除訂閱
        for (let i = 0; i < 10; i++) {
          const subscription = {
            id: `temp-${i}`,
            name: `Temp Service ${i}`,
            price: 100,
            cycle: 'monthly'
          }
          
          win.Alpine.store('app').addSubscription(subscription)
          win.Alpine.store('app').removeSubscription(`temp-${i}`)
        }
        
        // 觸發垃圾回收（如果可用）
        if (win.gc) {
          win.gc()
        }
        
        const finalMemory = win.performance.memory?.usedJSHeapSize || 0
        
        // 記憶體增長應該在合理範圍內（2MB）
        if (initialMemory > 0 && finalMemory > 0) {
          const memoryGrowth = finalMemory - initialMemory
          expect(memoryGrowth).to.be.lessThan(2 * 1024 * 1024) // 2MB
        }
      })
    })
  })

  describe('網路性能模擬', () => {
    it('慢速網路下應該有適當的 loading 狀態', () => {
      // 模擬慢速網路
      cy.intercept('**/api/**', (req) => {
        req.reply((res) => {
          // 延遲 2 秒響應
          return new Promise((resolve) => {
            setTimeout(() => resolve(res), 2000)
          })
        })
      })

      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
      })

      // 執行需要網路請求的操作
      cy.addSubscription({
        name: 'Network Test Service',
        price: '199'
      })

      // 應該顯示 loading 狀態
      cy.get('[data-testid="loading-indicator"]').should('be.visible')
      
      // loading 完成後應該隱藏
      cy.get('[data-testid="loading-indicator"]', { timeout: 5000 }).should('not.exist')
    })
  })

  describe('響應式性能', () => {
    it('視窗大小變化應該快速響應', () => {
      const sizes = [
        [375, 667],   // 手機
        [768, 1024],  // 平板  
        [1280, 720],  // 桌面
        [1920, 1080]  // 大桌面
      ]

      sizes.forEach(([width, height]) => {
        const startTime = Date.now()
        
        cy.viewport(width, height)
        
        // 檢查關鍵元素是否正確顯示
        cy.get('[data-testid="site-title"]').should('be.visible')
        
        cy.then(() => {
          const endTime = Date.now()
          const resizeTime = endTime - startTime
          
          // 響應式調整應該在 300ms 內完成
          expect(resizeTime).to.be.lessThan(300)
        })
      })
    })
  })

  describe('動畫性能', () => {
    it('月度總計動畫應該流暢', () => {
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
      })

      // 添加訂閱觸發動畫
      cy.addSubscription({
        name: 'Animation Test',
        price: '500'
      })

      // 動畫過程中數字應該逐漸變化
      cy.get('[data-testid="monthly-total"]').should('contain', '500')
    })

    it('頁面過渡動畫不應該影響性能', () => {
      cy.viewport(375, 667) // 手機尺寸

      const startTime = Date.now()

      // 開啟手機選單（有過渡動畫）
      cy.get('[data-testid="mobile-menu-button"]').click()
      cy.get('[data-testid="mobile-menu"]').should('be.visible')

      // 關閉手機選單
      cy.get('[data-testid="mobile-menu-button"]').click()
      cy.get('[data-testid="mobile-menu"]').should('not.be.visible')

      cy.then(() => {
        const endTime = Date.now()
        const animationTime = endTime - startTime
        
        // 完整的開啟-關閉動畫應該在 1 秒內完成
        expect(animationTime).to.be.lessThan(1000)
      })
    })
  })
})