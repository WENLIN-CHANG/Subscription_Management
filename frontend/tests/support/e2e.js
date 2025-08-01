// Cypress E2E 測試支援文件
import './commands'

// 全域配置
Cypress.on('uncaught:exception', (err, runnable) => {
  // 防止某些不重要的錯誤導致測試失敗
  return false
})

// 在每個測試前清理
beforeEach(() => {
  // 清除 localStorage
  cy.clearLocalStorage()
  
  // 清除 cookies
  cy.clearCookies()
  
  // 設定視窗大小
  cy.viewport(1280, 720)
})