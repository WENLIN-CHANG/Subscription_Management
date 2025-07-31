// 主題管理模組 - 處理亮色/深色主題切換
export const themeManager = {
  // 可用主題配置
  themes: {
    light: {
      name: 'corporate',
      displayName: '日間模式',
      icon: '☀️',
      type: 'light'
    },
    dark: {
      name: 'dark',
      displayName: '夜間模式', 
      icon: '🌙',
      type: 'dark'
    }
  },

  // 當前主題
  currentTheme: 'corporate',
  
  // 系統偏好設定檢測
  systemPreference: null,

  // 初始化主題管理器
  init() {
    // 檢測系統深色模式偏好
    this.detectSystemPreference()
    
    // 從本地存儲載入用戶偏好
    this.loadUserPreference()
    
    // 監聽系統主題變化
    this.listenToSystemChanges()
    
    // 應用主題
    this.applyTheme(this.currentTheme)
    
    console.log('主題管理器初始化完成，當前主題:', this.currentTheme)
  },

  // 檢測系統深色模式偏好
  detectSystemPreference() {
    if (window.matchMedia) {
      this.systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
  },

  // 從本地存儲載入用戶偏好
  loadUserPreference() {
    const saved = localStorage.getItem('theme-preference')
    if (saved) {
      this.currentTheme = saved
    } else {
      // 如果沒有保存的偏好，使用系統偏好
      if (this.systemPreference === 'dark') {
        this.currentTheme = 'dark'
      } else {
        this.currentTheme = 'corporate'
      }
    }
  },

  // 保存用戶偏好到本地存儲
  saveUserPreference(theme) {
    localStorage.setItem('theme-preference', theme)
  },

  // 監聽系統主題變化
  listenToSystemChanges() {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', (e) => {
        this.systemPreference = e.matches ? 'dark' : 'light'
        
        // 如果用戶沒有手動設置過主題，跟隨系統變化
        const hasUserPreference = localStorage.getItem('theme-preference')
        if (!hasUserPreference) {
          const newTheme = this.systemPreference === 'dark' ? 'dark' : 'corporate'
          this.setTheme(newTheme, false) // false 表示不保存到本地存儲
        }
      })
    }
  },

  // 應用主題到 HTML 元素
  applyTheme(themeName) {
    const html = document.documentElement
    html.setAttribute('data-theme', themeName)
    this.currentTheme = themeName
    
    // 觸發主題變化事件
    const event = new CustomEvent('themeChanged', {
      detail: { theme: themeName, themeInfo: this.getThemeInfo(themeName) }
    })
    document.dispatchEvent(event)
  },

  // 設置主題
  setTheme(themeName, savePreference = true) {
    if (!themeName || !this.isValidTheme(themeName)) {
      console.warn('無效的主題名稱:', themeName)
      return false
    }

    // 添加過渡動畫類
    const html = document.documentElement
    html.classList.add('theme_transition')
    
    // 應用新主題
    this.applyTheme(themeName)
    
    // 保存用戶偏好
    if (savePreference) {
      this.saveUserPreference(themeName)
    }
    
    // 移除過渡動畫類
    setTimeout(() => {
      html.classList.remove('theme_transition')
    }, 300)
    
    return true
  },

  // 切換主題（亮色/深色模式簡單切換）
  toggleTheme() {
    const currentType = this.getCurrentThemeType()
    let newTheme
    
    if (currentType === 'light') {
      newTheme = 'dark' // 預設深色主題
    } else {
      newTheme = 'corporate' // 預設亮色主題
    }
    
    return this.setTheme(newTheme)
  },

  // 獲取當前主題類型（light/dark）
  getCurrentThemeType() {
    const themeInfo = this.getThemeInfo(this.currentTheme)
    return themeInfo ? themeInfo.type : 'light'
  },

  // 獲取主題資訊
  getThemeInfo(themeName) {
    // 在預定義主題中查找
    for (const theme of Object.values(this.themes)) {
      if (theme.name === themeName) {
        return theme
      }
    }
    
    // 如果不在預定義中，根據主題名稱推測
    const darkThemes = ['dark', 'night', 'dracula', 'black', 'luxury', 'business']
    const isDark = darkThemes.includes(themeName)
    
    return {
      name: themeName,
      displayName: themeName,
      icon: isDark ? '🌙' : '☀️',
      type: isDark ? 'dark' : 'light'
    }
  },

  // 檢查主題是否有效
  isValidTheme(themeName) {
    // 檢查是否為預定義主題
    for (const theme of Object.values(this.themes)) {
      if (theme.name === themeName) {
        return true
      }
    }
    
    // 檢查是否為 DaisyUI 內建主題
    const daisyUIThemes = [
      'light', 'dark', 'cupcake', 'bumblebee', 'emerald', 'corporate', 'synthwave',
      'retro', 'cyberpunk', 'valentine', 'halloween', 'garden', 'forest', 'aqua',
      'lofi', 'pastel', 'fantasy', 'wireframe', 'black', 'luxury', 'dracula',
      'cmyk', 'autumn', 'business', 'acid', 'lemonade', 'night', 'coffee', 'winter'
    ]
    
    return daisyUIThemes.includes(themeName)
  },

  // 獲取所有可用主題
  getAvailableThemes() {
    return Object.values(this.themes)
  },

  // 獲取當前主題資訊
  getCurrentThemeInfo() {
    return this.getThemeInfo(this.currentTheme)
  },

  // 是否為深色主題
  isDarkTheme(themeName = this.currentTheme) {
    const themeInfo = this.getThemeInfo(themeName)
    return themeInfo.type === 'dark'
  },

  // 是否為亮色主題
  isLightTheme(themeName = this.currentTheme) {
    return !this.isDarkTheme(themeName)
  }
}

// 自動初始化（延遲初始化以確保 DOM 準備完成）
document.addEventListener('DOMContentLoaded', () => {
  themeManager.init()
})