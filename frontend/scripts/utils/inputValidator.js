/**
 * 前端輸入驗證和清理工具
 */

export const InputValidator = {
  /**
   * 清理字符串輸入
   * @param {string} str - 輸入字符串
   * @param {number} maxLength - 最大長度
   * @returns {string} 清理後的字符串
   */
  sanitizeString(str, maxLength = null) {
    if (!str || typeof str !== 'string') {
      return ''
    }

    // 去除首尾空白
    str = str.trim()

    // 限制長度
    if (maxLength && str.length > maxLength) {
      str = str.substring(0, maxLength)
    }

    // 移除危險字符
    str = str.replace(/[<>]/g, '')

    return str
  },

  /**
   * 驗證用戶名
   * @param {string} username - 用戶名
   * @returns {object} 驗證結果
   */
  validateUsername(username) {
    const errors = []

    if (!username || username.trim() === '') {
      errors.push('用戶名不能為空')
      return { isValid: false, errors }
    }

    const cleanUsername = this.sanitizeString(username, 50)

    if (cleanUsername.length < 3) {
      errors.push('用戶名長度至少需要 3 個字符')
    }

    if (cleanUsername.length > 50) {
      errors.push('用戶名長度不能超過 50 個字符')
    }

    // 檢查字符是否合法（字母、數字、下劃線、中文）
    const usernamePattern = /^[a-zA-Z0-9_\u4e00-\u9fff]+$/
    if (!usernamePattern.test(cleanUsername)) {
      errors.push('用戶名只能包含字母、數字、下劃線和中文字符')
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: cleanUsername
    }
  },

  /**
   * 驗證電子郵件
   * @param {string} email - 電子郵件
   * @returns {object} 驗證結果
   */
  validateEmail(email) {
    const errors = []

    if (!email || email.trim() === '') {
      errors.push('電子郵件不能為空')
      return { isValid: false, errors }
    }

    const cleanEmail = this.sanitizeString(email.toLowerCase(), 320)

    // 電子郵件格式驗證
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    if (!emailPattern.test(cleanEmail)) {
      errors.push('電子郵件格式不正確')
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: cleanEmail
    }
  },

  /**
   * 驗證密碼
   * @param {string} password - 密碼
   * @returns {object} 驗證結果
   */
  validatePassword(password) {
    const errors = []

    if (!password) {
      errors.push('密碼不能為空')
      return { isValid: false, errors }
    }

    if (password.length < 6) {
      errors.push('密碼長度至少需要 6 個字符')
    }

    if (password.length > 128) {
      errors.push('密碼長度不能超過 128 個字符')
    }

    // 檢查是否包含危險字符
    const dangerousPatterns = [
      /<script/i,
      /javascript:/i,
      /vbscript:/i,
      /onload=/i,
      /onerror=/i
    ]

    for (const pattern of dangerousPatterns) {
      if (pattern.test(password)) {
        errors.push('密碼包含不允許的字符')
        break
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: password
    }
  },

  /**
   * 驗證訂閱服務名稱
   * @param {string} name - 服務名稱
   * @returns {object} 驗證結果
   */
  validateSubscriptionName(name) {
    const errors = []

    if (!name || name.trim() === '') {
      errors.push('服務名稱不能為空')
      return { isValid: false, errors }
    }

    const cleanName = this.sanitizeString(name, 100)

    if (cleanName.length === 0) {
      errors.push('服務名稱不能為空')
    }

    if (cleanName.length > 100) {
      errors.push('服務名稱長度不能超過 100 個字符')
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: cleanName
    }
  },

  /**
   * 驗證價格
   * @param {string|number} price - 價格
   * @returns {object} 驗證結果
   */
  validatePrice(price) {
    const errors = []

    if (price === null || price === undefined || price === '') {
      errors.push('價格不能為空')
      return { isValid: false, errors }
    }

    const numPrice = parseFloat(price)

    if (isNaN(numPrice)) {
      errors.push('價格必須是數字')
      return { isValid: false, errors }
    }

    if (numPrice < 0) {
      errors.push('價格不能為負數')
    }

    if (numPrice > 999999.99) {
      errors.push('價格不能超過 999,999.99')
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: Math.round(numPrice * 100) / 100 // 保留兩位小數
    }
  },

  /**
   * 驗證分類
   * @param {string} category - 分類
   * @returns {object} 驗證結果
   */
  validateCategory(category) {
    const errors = []
    const validCategories = [
      'entertainment', 'music', 'productivity', 'gaming',
      'news', 'education', 'fitness', 'food', 'shopping', 'other'
    ]

    if (!category || category.trim() === '') {
      errors.push('分類不能為空')
      return { isValid: false, errors }
    }

    const cleanCategory = category.toLowerCase().trim()

    if (!validCategories.includes(cleanCategory)) {
      errors.push(`無效的分類，有效選項：${validCategories.join(', ')}`)
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: cleanCategory
    }
  },

  /**
   * 驗證計費週期
   * @param {string} cycle - 計費週期
   * @returns {object} 驗證結果
   */
  validateCycle(cycle) {
    const errors = []
    const validCycles = ['monthly', 'yearly', 'weekly', 'daily']

    if (!cycle || cycle.trim() === '') {
      errors.push('計費週期不能為空')
      return { isValid: false, errors }
    }

    const cleanCycle = cycle.toLowerCase().trim()

    if (!validCycles.includes(cleanCycle)) {
      errors.push(`無效的計費週期，有效選項：${validCycles.join(', ')}`)
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: cleanCycle
    }
  },

  /**
   * 驗證日期
   * @param {string} date - 日期字符串 (YYYY-MM-DD)
   * @returns {object} 驗證結果
   */
  validateDate(date) {
    const errors = []

    if (!date || date.trim() === '') {
      errors.push('日期不能為空')
      return { isValid: false, errors }
    }

    const cleanDate = this.sanitizeString(date, 10)

    // 驗證日期格式
    const datePattern = /^\d{4}-\d{2}-\d{2}$/
    if (!datePattern.test(cleanDate)) {
      errors.push('日期格式必須為 YYYY-MM-DD')
      return { isValid: false, errors, value: cleanDate }
    }

    // 驗證日期有效性
    const dateObj = new Date(cleanDate)
    if (isNaN(dateObj.getTime()) || dateObj.toISOString().split('T')[0] !== cleanDate) {
      errors.push('無效的日期')
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: cleanDate
    }
  },

  /**
   * 驗證搜索查詢
   * @param {string} query - 搜索查詢
   * @returns {object} 驗證結果
   */
  validateSearchQuery(query) {
    const errors = []

    if (!query) {
      return { isValid: true, errors: [], value: '' }
    }

    const cleanQuery = this.sanitizeString(query, 200)

    // 檢查可疑的 SQL 注入模式
    const sqlPatterns = [
      /\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b/i,
      /\b(or|and)\s+\d+\s*=\s*\d+\b/i,
      /(--|#|\/\*|\*\/)/,
      /'/
    ]

    for (const pattern of sqlPatterns) {
      if (pattern.test(cleanQuery)) {
        errors.push('搜索查詢包含不允許的字符')
        break
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      value: cleanQuery
    }
  },

  /**
   * 驗證完整的訂閱表單
   * @param {object} subscription - 訂閱對象
   * @returns {object} 驗證結果
   */
  validateSubscriptionForm(subscription) {
    const results = {
      name: this.validateSubscriptionName(subscription.name),
      price: this.validatePrice(subscription.price || subscription.originalPrice),
      category: this.validateCategory(subscription.category),
      cycle: this.validateCycle(subscription.cycle),
      startDate: this.validateDate(subscription.startDate)
    }

    const isValid = Object.values(results).every(result => result.isValid)
    const allErrors = Object.entries(results)
      .filter(([field, result]) => !result.isValid)
      .reduce((acc, [field, result]) => {
        acc[field] = result.errors
        return acc
      }, {})

    return {
      isValid,
      errors: allErrors,
      cleanData: {
        name: results.name.value,
        price: results.price.value,
        category: results.category.value,
        cycle: results.cycle.value,
        startDate: results.startDate.value
      }
    }
  },

  /**
   * 驗證用戶註冊表單
   * @param {object} user - 用戶對象
   * @returns {object} 驗證結果
   */
  validateRegistrationForm(user) {
    const results = {
      username: this.validateUsername(user.username),
      email: this.validateEmail(user.email),
      password: this.validatePassword(user.password)
    }

    // 檢查確認密碼
    if (user.confirmPassword !== user.password) {
      results.confirmPassword = {
        isValid: false,
        errors: ['兩次輸入的密碼不一致']
      }
    } else {
      results.confirmPassword = { isValid: true, errors: [] }
    }

    const isValid = Object.values(results).every(result => result.isValid)
    const allErrors = Object.entries(results)
      .filter(([field, result]) => !result.isValid)
      .reduce((acc, [field, result]) => {
        acc[field] = result.errors
        return acc
      }, {})

    return {
      isValid,
      errors: allErrors,
      cleanData: {
        username: results.username.value,
        email: results.email.value,
        password: results.password.value
      }
    }
  },

  /**
   * 驗證登入表單
   * @param {object} user - 用戶對象
   * @returns {object} 驗證結果
   */
  validateLoginForm(user) {
    const results = {
      username: this.validateUsername(user.username),
      password: this.validatePassword(user.password)
    }

    const isValid = Object.values(results).every(result => result.isValid)
    const allErrors = Object.entries(results)
      .filter(([field, result]) => !result.isValid)
      .reduce((acc, [field, result]) => {
        acc[field] = result.errors
        return acc
      }, {})

    return {
      isValid,
      errors: allErrors,
      cleanData: {
        username: results.username.value,
        password: results.password.value
      }
    }
  }
}