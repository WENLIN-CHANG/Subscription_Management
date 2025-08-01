// 訂閱 CRUD 操作 E2E 測試
describe('訂閱 CRUD 操作', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForAlpine()
  })

  describe('未登入狀態', () => {
    it('應該顯示範例資料提示', () => {
      cy.get('[data-testid="sample-data-alert"]').should('be.visible')
      cy.get('[data-testid="sample-data-alert"]').should('contain', '體驗訂閱管理功能')
      cy.get('[data-testid="sample-data-alert"]').should('contain', '登入後，您可以建立專屬的訂閱記錄')
    })

    it('應該顯示範例訂閱服務', () => {
      cy.get('[data-testid="subscription-card"]').should('have.length.at.least', 1)
      cy.get('[data-testid="subscription-card"]').first().should('contain', 'Netflix')
    })

    it('點擊新增訂閱時應該提示登入', () => {
      cy.get('[data-testid="add-subscription-form"]').should('not.exist')
    })
  })

  describe('登入狀態下的 CRUD 操作', () => {
    beforeEach(() => {
      // 模擬登入
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
      })
    })

    it('應該顯示新增訂閱表單', () => {
      cy.get('[data-testid="add-subscription-form"]').should('be.visible')
      cy.get('[data-testid="service-name-input"]').should('be.visible')
      cy.get('[data-testid="price-input"]').should('be.visible')
      cy.get('[data-testid="currency-select"]').should('be.visible')
      cy.get('[data-testid="cycle-select"]').should('be.visible')
      cy.get('[data-testid="category-select"]').should('be.visible')
      cy.get('[data-testid="start-date-input"]').should('be.visible')
    })

    it('應該能成功新增訂閱', () => {
      const subscription = {
        name: 'Cypress Test Service',
        price: '299',
        currency: 'TWD',
        cycle: 'monthly',
        category: 'software',
        startDate: '2024-01-01'
      }

      // 填寫表單
      cy.get('[data-testid="service-name-input"]').type(subscription.name)
      cy.get('[data-testid="price-input"]').type(subscription.price)
      cy.get('[data-testid="currency-select"]').select(subscription.currency)
      cy.get('[data-testid="cycle-select"]').select(subscription.cycle)
      cy.get('[data-testid="category-select"]').select(subscription.category)
      cy.get('[data-testid="start-date-input"]').type(subscription.startDate)

      // 提交表單
      cy.get('[data-testid="add-subscription-button"]').click()

      // 驗證結果
      cy.get('[data-testid="subscription-card"]').should('contain', 'Cypress Test Service')
      cy.get('[data-testid="subscription-card"]').should('contain', 'NT$299')
      cy.get('[data-testid="success-message"]').should('contain', '新增訂閱「Cypress Test Service」成功')
      
      // 表單應該被重置
      cy.get('[data-testid="service-name-input"]').should('have.value', '')
    })

    it('表單驗證應該正常工作', () => {
      // 空表單提交應該顯示錯誤
      cy.get('[data-testid="add-subscription-button"]').click()
      cy.get('[data-testid="service-name-input"]:invalid').should('exist')

      // 填寫服務名稱但不填價格
      cy.get('[data-testid="service-name-input"]').type('Test Service')
      cy.get('[data-testid="add-subscription-button"]').click()
      cy.get('[data-testid="price-input"]:invalid').should('exist')

      // 填寫負數價格
      cy.get('[data-testid="price-input"]').type('-100')
      cy.get('[data-testid="category-select"]').select('streaming')
      cy.get('[data-testid="start-date-input"]').type('2024-01-01')
      cy.get('[data-testid="add-subscription-button"]').click()
      cy.get('[data-testid="error-message"]').should('contain', '請輸入有效的價格')
    })

    it('應該能編輯現有訂閱', () => {
      // 先添加一個訂閱
      cy.addSubscription({
        name: 'Original Service',
        price: '199',
        category: 'streaming'
      })

      // 點擊編輯按鈕
      cy.get('[data-testid="subscription-card"]')
        .contains('Original Service')
        .parents('[data-testid="subscription-card"]')
        .find('[data-testid="edit-button"]')
        .click()

      // 驗證表單被填充
      cy.get('[data-testid="service-name-input"]').should('have.value', 'Original Service')
      cy.get('[data-testid="price-input"]').should('have.value', '199')

      // 修改服務名稱和價格
      cy.get('[data-testid="service-name-input"]').clear().type('Updated Service')
      cy.get('[data-testid="price-input"]').clear().type('299')

      // 提交更新
      cy.get('[data-testid="update-subscription-button"]').click()

      // 驗證更新結果
      cy.get('[data-testid="subscription-card"]').should('contain', 'Updated Service')
      cy.get('[data-testid="subscription-card"]').should('contain', 'NT$299')
      cy.get('[data-testid="success-message"]').should('contain', '更新訂閱「Updated Service」成功')
    })

    it('應該能取消編輯', () => {
      // 先添加一個訂閱
      cy.addSubscription({
        name: 'Test Service',
        price: '199'
      })

      // 開始編輯
      cy.get('[data-testid="edit-button"]').click()
      
      // 修改表單
      cy.get('[data-testid="service-name-input"]').clear().type('Modified Name')
      
      // 取消編輯
      cy.get('[data-testid="cancel-edit-button"]').click()
      
      // 表單應該被重置
      cy.get('[data-testid="service-name-input"]').should('have.value', '')
      
      // 原始服務名稱應該保持不變
      cy.get('[data-testid="subscription-card"]').should('contain', 'Test Service')
    })

    it('應該能刪除訂閱', () => {
      // 先添加一個訂閱
      cy.addSubscription({
        name: 'Service to Delete',
        price: '99'
      })

      // 確認訂閱存在
      cy.get('[data-testid="subscription-card"]').should('contain', 'Service to Delete')

      // 模擬確認對話框
      cy.window().then((win) => {
        cy.stub(win, 'confirm').returns(true)
      })

      // 點擊刪除按鈕
      cy.get('[data-testid="subscription-card"]')
        .contains('Service to Delete')
        .parents('[data-testid="subscription-card"]')
        .find('[data-testid="delete-button"]')
        .click()

      // 驗證刪除結果
      cy.get('[data-testid="subscription-card"]').should('not.contain', 'Service to Delete')
      cy.get('[data-testid="success-message"]').should('contain', '刪除訂閱「Service to Delete」成功')
    })

    it('取消刪除確認時不應該刪除訂閱', () => {
      // 先添加一個訂閱
      cy.addSubscription({
        name: 'Service to Keep',
        price: '99'
      })

      // 模擬取消確認對話框
      cy.window().then((win) => {
        cy.stub(win, 'confirm').returns(false)
      })

      // 點擊刪除按鈕
      cy.get('[data-testid="delete-button"]').click()

      // 訂閱應該還在
      cy.get('[data-testid="subscription-card"]').should('contain', 'Service to Keep')
    })
  })

  describe('月度總計更新', () => {
    beforeEach(() => {
      cy.window().then((win) => {
        win.Alpine.store('app').setAuth(true, { id: 1, username: 'testuser' })
      })
    })

    it('新增訂閱時應該更新月度總計', () => {
      // 記錄初始總計
      cy.get('[data-testid="monthly-total"]').invoke('text').as('initialTotal')

      // 添加訂閱
      cy.addSubscription({
        name: 'Test Service',
        price: '300',
        cycle: 'monthly'
      })

      // 驗證月度總計已更新
      cy.get('[data-testid="monthly-total"]').should('contain', '300')
    })

    it('刪除訂閱時應該更新月度總計', () => {
      // 先添加兩個訂閱
      cy.addSubscription({
        name: 'Service 1',
        price: '200'
      })
      cy.addSubscription({
        name: 'Service 2',
        price: '300'
      })

      // 確認總計
      cy.get('[data-testid="monthly-total"]').should('contain', '500')

      // 刪除一個訂閱
      cy.window().then((win) => {
        cy.stub(win, 'confirm').returns(true)
      })
      
      cy.get('[data-testid="subscription-card"]')
        .contains('Service 1')
        .parents('[data-testid="subscription-card"]')
        .find('[data-testid="delete-button"]')
        .click()

      // 驗證總計更新
      cy.get('[data-testid="monthly-total"]').should('contain', '300')
    })
  })
})