import { describe, it, expect } from 'vitest'

describe('測試環境驗證', () => {
  it('基本數學運算應該正常工作', () => {
    expect(1 + 1).toBe(2)
    expect(2 * 3).toBe(6)
    expect(10 / 2).toBe(5)
  })

  it('字串操作應該正常工作', () => {
    expect('hello').toBe('hello')
    expect('hello world'.includes('world')).toBe(true)
    expect('test'.toUpperCase()).toBe('TEST')
  })

  it('陣列操作應該正常工作', () => {
    const arr = [1, 2, 3]
    expect(arr).toHaveLength(3)
    expect(arr.includes(2)).toBe(true)
    expect(arr.map(x => x * 2)).toEqual([2, 4, 6])
  })

  it('物件操作應該正常工作', () => {
    const obj = { name: 'test', value: 42 }
    expect(obj.name).toBe('test')
    expect(obj.value).toBe(42)
    expect(Object.keys(obj)).toEqual(['name', 'value'])
  })

  it('Promise 應該正常工作', async () => {
    const promise = Promise.resolve('success')
    const result = await promise
    expect(result).toBe('success')
  })
})