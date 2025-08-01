// 預算管理功能測試
describe('預算管理功能', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForAlpine()
    
    // 模擬登入
    cy.window().then((win) => {
      win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
    })
  })

  describe('預算設定', () => {
    it('未設定預算時應該顯示設定按鈕', () => {
      // 初始狀態應該沒有預算
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(0)
      })

      // 應該顯示設定預算按鈕
      cy.get('[data-testid="set-budget-button"]').should('be.visible')
      cy.get('[data-testid="set-budget-button"]').should('contain', '設定月度預算')
      
      // 不應該顯示預算卡片
      cy.get('[data-testid="budget-card"]').should('not.exist')
    })

    it('應該能開啟預算設定彈窗', () => {
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(0)
      })

      // 點擊設定預算按鈕
      cy.get('[data-testid="set-budget-button"]').click()

      // 預算設定彈窗應該顯示
      cy.get('[data-testid="budget-modal"]').should('be.visible')
      cy.get('[data-testid="budget-input"]').should('be.visible')
      cy.get('[data-testid="save-budget-button"]').should('be.visible')
      cy.get('[data-testid="cancel-budget-button"]').should('be.visible')
    })

    it('應該能設定新預算', () => {
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(0)
      })

      // 開啟設定彈窗
      cy.get('[data-testid="set-budget-button"]').click()

      // 輸入預算金額
      cy.get('[data-testid="budget-input"]').type('3000')

      // 保存預算
      cy.get('[data-testid="save-budget-button"]').click()

      // 預算卡片應該顯示
      cy.get('[data-testid="budget-card"]').should('be.visible')
      cy.get('[data-testid="budget-amount"]').should('contain', 'NT$3,000')
      
      // 彈窗應該關閉
      cy.get('[data-testid="budget-modal"]').should('not.be.visible')
      
      // 成功訊息應該顯示
      cy.get('[data-testid="success-message"]').should('contain', '預算設定成功')
    })

    it('應該能調整現有預算', () => {
      // 先設定預算
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(2000)
      })

      // 點擊調整按鈕
      cy.get('[data-testid="adjust-budget-button"]').click()

      // 輸入欄位應該顯示當前預算
      cy.get('[data-testid="budget-input"]').should('have.value', '2000')

      // 修改預算
      cy.get('[data-testid="budget-input"]').clear().type('4000')
      cy.get('[data-testid="save-budget-button"]').click()

      // 預算應該更新
      cy.get('[data-testid="budget-amount"]').should('contain', 'NT$4,000')
    })

    it('應該能取消預算設定', () => {
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(0)
      })

      // 開啟設定彈窗
      cy.get('[data-testid="set-budget-button"]').click()
      
      // 輸入預算
      cy.get('[data-testid="budget-input"]').type('5000')
      
      // 取消設定
      cy.get('[data-testid="cancel-budget-button"]').click()

      // 彈窗應該關閉
      cy.get('[data-testid="budget-modal"]').should('not.be.visible')
      
      // 預算卡片不應該顯示
      cy.get('[data-testid="budget-card"]').should('not.exist')
    })

    it('預算驗證應該正常工作', () => {
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(0)
      })

      cy.get('[data-testid="set-budget-button"]').click()

      // 測試空值
      cy.get('[data-testid="save-budget-button"]').click()
      cy.get('[data-testid="budget-input"]:invalid').should('exist')

      // 測試負值
      cy.get('[data-testid="budget-input"]').type('-100')
      cy.get('[data-testid="save-budget-button"]').click()
      cy.get('[data-testid="error-message"]').should('contain', '預算金額必須大於 0')

      // 測試非數字
      cy.get('[data-testid="budget-input"]').clear().type('abc')
      cy.get('[data-testid="save-budget-button"]').click()
      cy.get('[data-testid="budget-input"]:invalid').should('exist')
    })
  })

  describe('預算狀態顯示', () => {
    beforeEach(() => {
      // 設定預算為 1000
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(1000)
      })
    })

    it('正常預算狀態顯示', () => {
      // 添加少量訂閱（50% 使用率）
      cy.addSubscription({
        name: 'Test Service',
        price: '500',
        cycle: 'monthly'
      })

      // 預算狀態應該是正常
      cy.get('[data-testid="budget-status"]').should('contain', '正常')
      cy.get('[data-testid="budget-status"]').should('have.class', 'badge-success')
      
      // 進度條應該是綠色
      cy.get('[data-testid="budget-progress"]').should('have.class', 'progress-success')
      
      // 使用百分比應該顯示
      cy.get('[data-testid="budget-usage"]').should('contain', '50.0%')
      
      // 剩餘預算應該顯示
      cy.get('[data-testid="remaining-budget"]').should('contain', 'NT$500')
    })

    it('預算警告狀態顯示', () => {
      // 添加訂閱達到 80% 使用率
      cy.addSubscription({
        name: 'Service 1',
        price: '400'
      })
      cy.addSubscription({
        name: 'Service 2',
        price: '400'
      })

      // 預算狀態應該是警告
      cy.get('[data-testid="budget-status"]').should('contain', '接近上限')
      cy.get('[data-testid="budget-status"]').should('have.class', 'badge-warning')
      
      // 進度條應該是橙色
      cy.get('[data-testid="budget-progress"]').should('have.class', 'progress-warning')
      
      // 使用百分比應該顯示
      cy.get('[data-testid="budget-usage"]').should('contain', '80.0%')
    })

    it('預算超支狀態顯示', () => {
      // 添加訂閱超過預算
      cy.addSubscription({
        name: 'Expensive Service',
        price: '1200'
      })

      // 預算狀態應該是超支
      cy.get('[data-testid="budget-status"]').should('contain', '預算超支')
      cy.get('[data-testid="budget-status"]').should('have.class', 'badge-error')
      
      // 進度條應該是紅色
      cy.get('[data-testid="budget-progress"]').should('have.class', 'progress-error')
      
      // 應該顯示超支金額而不是剩餘金額
      cy.get('[data-testid="over-budget"]').should('contain', 'NT$200')
      cy.get('[data-testid="remaining-budget"]').should('not.exist')
    })
  })

  describe('預算與訂閱互動', () => {
    beforeEach(() => {
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(1000)
      })
    })

    it('新增訂閱應該更新預算狀態', () => {
      // 初始狀態
      cy.get('[data-testid="budget-usage"]').should('contain', '0.0%')

      // 添加訂閱
      cy.addSubscription({
        name: 'New Service',
        price: '300'
      })

      // 預算使用率應該更新
      cy.get('[data-testid="budget-usage"]').should('contain', '30.0%')
      cy.get('[data-testid="remaining-budget"]').should('contain', 'NT$700')
    })

    it('編輯訂閱應該更新預算狀態', () => {
      // 先添加訂閱
      cy.addSubscription({
        name: 'Test Service',
        price: '300'
      })

      // 確認初始狀態
      cy.get('[data-testid="budget-usage"]').should('contain', '30.0%')

      // 編輯訂閱價格
      cy.get('[data-testid="edit-button"]').click()
      cy.get('[data-testid="price-input"]').clear().type('600')
      cy.get('[data-testid="update-subscription-button"]').click()

      // 預算使用率應該更新
      cy.get('[data-testid="budget-usage"]').should('contain', '60.0%')
      cy.get('[data-testid="remaining-budget"]').should('contain', 'NT$400')
    })

    it('刪除訂閱應該更新預算狀態', () => {
      // 添加兩個訂閱
      cy.addSubscription({
        name: 'Service 1',
        price: '400'
      })
      cy.addSubscription({
        name: 'Service 2',
        price: '300'
      })

      // 確認總使用率
      cy.get('[data-testid="budget-usage"]').should('contain', '70.0%')

      // 刪除一個訂閱
      cy.window().then((win) => {
        cy.stub(win, 'confirm').returns(true)
      })
      
      cy.get('[data-testid="subscription-card"]')
        .contains('Service 1')
        .parents('[data-testid="subscription-card"]')
        .find('[data-testid="delete-button"]')
        .click()

      // 預算使用率應該更新
      cy.get('[data-testid="budget-usage"]').should('contain', '30.0%')
      cy.get('[data-testid="remaining-budget"]').should('contain', 'NT$700')
    })
  })

  describe('年度預估支出', () => {
    it('應該正確計算和顯示年度預估支出', () => {
      // 添加月費訂閱
      cy.addSubscription({
        name: 'Monthly Service',
        price: '300',
        cycle: 'monthly'
      })

      // 年度預估應該是 300 * 12 = 3600
      cy.get('[data-testid="yearly-estimate"]').should('contain', 'NT$3,600')

      // 添加年費訂閱
      cy.addSubscription({
        name: 'Yearly Service',
        price: '1200',
        cycle: 'yearly'
      })

      // 年度預估應該更新：(300 + 100) * 12 = 4800
      cy.get('[data-testid="yearly-estimate"]').should('contain', 'NT$4,800')
    })
  })

  describe('未登入用戶的預算功能', () => {
    beforeEach(() => {
      // 登出
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(false, null)
      })
    })

    it('未登入用戶不能設定預算', () => {
      // 預算設定按鈕應該有鎖定提示
      cy.get('[data-testid="set-budget-button"]').should('contain', '🔒')
      cy.get('[data-testid="set-budget-button"]').should('have.attr', 'title')
        .and('contain', '請先登入')

      // 點擊應該提示登入
      cy.get('[data-testid="set-budget-button"]').click()
      cy.get('[data-testid="login-modal"]').should('be.visible')
    })

    it('未登入用戶不能調整預算', () => {
      // 模擬有預算但未登入的狀態
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(1000)
      })

      // 調整按鈕應該有鎖定提示
      cy.get('[data-testid="adjust-budget-button"]').should('contain', '🔒')
      
      // 點擊應該提示登入
      cy.get('[data-testid="adjust-budget-button"]').click()
      cy.get('[data-testid="login-modal"]').should('be.visible')
    })
  })

  describe('預算設定的鍵盤操作', () => {
    it('Enter 鍵應該能提交預算設定', () => {
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(0)
      })

      // 開啟設定彈窗
      cy.get('[data-testid="set-budget-button"]').click()

      // 輸入預算並按 Enter
      cy.get('[data-testid="budget-input"]').type('2500{enter}')

      // 預算應該被保存
      cy.get('[data-testid="budget-amount"]').should('contain', 'NT$2,500')
      cy.get('[data-testid="budget-modal"]').should('not.be.visible')
    })

    it('Escape 鍵應該能關閉預算設定彈窗', () => {
      cy.window().then((win) => {
        win.Alpine.store('app').setBudget(0)
      })

      // 開啟設定彈窗
      cy.get('[data-testid="set-budget-button"]').click()

      // 按 Escape 鍵
      cy.get('[data-testid="budget-input"]').type('{esc}')

      // 彈窗應該關閉
      cy.get('[data-testid="budget-modal"]').should('not.be.visible')
    })
  })
})