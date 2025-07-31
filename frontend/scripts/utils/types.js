/**
 * 統一的資料類型定義
 * 這個檔案定義了前後端共用的資料結構和欄位名稱
 */

// 訂閱週期枚舉
export const SubscriptionCycle = {
  MONTHLY: 'monthly',
  QUARTERLY: 'quarterly', 
  YEARLY: 'yearly'
}

// 訂閱分類枚舉
export const SubscriptionCategory = {
  STREAMING: 'streaming',
  SOFTWARE: 'software',
  NEWS: 'news',
  GAMING: 'gaming',
  MUSIC: 'music',
  EDUCATION: 'education',
  PRODUCTIVITY: 'productivity',
  OTHER: 'other'
}

// 貨幣枚舉
export const Currency = {
  TWD: 'TWD',
  USD: 'USD',
  EUR: 'EUR',
  JPY: 'JPY',
  GBP: 'GBP',
  KRW: 'KRW',
  CNY: 'CNY'
}

// 欄位名稱映射 - 統一使用後端的 snake_case 命名
export const SubscriptionFields = {
  // 基本欄位
  ID: 'id',
  USER_ID: 'user_id',
  NAME: 'name',
  PRICE: 'price',                    // 台幣價格 (轉換後)
  ORIGINAL_PRICE: 'original_price',  // 原始價格
  CURRENCY: 'currency',              // 原始貨幣
  CYCLE: 'cycle',                    // 訂閱週期
  CATEGORY: 'category',              // 服務分類
  START_DATE: 'start_date',          // 開始日期
  IS_ACTIVE: 'is_active',            // 是否啟用
  CREATED_AT: 'created_at',          // 創建時間
  UPDATED_AT: 'updated_at'           // 更新時間
}

// 前端舊欄位名稱對應 (用於相容性)
export const LegacyFields = {
  startDate: SubscriptionFields.START_DATE,
  originalPrice: SubscriptionFields.ORIGINAL_PRICE
}

/**
 * 訂閱資料結構定義 (使用統一的欄位名稱)
 */
export const SubscriptionSchema = {
  // 創建訂閱時需要的欄位
  create: [
    SubscriptionFields.NAME,
    SubscriptionFields.ORIGINAL_PRICE,
    SubscriptionFields.CURRENCY,
    SubscriptionFields.CYCLE,
    SubscriptionFields.CATEGORY,
    SubscriptionFields.START_DATE
  ],
  
  // 更新訂閱時可選的欄位
  update: [
    SubscriptionFields.NAME,
    SubscriptionFields.ORIGINAL_PRICE,
    SubscriptionFields.CURRENCY,
    SubscriptionFields.CYCLE,
    SubscriptionFields.CATEGORY,
    SubscriptionFields.START_DATE,
    SubscriptionFields.IS_ACTIVE
  ],
  
  // 完整的回應欄位
  response: [
    SubscriptionFields.ID,
    SubscriptionFields.USER_ID,
    SubscriptionFields.NAME,
    SubscriptionFields.PRICE,
    SubscriptionFields.ORIGINAL_PRICE,
    SubscriptionFields.CURRENCY,
    SubscriptionFields.CYCLE,
    SubscriptionFields.CATEGORY,
    SubscriptionFields.START_DATE,
    SubscriptionFields.IS_ACTIVE,
    SubscriptionFields.CREATED_AT,
    SubscriptionFields.UPDATED_AT
  ]
}

/**
 * 資料轉換工具函數
 */
export const DataMapper = {
  /**
   * 將前端格式轉換為統一格式
   * 支援兩種輸入格式：camelCase (舊格式) 和 統一格式欄位名稱
   * @param {Object} frontendData - 前端資料
   * @returns {Object} 統一格式資料 (snake_case)
   */
  frontendToUnified(frontendData) {
    const unified = {}
    
    // 直接處理已經使用統一欄位名稱的資料
    Object.values(SubscriptionFields).forEach(field => {
      if (frontendData[field] !== undefined) {
        unified[field] = frontendData[field]
      }
    })
    
    // 處理舊格式的 camelCase 欄位名稱 (相容性支援)
    const legacyMappings = {
      name: SubscriptionFields.NAME,
      price: SubscriptionFields.PRICE,
      currency: SubscriptionFields.CURRENCY,
      cycle: SubscriptionFields.CYCLE,
      category: SubscriptionFields.CATEGORY,
      is_active: SubscriptionFields.IS_ACTIVE,
      originalPrice: SubscriptionFields.ORIGINAL_PRICE,
      startDate: SubscriptionFields.START_DATE
    }
    
    // 只有在統一格式中不存在時，才使用舊格式
    Object.keys(legacyMappings).forEach(oldKey => {
      const newKey = legacyMappings[oldKey]
      if (frontendData[oldKey] !== undefined && unified[newKey] === undefined) {
        unified[newKey] = frontendData[oldKey]
      }
    })
    
    return unified
  },
  
  /**
   * 將後端格式轉換為前端格式 (保持相容性)
   * @param {Object} backendData - 後端資料 (snake_case)
   * @returns {Object} 前端格式資料 (camelCase)
   */
  backendToFrontend(backendData) {
    const frontend = { ...backendData }
    
    // 轉換特殊欄位名稱
    if (backendData[SubscriptionFields.START_DATE] !== undefined) {
      frontend.startDate = backendData[SubscriptionFields.START_DATE]
    }
    
    if (backendData[SubscriptionFields.ORIGINAL_PRICE] !== undefined) {
      frontend.originalPrice = backendData[SubscriptionFields.ORIGINAL_PRICE]
    }
    
    return frontend
  },
  
  /**
   * 驗證資料欄位
   * @param {Object} data - 要驗證的資料
   * @param {Array} requiredFields - 必要欄位列表
   * @returns {Object} 驗證結果 {isValid: boolean, missingFields: Array}
   */
  validate(data, requiredFields) {
    const missingFields = requiredFields.filter(field => 
      data[field] === undefined || data[field] === null || data[field] === ''
    )
    
    return {
      isValid: missingFields.length === 0,
      missingFields
    }
  }
}

/**
 * 預設值定義
 */
export const DefaultValues = {
  subscription: {
    [SubscriptionFields.CURRENCY]: Currency.TWD,
    [SubscriptionFields.CYCLE]: SubscriptionCycle.MONTHLY,
    [SubscriptionFields.CATEGORY]: SubscriptionCategory.OTHER,
    [SubscriptionFields.IS_ACTIVE]: true
  }
}