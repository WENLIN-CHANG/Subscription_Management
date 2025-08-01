const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'e2e/**/*.cy.js',
    supportFile: 'support/e2e.js',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    setupNodeEvents(on, config) {
      // 節點事件監聽器
    }
  },
  component: {
    devServer: {
      framework: 'vanilla',
      bundler: 'webpack'
    },
    specPattern: 'component/**/*.cy.js'
  }
})