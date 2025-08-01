# 測試執行指南

## 概述

本指南詳細說明如何執行訂閱管理系統的全面測試套件，以驗證從簡單 FastAPI 結構重構為 Clean Architecture + DDD 架構後的系統穩定性和性能。

## 測試架構

### 測試分層結構

```
tests/
├── conftest.py                    # 測試配置和 fixtures
├── domain/                        # 領域層測試
│   └── services/
│       ├── test_subscription_domain_service.py
│       └── test_budget_domain_service.py
├── application/                   # 應用層測試
│   └── services/
│       ├── test_subscription_application_service.py
│       └── test_budget_application_service.py
├── infrastructure/                # 基礎設施層測試
│   ├── test_unit_of_work.py
│   ├── test_container.py
│   └── repositories/
│       └── test_subscription_repository.py
├── api/                          # API 測試
│   └── v1/
│       ├── test_subscriptions_api.py
│       └── test_budgets_api.py
├── common/                       # 通用組件測試
│   ├── test_exceptions.py
│   └── test_exception_handlers.py
├── compatibility/                # 向後兼容性測試
│   ├── test_api_compatibility.py
│   └── test_data_migration.py
└── performance/                  # 性能測試
    └── test_architecture_performance.py
```

### 測試標記

```python
# 測試類型標記
@pytest.mark.unit           # 單元測試
@pytest.mark.integration    # 集成測試
@pytest.mark.api           # API 測試

# 層級標記
@pytest.mark.domain        # 領域層
@pytest.mark.application   # 應用層
@pytest.mark.infrastructure # 基礎設施層

# 功能標記
@pytest.mark.auth          # 認證相關
@pytest.mark.compatibility # 兼容性測試
@pytest.mark.performance   # 性能測試
@pytest.mark.slow          # 慢速測試
```

## 測試環境準備

### 1. 安装依賴

```bash
# 進入後端目錄
cd backend

# 安裝測試依賴
pip install pytest pytest-asyncio pytest-cov pytest-mock psutil
```

### 2. 環境配置

確保以下環境變量正確設置：

```bash
export ENVIRONMENT=testing
export SECRET_KEY=test_secret_key
export DATABASE_URL=sqlite:///./test.db
```

### 3. 數據庫準備

```bash
# 創建測試數據庫表
python -c "from app.database.connection import create_tables; create_tables()"
```

## 測試執行方法

### 1. 執行所有測試

```bash
# 基本執行
pytest

# 詳細輸出
pytest -v

# 帶覆蓋率報告
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### 2. 按標記執行測試

```bash
# 只執行單元測試
pytest -m unit

# 只執行集成測試
pytest -m integration

# 執行 API 測試
pytest -m api

# 執行領域層測試
pytest -m domain

# 執行兼容性測試
pytest -m compatibility

# 排除慢速測試
pytest -m "not slow"

# 執行性能測試
pytest -m performance
```

### 3. 按層級執行測試

```bash
# 領域層測試
pytest tests/domain/

# 應用層測試
pytest tests/application/

# 基礎設施層測試
pytest tests/infrastructure/

# API 層測試
pytest tests/api/

# 兼容性測試
pytest tests/compatibility/

# 性能測試
pytest tests/performance/
```

### 4. 執行特定測試文件

```bash
# 測試訂閱領域服務
pytest tests/domain/services/test_subscription_domain_service.py

# 測試 API v1 訂閱端點
pytest tests/api/v1/test_subscriptions_api.py

# 測試依賴注入容器
pytest tests/infrastructure/test_container.py
```

### 5. 執行特定測試類或方法

```bash
# 執行特定測試類
pytest tests/domain/services/test_subscription_domain_service.py::TestSubscriptionDomainService

# 執行特定測試方法
pytest tests/api/v1/test_subscriptions_api.py::TestSubscriptionsAPIv1::TestCreateSubscription::test_create_subscription_success
```

## 測試場景和用例

### 1. 核心功能驗證

**領域層測試**
- 價格計算邏輯（月度/年度成本）
- 計費日期計算
- 類別分組和統計
- 數據驗證規則
- 匯率轉換邏輯

**應用層測試**
- 業務流程編排
- 事務管理
- 錯誤處理
- 數據轉換 (DTO)
- 服務協調

**基礎設施層測試**
- Repository 模式實現
- Unit of Work 事務管理
- 依賴注入容器
- 數據持久化

### 2. API 端點測試

**訂閱管理 API**
```bash
# 測試所有訂閱 API
pytest tests/api/v1/test_subscriptions_api.py -v

# 重點測試場景：
# - 創建訂閱（各種數據格式）
# - 獲取訂閱列表（分頁、過濾）
# - 更新訂閱（部分更新、完整更新）
# - 刪除訂閱
# - 批量操作
# - 獲取摘要統計
```

**預算管理 API**
```bash
# 測試所有預算 API
pytest tests/api/v1/test_budgets_api.py -v

