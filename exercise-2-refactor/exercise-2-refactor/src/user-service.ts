// User Service — manages user accounts
// Problem: This file duplicates utility functions found in other services

function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function validateEmail(email: string): boolean {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

function formatPrice(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
  balance: number;
}

export function createUser(name: string, email: string): User {
  if (!validateEmail(email)) {
    throw new Error(`Invalid email: ${email}`);
  }
  return {
    id: Math.random().toString(36).substring(2, 11),
    name,
    email,
    createdAt: new Date(),
    balance: 0,
  };
}

export function getUserSummary(user: User): string {
  return `${user.name} (${user.email}) — Joined: ${formatDate(user.createdAt)} — Balance: ${formatPrice(user.balance)}`;
}
