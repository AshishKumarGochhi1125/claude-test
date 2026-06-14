import { describe, it, expect } from 'vitest';
import { add, subtract, multiply, divide, DivisionByZeroError } from './calculator';

describe('Calculator', () => {
  describe('add', () => {
    it('adds two positive numbers', () => {
      expect(add(2, 3)).toBe(5);
    });

    it('adds negative numbers', () => {
      expect(add(-1, -2)).toBe(-3);
    });

    it('adds zero', () => {
      expect(add(5, 0)).toBe(5);
    });
  });

  describe('subtract', () => {
    it('subtracts two numbers', () => {
      expect(subtract(10, 3)).toBe(7);
    });

    it('handles negative results', () => {
      expect(subtract(3, 10)).toBe(-7);
    });
  });

  describe('multiply', () => {
    it('multiplies two numbers', () => {
      expect(multiply(4, 5)).toBe(20);
    });

    it('multiplies by zero', () => {
      expect(multiply(100, 0)).toBe(0);
    });

    it('multiplies negative numbers', () => {
      expect(multiply(-3, 4)).toBe(-12);
    });
  });

  describe('divide', () => {
    it('divides two numbers', () => {
      expect(divide(10, 2)).toBe(5);
    });

    it('handles decimal results', () => {
      expect(divide(7, 2)).toBe(3.5);
    });

    it('divides negative numbers', () => {
      expect(divide(-10, 2)).toBe(-5);
    });

    // THIS TEST FAILS — divide() throws generic Error, not DivisionByZeroError
    it('throws DivisionByZeroError when dividing by zero', () => {
      expect(() => divide(5, 0)).toThrow(DivisionByZeroError);
    });

    // THIS TEST ALSO FAILS — same root cause
    it('throws DivisionByZeroError with correct message', () => {
      expect(() => divide(0, 0)).toThrow('Cannot divide by zero');
      expect(() => divide(0, 0)).toThrow(DivisionByZeroError);
    });
  });
});
