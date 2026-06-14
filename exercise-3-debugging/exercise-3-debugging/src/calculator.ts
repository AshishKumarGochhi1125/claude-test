/**
 * Calculator module
 *
 * A simple arithmetic library with add, subtract, multiply, and divide.
 *
 * BUG: The divide function has a bug — it throws a generic Error
 * instead of the custom DivisionByZeroError when dividing by zero.
 * The test suite catches this because it checks for the specific error type.
 */

export class DivisionByZeroError extends Error {
  constructor(message: string = 'Cannot divide by zero') {
    super(message);
    this.name = 'DivisionByZeroError';
  }
}

export function add(a: number, b: number): number {
  return a + b;
}

export function subtract(a: number, b: number): number {
  return a - b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}

/**
 * Divides a by b.
 * Should throw DivisionByZeroError when b is 0.
 *
 * BUG: Currently throws generic Error instead of DivisionByZeroError.
 */
export function divide(a: number, b: number): number {
  if (b === 0) {
    // BUG: This should be `throw new DivisionByZeroError()`
    // but it throws a generic Error instead
    throw new Error('Cannot divide by zero');
  }
  return a / b;
}
