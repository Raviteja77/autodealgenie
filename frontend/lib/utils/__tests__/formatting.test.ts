/**
 * Unit tests for formatting utilities
 * 
 * Tests all formatting functions to ensure they work correctly
 */

import {
  formatPrice,
  formatCompactPrice,
  formatTimestamp,
  formatFullTimestamp,
  formatPercentage,
  calculateDiscountPercent,
  formatNumber,
  truncateText,
  formatSavings,
} from '../formatting';

describe('Formatting Utilities', () => {
  describe('formatPrice', () => {
    it('should format numbers as USD currency', () => {
      expect(formatPrice(25000)).toBe('$25,000');
      expect(formatPrice(1234.56)).toBe('$1,235');
      expect(formatPrice(0)).toBe('$0');
    });

    it('should handle negative numbers', () => {
      expect(formatPrice(-500)).toBe('-$500');
    });
  });

  describe('formatCompactPrice', () => {
    it('should format large numbers compactly', () => {
      expect(formatCompactPrice(25000)).toBe('$25.0K');
      expect(formatCompactPrice(1500000)).toBe('$1.5M');
      expect(formatCompactPrice(2500000000)).toBe('$2.5B');
    });

    it('should format small numbers normally', () => {
      expect(formatCompactPrice(500)).toBe('$500');
    });
  });

  describe('formatNumber', () => {
    it('should format numbers with commas', () => {
      expect(formatNumber(45000)).toBe('45,000');
      expect(formatNumber(1234567)).toBe('1,234,567');
    });
  });

  describe('formatPercentage', () => {
    it('should calculate and format percentages', () => {
      expect(formatPercentage(45, 100)).toBe('45%');
      expect(formatPercentage(33.333, 100, 1)).toBe('33.3%');
    });

    it('should handle zero total', () => {
      expect(formatPercentage(10, 0)).toBe('0%');
    });
  });

  describe('calculateDiscountPercent', () => {
    it('should calculate discount percentage', () => {
      expect(calculateDiscountPercent(25000, 22500)).toBe(10);
      expect(calculateDiscountPercent(30000, 27000)).toBe(10);
    });

    it('should handle zero original price', () => {
      expect(calculateDiscountPercent(0, 100)).toBe(0);
    });

    it('should handle negative discounts (price increase)', () => {
      expect(calculateDiscountPercent(20000, 22000)).toBe(-10);
    });
  });

  describe('truncateText', () => {
    it('should truncate long text', () => {
      expect(truncateText('This is a long message', 10)).toBe('This is a...');
    });

    it('should not truncate short text', () => {
      expect(truncateText('Short', 10)).toBe('Short');
    });
  });

  describe('formatSavings', () => {
    it('should format positive savings', () => {
      const result = formatSavings(25000, 22500);
      expect(result.amount).toBe(2500);
      expect(result.color).toBe('success');
      expect(result.text).toContain('saved');
    });

    it('should format negative savings (over asking)', () => {
      const result = formatSavings(20000, 22000);
      expect(result.amount).toBe(-2000);
      expect(result.color).toBe('error');
      expect(result.text).toContain('over asking');
    });

    it('should handle no savings', () => {
      const result = formatSavings(20000, 20000);
      expect(result.amount).toBe(0);
      expect(result.color).toBe('warning');
      expect(result.text).toBe('At asking price');
    });
  });

  describe('formatTimestamp', () => {
    it('should format timestamps as time strings', () => {
      const date = new Date('2024-01-15T14:30:00Z');
      const formatted = formatTimestamp(date);
      // Note: Result depends on locale/timezone, just check it's a string
      expect(typeof formatted).toBe('string');
      expect(formatted.length).toBeGreaterThan(0);
    });
  });

  describe('formatFullTimestamp', () => {
    it('should format timestamps as full date and time', () => {
      const date = new Date('2024-01-15T14:30:00Z');
      const formatted = formatFullTimestamp(date);
      expect(typeof formatted).toBe('string');
      expect(formatted).toContain('at');
    });
  });
});
