// Order Service — manages customer orders
// Problem: This file duplicates utility functions found in other services

function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatPrice(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export interface OrderItem {
  name: string;
  quantity: number;
  priceInCents: number;
}

export interface Order {
  id: string;
  items: OrderItem[];
  createdAt: Date;
  status: 'pending' | 'shipped' | 'delivered';
}

export function calculateOrderTotal(items: OrderItem[]): number {
  return items.reduce((sum, item) => sum + item.priceInCents * item.quantity, 0);
}

export function getOrderSummary(order: Order): string {
  const total = calculateOrderTotal(order.items);
  return `Order ${order.id} — ${formatDate(order.createdAt)} — ${order.items.length} items — Total: ${formatPrice(total)} — ${order.status}`;
}
