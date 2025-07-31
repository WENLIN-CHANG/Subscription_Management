import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    // 測試環境
    environment: 'jsdom',
    
    // 測試文件模式匹配
    include: [
      'frontend/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'tests/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'
    ],
    
    // 全局測試設置
    globals: true,
    
    // 覆蓋率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'backend/',
        'frontend/scripts/data/sampleData.js',
        '**/*.config.js',
        '**/*.d.ts'
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        }
      }
    },
    
    // 測試超時時間
    testTimeout: 10000,
    
    // 設置檔案
    setupFiles: ['./tests/setup.js']
  },
  
  // Vite 配置
  resolve: {
    alias: {
      '@': '/frontend'
    }
  }
})