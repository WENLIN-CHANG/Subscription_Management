import { vi } from 'vitest'

// 模擬 window.scrollTo
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(),
  writable: true
})

// 模擬 localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// 模擬 fetch API
global.fetch = vi.fn()

// 模擬 console 方法以避免測試時的日誌干擾
vi.spyOn(console, 'log').mockImplementation(() => {})
vi.spyOn(console, 'error').mockImplementation(() => {})
vi.spyOn(console, 'warn').mockImplementation(() => {})

// 模擬 ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// 模擬 IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// 重置所有模擬在每個測試前
beforeEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
})