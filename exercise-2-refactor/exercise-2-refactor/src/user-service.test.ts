import { describe, it, expect } from 'vitest';
import { createUser, getUserSummary } from './user-service';

describe('UserService', () => {
  it('should create a user with valid email', () => {
    const user = createUser('Alice', 'alice@example.com');
    expect(user.name).toBe('Alice');
    expect(user.email).toBe('alice@example.com');
    expect(user.balance).toBe(0);
  });

  it('should throw on invalid email', () => {
    expect(() => createUser('Bob', 'not-an-email')).toThrow('Invalid email');
  });

  it('should generate a user summary', () => {
    const user = createUser('Alice', 'alice@example.com');
    const summary = getUserSummary(user);
    expect(summary).toContain('Alice');
    expect(summary).toContain('alice@example.com');
    expect(summary).toContain('$0.00');
  });
});
