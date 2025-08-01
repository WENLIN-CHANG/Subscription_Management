// 自定義 Cypress 命令

// 模擬登入
Cypress.Commands.add('login', (username = 'testuser', password = 'testpass') => {
  // 這裡需要根據你的實際登入流程來實現
  cy.get('[data-testid="login-button"]').click()
  cy.get('[data-testid="username-input"]').type(username)
  cy.get('[data-testid="password-input"]').type(password)
  cy.get('[data-testid="login-submit"]').click()
  cy.wait(1000) // 等待登入完成
})

// 模擬登出
Cypress.Commands.add('logout', () => {
  cy.get('[data-testid="user-menu"]').click()
  cy.get('[data-testid="logout-button"]').click()
})

// 添加訂閱
Cypress.Commands.add('addSubscription', (subscription) => {
  const defaultSubscription = {
    name: 'Test Service',
    price: '100',
    currency: 'TWD',
    cycle: 'monthly',
    category: 'streaming',
    startDate: '2024-01-01'
  }
  
  const sub = { ...defaultSubscription, ...subscription }
  
  cy.get('[data-testid="service-name-input"]').clear().type(sub.name)
  cy.get('[data-testid="price-input"]').clear().type(sub.price)
  cy.get('[data-testid="currency-select"]').select(sub.currency)
  cy.get('[data-testid="cycle-select"]').select(sub.cycle)
  cy.get('[data-testid="category-select"]').select(sub.category)
  cy.get('[data-testid="start-date-input"]').clear().type(sub.startDate)
  cy.get('[data-testid="add-subscription-button"]').click()
})

// 等待 Alpine.js 初始化
Cypress.Commands.add('waitForAlpine', () => {
  cy.window().should('have.property', 'Alpine')
  cy.wait(500) // 給 Alpine.js 一些時間初始化
})

// 檢查響應式設計
Cypress.Commands.add('checkResponsive', (sizes = ['iphone-6', 'ipad-2', 'macbook-15']) => {
  sizes.forEach(size => {
    cy.viewport(size)
    cy.wait(500)
    // 這裡可以添加特定的響應式檢查
  })
})

// 檢查無障礙功能
Cypress.Commands.add('checkAccessibility', () => {
  // 檢查是否有適當的 alt 文字、標籤等
  cy.get('input').should('have.attr', 'aria-label').or('have.attr', 'placeholder')
  cy.get('button').should('be.visible').and('not.be.disabled')
})