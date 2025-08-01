// 測試環境設置
import { JSDOM } from 'jsdom';

// 設置 DOM 環境
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost:3000',
  pretendToBeVisual: true,
  resources: 'usable'
});

// 設置全局變量
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.HTMLElement = dom.window.HTMLElement;
global.customElements = dom.window.customElements;

// 模擬 localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// 模擬 fetch API
global.fetch = jest.fn();

// 設置測試超時時間
jest.setTimeout(10000);

// 清理每個測試後的狀態
afterEach(() => {
  // 清理 DOM
  document.body.innerHTML = '';
  
  // 清理 localStorage mock
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
  
  // 清理 fetch mock
  fetch.mockClear();
  
  // 清理全局狀態
  if (window.Alpine) {
    window.Alpine = null;
  }
});