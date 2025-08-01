# 訂閱管理系統 - 後端架構文檔

## 架構概覽

本系統採用 **清潔架構 (Clean Architecture)** 結合 **領域驅動設計 (Domain Driven Design)** 的方法重構，實現了高度可維護、可測試和可擴展的後端系統。

## 架構層次

### 1. 領域層 (Domain Layer)
位於 `app/domain/` 目錄下，包含核心業務邏輯和規則。

#### 領域服務 (Domain Services)
- `SubscriptionDomainService`: 處理訂閱相關的核心業務邏輯
  - 計算台幣價格
  - 計算月度/年度成本
  - 計算下次計費日期
  - 訂閱數據驗證

- `BudgetDomainService`: 處理預算相關的核心業務邏輯
  - 計算預算使用情況
  - 生成預算建議
  - 計算節省潛力

#### 領域接口 (Domain Interfaces)
- `IUserRepository`, `ISubscriptionRepository`, `IBudgetRepository`: Repository 接口
- `IExchangeRateService`, `IEmailService`, `ICacheService`: 外部服務接口
- `IUnitOfWork`: 工作單元接口

### 2. 應用層 (Application Layer)
位於 `app/application/` 目錄下，協調領域服務和基礎設施。

#### 應用服務 (Application Services)
- `SubscriptionApplicationService`: 訂閱應用服務
- `BudgetApplicationService`: 預算應用服務

#### 數據傳輸對象 (DTOs)
- `subscription_dtos.py`: 訂閱相關的命令、查詢和響應對象
- `budget_dtos.py`: 預算相關的命令、查詢和響應對象

### 3. 基礎設施層 (Infrastructure Layer)
位於 `app/infrastructure/` 目錄下，實現外部依賴和技術細節。

#### Repository 實現
- `SQLAlchemyBaseRepository`: 基礎 Repository 實現
- `UserRepository`, `SubscriptionRepository`, `BudgetRepository`: 具體 Repository 實現
- `SQLAlchemyUnitOfWork`: Unit of Work 模式實現

#### 外部服務實現
- `ExchangeRateServiceImpl`: 匯率服務實現

#### 依賴注入
- `DIContainer`: 自定義依賴注入容器
- `dependencies.py`: FastAPI 依賴注入配置

### 4. 接口層 (Interface Layer)
位於 `app/api/` 目錄下，處理 HTTP 請求和響應。

#### API 版本控制
- `v1/`: API v1 版本
  - `endpoints/`: 具體的 API 端點
  - `router.py`: 路由配置

### 5. 共通層 (Common Layer)
位於 `app/common/` 目錄下，包含共享的組件。

#### 響應格式
- `ApiResponse`: 統一的 API 響應格式
- `PaginatedResponse`: 分頁響應格式

#### 異常處理
- `ApplicationException`: 應用程序基礎異常
- 各種具體異常類型
- 全局異常處理器

#### 驗證器
- 各種業務規則驗證器
- 請求數據驗證

#### 中間件
- 請求驗證中間件
- 響應頭中間件
- 請求計時中間件
- API 指標中間件

## 核心設計模式

### 1. Repository 模式
- 抽象化數據訪問邏輯
- 便於單元測試
- 支持不同數據源切換

### 2. Unit of Work 模式
- 管理事務邊界
- 確保數據一致性
- 提供統一的數據訪問接口

### 3. 依賴注入 (DI)
- 降低耦合度
- 提高可測試性
- 支持運行時配置

### 4. 領域驅動設計 (DDD)
- 領域服務封裝核心業務邏輯
- 領域對象負責自身的業務規則
- 清晰的領域邊界

## 主要特性

### 1. 統一響應格式
```json
{
  "status": "success|error|warning",
  "message": "操作描述",
  "data": "實際數據",
  "errors": ["錯誤列表"],
  "metadata": {"額外信息"}
}
```

### 2. API 版本控制
- 支持多版本並存
- 向後兼容
- 清晰的版本路徑

### 3. 完善的錯誤處理
- 全局異常攔截
- 統一錯誤響應格式
- 詳細的錯誤信息

### 4. 請求驗證
- 數據格式驗證
- 業務規則驗證
- 安全性檢查

### 5. 中間件支持
- 請求/響應處理
- 日誌記錄
- 性能監控
- 安全頭添加

## 目錄結構

```
app/
├── api/                    # 接口層
│   └── v1/                 # API v1 版本
│       ├── endpoints/      # API 端點
│       └── router.py       # 路由配置
├── application/            # 應用層
│   ├── dtos/               # 數據傳輸對象
│   └── services/           # 應用服務
├── common/                 # 共通層
│   ├── exceptions.py       # 異常定義
│   ├── responses.py        # 響應格式
│   ├── validators.py       # 驗證器
│   └── middleware.py       # 中間件
├── domain/                 # 領域層
│   ├── interfaces/         # 領域接口
│   └── services/           # 領域服務
├── infrastructure/         # 基礎設施層
│   ├── repositories/       # Repository 實現
│   ├── services/           # 外部服務實現
│   ├── unit_of_work.py     # UoW 實現
│   ├── dependencies.py     # 依賴注入配置
│   └── container.py        # DI 容器
├── core/                   # 核心配置
├── database/               # 資料庫配置
├── models/                 # 資料模型
├── schemas/                # Pydantic 模型
└── main_new.py             # 新版主應用程序
```

## 使用方式

### 1. 啟動新版本
```bash
# 使用新的架構啟動
uvicorn app.main_new:app --reload
```

### 2. 訪問 API 文檔
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### 3. API 端點
- 新版本: `/api/v1/...`
- 向後兼容: `/api/...`

## 測試策略

### 1. 單元測試
- 領域服務測試
- Repository 測試
- 應用服務測試

### 2. 集成測試
- API 端點測試
- 資料庫集成測試

### 3. 模擬測試
- 外部服務模擬
- 依賴注入模擬

## 部署考慮

### 1. 環境配置
- 開發、測試、生產環境分離
- 環境變數配置

### 2. 監控和日誌
- 結構化日誌
- 性能監控
- 錯誤追蹤

### 3. 擴展性
- 水平擴展支持
- 快取策略
- 資料庫優化

## 遷移建議

1. **漸進式遷移**: 可以同時運行舊版和新版，逐步遷移功能
2. **API 兼容性**: 新版本保持向後兼容
3. **測試覆蓋**: 在遷移過程中保持測試覆蓋率
4. **監控指標**: 監控新舊版本的性能指標

## 未來擴展

1. **事件驅動架構**: 引入領域事件
2. **CQRS 模式**: 讀寫分離
3. **微服務分解**: 按領域分解服務
4. **快取策略**: 引入 Redis 快取
5. **訊息佇列**: 非同步處理