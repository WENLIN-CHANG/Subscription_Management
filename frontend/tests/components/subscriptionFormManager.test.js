// 訂閱表單管理器測試
import { subscriptionFormManager } from '../../scripts/components/subscriptionFormManager.js';

describe('SubscriptionFormManager', () => {
  let formManager;
  
  beforeEach(() => {
    // 模擬 Alpine store
    window.Alpine = {
      store: jest.fn(() => ({
        app: {
          isLoggedIn: true,
          isEditing: false,
          editingSubscription: null
        }
      }))
    };
    
    // 模擬 stateManager
    window.stateManager = {
      error: {
        set: jest.fn(),
        clear: jest.fn()
      }
    };
    
    // 模擬 dataManager
    window.dataManager = {
      isSampleDataMode: jest.fn(() => false),
      getSampleDataInfo: jest.fn(() => ({ totalServices: 0 }))
    };
    
    formManager = subscriptionFormManager();
  });
  
  afterEach(() => {
    delete window.Alpine;
    delete window.stateManager;
    delete window.dataManager;
  });

  describe('表單驗證', () => {
    test('應該驗證必填字段', () => {
      formManager.newSubscription = {
        name: '',
        originalPrice: '',
        currency: 'TWD',
        cycle: 'monthly',
        category: '',
        startDate: ''
      };
      
      expect(() => formManager.validateForm()).toThrow();
    });
    
    test('應該驗證服務名稱長度', () => {
      formManager.newSubscription = {
        name: 'A', // 太短
        originalPrice: '100',
        currency: 'TWD',
        cycle: 'monthly',
        category: 'streaming',
        startDate: '2024-01-01'
      };
      
      expect(() => formManager.validateForm()).toThrow('服務名稱至少需要 2 個字符');
    });
    
    test('應該驗證價格範圍', () => {
      formManager.newSubscription = {
        name: 'Netflix',
        originalPrice: '-10', // 負數
        currency: 'TWD',
        cycle: 'monthly',
        category: 'streaming',
        startDate: '2024-01-01'
      };
      
      expect(() => formManager.validateForm()).toThrow('價格必須大於 0');
    });
    
    test('應該驗證日期範圍', () => {
      const twoYearsAgo = new Date();
      twoYearsAgo.setFullYear(twoYearsAgo.getFullYear() - 2);
      
      formManager.newSubscription = {
        name: 'Netflix',
        originalPrice: '100',
        currency: 'TWD',
        cycle: 'monthly',
        category: 'streaming',
        startDate: twoYearsAgo.toISOString().split('T')[0]
      };
      
      expect(() => formManager.validateForm()).toThrow('開始日期不能超過一年前');
    });
    
    test('應該通過有效數據驗證', () => {
      formManager.newSubscription = {
        name: 'Netflix',
        originalPrice: '390',
        currency: 'TWD',
        cycle: 'monthly',
        category: 'streaming',
        startDate: '2024-01-01'
      };
      
      expect(() => formManager.validateForm()).not.toThrow();
    });
  });

  describe('表單操作', () => {
    test('應該重置表單', () => {
      formManager.newSubscription.name = 'Test';
      formManager.resetForm();
      
      expect(formManager.newSubscription.name).toBe('');
      expect(formManager.newSubscription.currency).toBe('TWD');
      expect(formManager.newSubscription.cycle).toBe('monthly');
    });
    
    test('應該清除驗證錯誤', () => {
      formManager.validationErrors = { name: 'error' };
      formManager.clearValidationErrors();
      
      expect(formManager.validationErrors).toEqual({});
    });
  });

  describe('數據持久化', () => {
    test('應該保存表單數據以便恢復', () => {
      formManager.newSubscription = {
        name: 'Netflix',
        originalPrice: '390'
      };
      
      formManager.saveFormDataForRestore();
      
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'restoreSubscriptionForm',
        JSON.stringify(formManager.newSubscription)
      );
    });
    
    test('空表單不應該保存', () => {
      formManager.newSubscription = {
        name: '',
        originalPrice: ''
      };
      
      formManager.saveFormDataForRestore();
      
      expect(localStorage.setItem).not.toHaveBeenCalled();
    });
  });
});