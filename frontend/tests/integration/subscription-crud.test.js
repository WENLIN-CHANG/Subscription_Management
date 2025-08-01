// 訂閱 CRUD 集成測試
import { subscriptionActions } from '../../scripts/business/subscriptionActions.js';

describe('訂閱 CRUD 集成測試', () => {
  let mockContext;
  let mockDataManager;
  let mockStateManager;
  let mockStore;

  beforeEach(() => {
    // 模擬 Alpine store
    mockStore = {
      subscriptions: [],
      setSubscriptions: jest.fn(),
      calculateMonthlyTotal: jest.fn()
    };

    window.Alpine = {
      store: jest.fn(() => mockStore)
    };

    // 模擬 dataManager
    mockDataManager = {
      isLoggedIn: jest.fn(() => true),
      loadSubscriptions: jest.fn(() => Promise.resolve([])),
      createSubscription: jest.fn(() => Promise.resolve({ id: '1', name: 'Test' })),
      updateSubscription: jest.fn(() => Promise.resolve()),
      deleteSubscription: jest.fn(() => Promise.resolve()),
      saveSubscriptions: jest.fn(() => Promise.resolve())
    };

    // 模擬 stateManager
    mockStateManager = {
      withLoading: jest.fn((key, fn) => fn()),
      error: {
        set: jest.fn()
      },
      success: {
        show: jest.fn()
      }
    };

    // 設置全局對象
    window.dataManager = mockDataManager;
    window.stateManager = mockStateManager;

    // 模擬上下文
    mockContext = {
      newSubscription: {
        name: 'Netflix',
        originalPrice: '390',
        currency: 'TWD',
        cycle: 'monthly',
        category: 'streaming',
        startDate: '2024-01-01'
      },
      subscriptions: [],
      calculateMonthlyTotal: jest.fn(),
      showLogin: jest.fn()
    };
  });

  afterEach(() => {
    delete window.Alpine;
    delete window.dataManager;
    delete window.stateManager;
  });

  describe('新增訂閱', () => {
    test('應該成功新增訂閱', async () => {
      mockDataManager.loadSubscriptions.mockResolvedValue([
        { id: '1', name: 'Netflix', price: 390 }
      ]);

      await subscriptionActions.addSubscription(mockContext);

      expect(mockDataManager.createSubscription).toHaveBeenCalledWith({
        name: 'Netflix',
        originalPrice: 390,
        currency: 'TWD',
        cycle: 'monthly',
        category: 'streaming',
        startDate: '2024-01-01'
      });

      expect(mockStore.setSubscriptions).toHaveBeenCalledWith([
        { id: '1', name: 'Netflix', price: 390 }
      ]);
    });

    test('未登入時應該提示登入', async () => {
      mockDataManager.isLoggedIn.mockReturnValue(false);

      await subscriptionActions.addSubscription(mockContext);

      expect(mockContext.showLogin).toHaveBeenCalled();
      expect(mockDataManager.createSubscription).not.toHaveBeenCalled();
    });

    test('驗證失敗時應該顯示錯誤', async () => {
      mockContext.newSubscription.name = ''; // 無效數據

      await subscriptionActions.addSubscription(mockContext);

      expect(mockStateManager.error.set).toHaveBeenCalled();
      expect(mockDataManager.createSubscription).not.toHaveBeenCalled();
    });
  });

  describe('刪除訂閱', () => {
    beforeEach(() => {
      mockStore.subscriptions = [
        { id: '1', name: 'Netflix', price: 390 }
      ];

      // 模擬 confirm 對話框
      global.confirm = jest.fn(() => true);
    });

    test('應該成功刪除訂閱', async () => {
      mockDataManager.loadSubscriptions.mockResolvedValue([]);

      await subscriptionActions.deleteSubscription(mockContext, '1');

      expect(mockDataManager.deleteSubscription).toHaveBeenCalledWith('1');
      expect(mockStore.setSubscriptions).toHaveBeenCalledWith([]);
    });

    test('取消確認時不應該刪除', async () => {
      global.confirm.mockReturnValue(false);

      await subscriptionActions.deleteSubscription(mockContext, '1');

      expect(mockDataManager.deleteSubscription).not.toHaveBeenCalled();
    });

    test('範例數據應該提示登入', async () => {
      mockDataManager.isLoggedIn.mockReturnValue(false);

      await subscriptionActions.deleteSubscription(mockContext, 'sample-1');

      expect(mockStateManager.success.show).toHaveBeenCalledWith(
        expect.stringContaining('範例資料'),
        '登入提示'
      );
    });
  });

  describe('編輯訂閱', () => {
    beforeEach(() => {
      mockStore.subscriptions = [
        { 
          id: '1', 
          name: 'Netflix', 
          price: 390,
          originalPrice: 390,
          currency: 'TWD',
          cycle: 'monthly',
          category: 'streaming',
          startDate: '2024-01-01'
        }
      ];
    });

    test('應該開始編輯訂閱', () => {
      // 模擬 DOM 查詢
      const mockForm = {
        scrollIntoView: jest.fn(),
        querySelector: jest.fn(() => ({
          focus: jest.fn()
        }))
      };
      global.document.querySelector = jest.fn(() => mockForm);

      subscriptionActions.editSubscription(mockContext, '1');

      expect(mockStore.startEditing).toHaveBeenCalledWith(mockStore.subscriptions[0]);
      expect(mockForm.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' });
    });

    test('範例數據應該提示登入', () => {
      mockDataManager.isLoggedIn.mockReturnValue(false);

      subscriptionActions.editSubscription(mockContext, 'sample-1');

      expect(mockStateManager.success.show).toHaveBeenCalledWith(
        expect.stringContaining('範例資料'),
        '登入提示'
      );
    });
  });

  describe('更新訂閱', () => {
    beforeEach(() => {
      mockContext.editingSubscription = { id: '1', name: 'Netflix' };
      mockStore.editingSubscription = { id: '1', name: 'Netflix' };
    });

    test('應該成功更新訂閱', async () => {
      mockDataManager.loadSubscriptions.mockResolvedValue([
        { id: '1', name: 'Netflix Updated', price: 450 }
      ]);

      await subscriptionActions.updateSubscription(mockContext);

      expect(mockDataManager.updateSubscription).toHaveBeenCalled();
      expect(mockStore.setSubscriptions).toHaveBeenCalledWith([
        { id: '1', name: 'Netflix Updated', price: 450 }
      ]);
      expect(mockStore.stopEditing).toHaveBeenCalled();
    });
  });
});