# 重點測試場景：
# - 創建和管理預算
# - 獲取預算使用情況
# - 預算分析和建議
# - 預算警告機制
```

### 3. 兼容性測試

**API 兼容性**
```bash
# 測試新舊 API 兼容性
pytest tests/compatibility/test_api_compatibility.py -v

# 重點驗證：
# - 舊 API 端點仍然可用
# - 響應格式一致性
# - 錯誤處理兼容性
# - 功能行為一致性
```

**數據遷移兼容性**
```bash
# 測試數據遷移
pytest tests/compatibility/test_data_migration.py -v

# 重點驗證：
# - 現有數據能正常訪問
# - 新舊字段映射正確
# - 數據完整性
# - 外鍵約束
```

### 4. 性能測試

```bash
# 執行性能測試（需要更多時間）
pytest tests/performance/ -v -s

# 重點測試：
# - API 響應時間對比
# - 內存使用對比
# - 並發處理能力
# - 數據庫查詢性能
# - 負載測試
```

## 測試報告和分析

### 1. 覆蓋率報告

```bash
# 生成 HTML 覆蓋率報告
pytest --cov=app --cov-report=html

# 查看報告
# 在瀏覽器中打開 coverage_html/index.html
```

### 2. 測試結果報告

```bash
# 生成 JUnit XML 報告
pytest --junitxml=test_results.xml

# 生成詳細的測試報告
pytest --html=report.html --self-contained-html
```

### 3. 性能基準報告

性能測試會在控制台輸出詳細的性能對比數據：

```
API 響應時間對比:
舊架構 - 平均: 0.0234s, 中位數: 0.0189s
新架構 - 平均: 0.0267s, 中位數: 0.0223s
性能變化: +14.10%

內存使用對比:
舊架構內存增長: 2.34 MB
新架構內存增長: 3.12 MB
内存使用比率: 1.33

數據庫查詢性能:
獲取所有訂閱: 0.0045s (15 條)
獲取活躍訂閱: 0.0038s (12 條)
按類別查詢: 0.0042s (8 條)
```

## 持續集成配置

### GitHub Actions 配置示例

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run unit tests
      run: |
        cd backend
        pytest -m unit --cov=app
    
    - name: Run integration tests
      run: |
        cd backend
        pytest -m integration
    
    - name: Run compatibility tests
      run: |
        cd backend
        pytest -m compatibility
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 最佳實踐

### 1. 測試執行順序

建議按以下順序執行測試：

1. **單元測試** - 快速驗證核心邏輯
2. **集成測試** - 驗證組件協作
3. **API 測試** - 驗證端點功能
4. **兼容性測試** - 確保向後兼容
5. **性能測試** - 驗證性能指標

### 2. 調試測試失敗

```bash
# 詳細輸出失敗信息
pytest -vvv --tb=long

# 在第一個失敗處停止
pytest -x

# 進入調試模式
pytest --pdb

# 只運行失敗的測試
pytest --lf
```

### 3. 並行執行

```bash
# 安裝 pytest-xdist
pip install pytest-xdist

# 並行執行測試
pytest -n auto

# 指定進程數
pytest -n 4
```

### 4. 測試數據清理

測試使用獨立的測試數據庫，每個測試方法執行後會自動清理數據。如需手動清理：

```bash
# 刪除測試數據庫
rm test.db

# 重新創建表結構
python -c "from app.database.connection import create_tables; create_tables()"
```

## 故障排除

### 常見問題

1. **導入錯誤**
   ```bash
   # 確保 PYTHONPATH 包含項目根目錄
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

2. **數據庫錯誤**
   ```bash
   # 重新創建測試數據庫
   rm test.db
   python -c "from app.database.connection import create_tables; create_tables()"
   ```

3. **依賴缺失**
   ```bash
   # 重新安裝依賴
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov pytest-mock psutil
   ```

4. **權限問題**
   ```bash
   # 確保測試文件有執行權限
   chmod +x tests/*.py
   ```

### 性能測試注意事項

- 性能測試會消耗較多系統資源，建議在專用測試環境執行
- 某些性能測試可能受到系統負載影響，結果會有一定波動
- 建議多次執行性能測試取平均值
- 在 CI/CD 環境中可能需要調整性能基準

## 結論

這個測試套件提供了全面的測試覆蓋，確保新架構：

1. **功能正確性** - 所有業務邏輯按預期工作
2. **架構穩定性** - 各層組件協作良好
3. **向後兼容性** - 不破壞現有功能
4. **性能可接受** - 重構不會顯著影響性能
5. **錯誤處理** - 異常情況得到適當處理

執行完整的測試套件後，你可以確信新架構已準備好投入生產使用。