import { describe, it, expect, beforeEach, vi } from 'vitest'
import { stateManager } from '../../frontend/scripts/ui/stateManager.js'

describe('stateManager', () => {
  beforeEach(() => {
    // 清理狀態
    stateManager.loading.states.clear()
    stateManager.error.current = null
    stateManager.success.current = null
    
    // 清理 DOM
    document.body.innerHTML = ''
  })

  describe('loading', () => {
    it('應該正確設置和獲取載入狀態', () => {
      stateManager.loading.set('test', true)
      expect(stateManager.loading.get('test')).toBe(true)
      
      stateManager.loading.set('test', false)
      expect(stateManager.loading.get('test')).toBe(false)
    })

    it('應該正確更新 UI 載入狀態', () => {
      // 創建測試元素
      const button = document.createElement('button')
      button.setAttribute('data-loading', 'test')
      document.body.appendChild(button)

      stateManager.loading.set('test', true)
      
      expect(button.classList.contains('loading')).toBe(true)
      expect(button.disabled).toBe(true)
      
      stateManager.loading.set('test', false)
      
      expect(button.classList.contains('loading')).toBe(false)
      expect(button.disabled).toBe(false)
    })

    it('應該正確更新載入指示器', () => {
      const indicator = document.createElement('div')
      indicator.setAttribute('data-loading-indicator', 'test')
      document.body.appendChild(indicator)

      stateManager.loading.set('test', true)
      expect(indicator.style.display).toBe('block')
      
      stateManager.loading.set('test', false)
      expect(indicator.style.display).toBe('none')
    })
  })

  describe('error', () => {
    it('應該正確設置錯誤訊息', () => {
      stateManager.error.set('測試錯誤', '測試情境')
      expect(stateManager.error.current).toContain('測試錯誤')
      expect(stateManager.error.current).toContain('測試情境')
    })

    it('應該處理 Error 物件', () => {
      const error = new Error('JavaScript 錯誤')
      stateManager.error.set(error, 'API 呼叫')
      expect(stateManager.error.current).toContain('JavaScript 錯誤')
      expect(stateManager.error.current).toContain('API 呼叫')
    })

    it('應該處理物件錯誤', () => {
      const errorObj = { detail: '伺服器錯誤' }
      stateManager.error.set(errorObj, 'API 回應')
      expect(stateManager.error.current).toContain('伺服器錯誤')
    })

    it('應該更新錯誤 UI', () => {
      const errorDiv = document.createElement('div')
      errorDiv.id = 'error-message'
      errorDiv.style.display = 'none'
      document.body.appendChild(errorDiv)

      stateManager.error.set('測試錯誤')
      
      expect(errorDiv.style.display).toBe('block')
      expect(errorDiv.textContent).toContain('測試錯誤')
    })

    it('應該能清除錯誤', () => {
      const errorDiv = document.createElement('div')
      errorDiv.id = 'error-message'
      document.body.appendChild(errorDiv)

      stateManager.error.set('測試錯誤')
      expect(errorDiv.style.display).toBe('block')
      
      stateManager.error.clear()
      expect(stateManager.error.current).toBe(null)
      expect(errorDiv.style.display).toBe('none')
    })
  })

  describe('success', () => {
    it('應該正確設置成功訊息', () => {
      stateManager.success.set('操作成功', '測試情境')
      expect(stateManager.success.current).toContain('操作成功')
      expect(stateManager.success.current).toContain('測試情境')
    })

    it('應該更新成功 UI', () => {
      const successDiv = document.createElement('div')
      successDiv.id = 'success-message'
      successDiv.style.display = 'none'
      document.body.appendChild(successDiv)

      stateManager.success.set('測試成功')
      
      expect(successDiv.style.display).toBe('block')
      expect(successDiv.textContent).toContain('測試成功')
    })

    it('應該自動清除成功訊息', () => {
      vi.useFakeTimers()
      
      const successDiv = document.createElement('div')
      successDiv.id = 'success-message'
      document.body.appendChild(successDiv)

      stateManager.success.set('測試成功')
      expect(successDiv.style.display).toBe('block')
      
      // 快進時間
      vi.advanceTimersByTime(4000)
      
      expect(stateManager.success.current).toBe(null)
      expect(successDiv.style.display).toBe('none')
      
      vi.useRealTimers()
    })
  })

  describe('withLoading', () => {
    it('應該正確處理載入狀態', async () => {
      const mockFn = vi.fn().mockResolvedValue('成功')
      
      const result = await stateManager.withLoading('test', mockFn)
      
      expect(result).toBe('成功')
      expect(mockFn).toHaveBeenCalled()
    })

    it('應該處理錯誤情況', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('測試錯誤'))
      
      await expect(
        stateManager.withLoading('test', mockFn)
      ).rejects.toThrow('測試錯誤')
      
      expect(stateManager.error.current).toContain('測試錯誤')
    })

    it('應該顯示成功訊息', async () => {
      const mockFn = vi.fn().mockResolvedValue('成功')
      
      await stateManager.withLoading('test', mockFn, {
        successMessage: '操作完成',
        successContext: '測試'
      })
      
      expect(stateManager.success.current).toContain('操作完成')
      expect(stateManager.success.current).toContain('測試')
    })
  })
})