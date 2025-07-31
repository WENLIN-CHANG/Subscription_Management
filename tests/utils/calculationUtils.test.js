import { describe, it, expect } from 'vitest'
import { calculationUtils } from '../../frontend/scripts/utils/calculationUtils.js'

describe('calculationUtils', () => {
  describe('calculateMonthlyPrice', () => {
    it('應該正確計算月費價格 - 每月', () => {
      const subscription = {
        price: 100,
        cycle: 'monthly'
      }
      const result = calculationUtils.calculateMonthlyPrice(subscription)
      expect(result).toBe(100)
    })

    it('應該正確計算月費價格 - 每年', () => {
      const subscription = {
        price: 1200,
        cycle: 'yearly'
      }
      const result = calculationUtils.calculateMonthlyPrice(subscription)
      expect(result).toBe(100)
    })

    it('應該正確計算月費價格 - 每週', () => {
      const subscription = {
        price: 25,
        cycle: 'weekly'
      }
      const result = calculationUtils.calculateMonthlyPrice(subscription)
      expect(result).toBeCloseTo(108.33, 2)
    })

    it('應該處理無效的週期類型', () => {
      const subscription = {
        price: 100,
        cycle: 'invalid'
      }
      const result = calculationUtils.calculateMonthlyPrice(subscription)
      expect(result).toBe(100) // 預設為 monthly
    })
  })

  describe('calculateTotal', () => {
    it('應該正確計算訂閱總額', () => {
      const subscriptions = [
        { price: 100, cycle: 'monthly' },
        { price: 1200, cycle: 'yearly' },
        { price: 25, cycle: 'weekly' }
      ]
      const result = calculationUtils.calculateTotal(subscriptions)
      expect(result).toBeCloseTo(308.33, 2)
    })

    it('應該處理空陣列', () => {
      const result = calculationUtils.calculateTotal([])
      expect(result).toBe(0)
    })

    it('應該忽略無效的訂閱', () => {
      const subscriptions = [
        { price: 100, cycle: 'monthly' },
        { price: null, cycle: 'monthly' },
        { price: 50, cycle: 'monthly' }
      ]
      const result = calculationUtils.calculateTotal(subscriptions)
      expect(result).toBe(150)
    })
  })

  describe('formatCurrency', () => {
    it('應該正確格式化台幣', () => {
      const result = calculationUtils.formatCurrency(1234.56)
      expect(result).toBe('NT$ 1,235')
    })

    it('應該處理零值', () => {
      const result = calculationUtils.formatCurrency(0)
      expect(result).toBe('NT$ 0')
    })

    it('應該處理負值', () => {
      const result = calculationUtils.formatCurrency(-100)
      expect(result).toBe('NT$ -100')
    })

    it('應該處理大數值', () => {
      const result = calculationUtils.formatCurrency(1234567.89)
      expect(result).toBe('NT$ 1,234,568')
    })
  })

  describe('calculateAnnualSavings', () => {
    it('應該正確計算年度節省金額', () => {
      const monthlyPrice = 100
      const yearlyPrice = 1000
      const result = calculationUtils.calculateAnnualSavings(monthlyPrice, yearlyPrice)
      expect(result).toBe(200) // 100*12 - 1000 = 200
    })

    it('應該處理沒有節省的情況', () => {
      const monthlyPrice = 100
      const yearlyPrice = 1200
      const result = calculationUtils.calculateAnnualSavings(monthlyPrice, yearlyPrice)
      expect(result).toBe(0)
    })

    it('應該處理年費比月費貴的情況', () => {
      const monthlyPrice = 100
      const yearlyPrice = 1500
      const result = calculationUtils.calculateAnnualSavings(monthlyPrice, yearlyPrice)
      expect(result).toBe(0)
    })
  })
})