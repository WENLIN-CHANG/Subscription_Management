// 狀態管理器測試
import { stateManager } from '../../scripts/ui/stateManager.js';

describe('StateManager', () => {
  beforeEach(() => {
    // 清理 DOM
    document.body.innerHTML = '';
    
    // 初始化 stateManager
    stateManager.init();
  });

  describe('Loading 狀態管理', () => {
    test('應該設置和獲取 loading 狀態', () => {
      stateManager.loading.set('test', true);
      expect(stateManager.loading.get('test')).toBe(true);
      
      stateManager.loading.set('test', false);
      expect(stateManager.loading.get('test')).toBe(false);
    });
    
    test('應該更新 UI 元素的 loading 狀態', () => {
      // 創建測試元素
      const button = document.createElement('button');
      button.setAttribute('data-loading', 'test');
      document.body.appendChild(button);
      
      stateManager.loading.set('test', true);
      expect(button.classList.contains('loading')).toBe(true);
      expect(button.disabled).toBe(true);
      
      stateManager.loading.set('test', false);
      expect(button.classList.contains('loading')).toBe(false);
      expect(button.disabled).toBe(false);
    });
    
    test('應該顯示全局 loading 覆蓋層', () => {
      stateManager.loading.set('test', true, { 
        showOverlay: true, 
        message: '測試載入中...' 
      });
      
      const overlay = document.getElementById('global-loading-overlay');
      expect(overlay).toBeTruthy();
      expect(overlay.textContent).toContain('測試載入中...');
    });
  });

  describe('錯誤處理', () => {
    test('應該設置和顯示錯誤', () => {
      const testError = new Error('測試錯誤');
      stateManager.error.set(testError, '測試上下文');
      
      expect(stateManager.error.current.message).toBe('測試錯誤');
      expect(stateManager.error.current.context).toBe('測試上下文');
      
      const errorAlert = document.getElementById('error-alert');
      expect(errorAlert).toBeTruthy();
      expect(errorAlert.textContent).toContain('測試錯誤');
    });
    
    test('應該處理不同嚴重級別的錯誤', () => {
      const criticalError = { 
        message: '嚴重錯誤', 
        response: { status: 500, statusText: 'Internal Server Error' }
      };
      
      stateManager.error.set(criticalError, '系統');
      
      expect(stateManager.error.current.severity).toBe('critical');
      expect(stateManager.error.current.type).toBe('HTTPError');
    });
    
    test('應該記錄錯誤歷史', () => {
      stateManager.error.set('錯誤1', '上下文1');
      stateManager.error.set('錯誤2', '上下文2');
      
      const history = stateManager.error.getHistory();
      expect(history).toHaveLength(2);
      expect(history[0].message).toBe('錯誤1');
      expect(history[1].message).toBe('錯誤2');
    });
    
    test('應該清除錯誤', () => {
      stateManager.error.set('測試錯誤', '測試');
      stateManager.error.clear();
      
      expect(stateManager.error.current).toBe(null);
      
      const errorAlert = document.getElementById('error-alert');
      expect(errorAlert).toBeFalsy();
    });
  });

  describe('成功通知', () => {
    test('應該顯示成功訊息', () => {
      stateManager.success.show('操作成功', '測試');
      
      const successAlert = document.getElementById('success-alert');
      expect(successAlert).toBeTruthy();
      expect(successAlert.textContent).toContain('操作成功');
    });
    
    test('應該自動隱藏成功訊息', (done) => {
      stateManager.success.show('操作成功', '測試');
      
      setTimeout(() => {
        const successAlert = document.getElementById('success-alert');
        expect(successAlert).toBeFalsy();
        done();
      }, 2100); // 稍微超過自動隱藏時間
    });
  });

  describe('withLoading 包裝器', () => {
    test('應該包裝異步操作', async () => {
      const mockFn = jest.fn().mockResolvedValue('結果');
      
      const result = await stateManager.withLoading('test', mockFn);
      
      expect(result).toBe('結果');
      expect(mockFn).toHaveBeenCalled();
    });
    
    test('應該處理異步操作錯誤', async () => {
      const mockError = new Error('異步錯誤');
      const mockFn = jest.fn().mockRejectedValue(mockError);
      
      await expect(stateManager.withLoading('test', mockFn)).rejects.toThrow('異步錯誤');
      
      expect(stateManager.error.current.message).toBe('異步錯誤');
    });
    
    test('應該顯示成功訊息', async () => {
      const mockFn = jest.fn().mockResolvedValue('結果');
      
      await stateManager.withLoading('test', mockFn, {
        successMessage: '操作完成',
        successContext: '測試'
      });
      
      const successAlert = document.getElementById('success-alert');
      expect(successAlert).toBeTruthy();
      expect(successAlert.textContent).toContain('操作完成');
    });
  });
});