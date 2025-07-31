# 訂閱管理系統

一個現代化的訂閱管理和預算追蹤系統，使用 FastAPI 後端和 AlpineJS + DaisyUI 前端。

## 功能特色

- 🔐 用戶註冊和登入系統
- 🔑 密碼修改功能
- 📊 訂閱服務管理和追蹤
- 💰 月度預算設定和監控
- 📈 支出統計和分析
- 🔄 數據雲端同步
- 📱 響應式設計 (支援桌面/平板/手機)
- 🍔 移動端漢堡選單
- 🌙 日間/夜間主題切換
- 🚀 智能數據遷移

## 快速開始

### 前置要求

- Node.js (推薦 v18+)
- Python 3.8+
- npm 或 yarn

### 安裝依賴

```bash
# 安裝前端依賴
npm install

# 安裝後端依賴
cd backend
pip install -r requirements.txt
cd ..
```

### 啟動開發服務器

```bash
# 同時啟動前端和後端
npm run dev
```

這個命令會同時啟動：
- 前端開發服務器 (Vite) - http://localhost:5173
- 後端 API 服務器 (FastAPI) - http://localhost:8000

### 單獨啟動服務

```bash
# 只啟動前端
npm run frontend

# 只啟動後端
npm run backend

# 或者直接啟動後端
npm run backend-only
```

## API 文檔

當後端運行時，可以訪問以下地址查看 API 文檔：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 技術棧

### 前端
- **AlpineJS** - 輕量級響應式框架
- **DaisyUI** - Tailwind CSS 組件庫
- **Vite** - 快速構建工具

### 後端
- **FastAPI** - 現代 Python Web 框架
- **SQLAlchemy** - ORM 數據庫工具
- **JWT** - 安全認證
- **SQLite** - 數據庫（默認）

## 項目結構

```
├── frontend/
│   ├── app.js              # 主應用邏輯
│   ├── index.html          # 主頁面
│   ├── style.css           # 樣式文件
│   └── scripts/            # 功能模塊 (按功能分類)
│       ├── auth/           # 認證相關
│       │   ├── apiClient.js    # API 客戶端
│       │   └── authManager.js  # 認證管理
│       ├── business/       # 業務邏輯
│       │   ├── budgetManager.js      # 預算管理
│       │   ├── statisticsManager.js # 統計分析
│       │   └── subscriptionActions.js # 訂閱操作
│       ├── data/           # 資料管理
│       │   ├── dataManager.js      # 數據管理
│       │   ├── migrationManager.js # 數據遷移
│       │   └── sampleData.js       # 範例數據
│       ├── ui/             # 介面與互動
│       │   ├── stateManager.js     # 狀態管理
│       │   ├── themeManager.js     # 主題管理
│       │   └── uiUtils.js          # UI 工具
│       └── utils/          # 工具函數
│           ├── calculationUtils.js # 計算工具
│           └── types.js            # 型別定義
├── backend/
│   ├── app/
│   │   ├── api/           # API 端點
│   │   │   ├── auth.py         # 認證相關 API
│   │   │   ├── subscriptions.py # 訂閱管理 API
│   │   │   └── budget.py       # 預算管理 API
│   │   ├── core/          # 核心配置
│   │   ├── database/      # 數據庫配置
│   │   ├── models/        # 數據模型
│   │   └── schemas/       # Pydantic 模式
│   ├── requirements.txt   # Python 依賴
│   └── run_dev.py        # 開發服務器啟動
└── package.json          # Node.js 配置
```

## 開發說明

### 代碼組織
前端採用模組化設計，按功能領域分類：
- **auth/**: 用戶認證、API 通訊
- **business/**: 核心業務邏輯（訂閱、預算、統計）
- **data/**: 資料存取、遷移、範例資料
- **ui/**: 用戶介面狀態、主題、UI 工具
- **utils/**: 純工具函數、型別定義

### 響應式設計
- **桌面版 (1024px+)**: 完整水平導航欄
- **平板版 (768px-1024px)**: 水平導航欄
- **手機版 (768px以下)**: 漢堡選單

### 數據遷移
系統支持從本地存儲自動遷移到雲端數據庫，首次登入時會自動提示。

### 環境變量
可以創建 `.env` 文件來配置：
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./subscription_db.sqlite
```

### 貢獻指南
1. Fork 項目
2. 創建功能分支
3. 提交更改
4. 發起 Pull Request

## 授權
ISC License