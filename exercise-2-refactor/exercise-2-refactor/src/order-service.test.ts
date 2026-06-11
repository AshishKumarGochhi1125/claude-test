import { describe, it, expect } from 'vitest';
import { calculateOrderTotal, getOrderSummary, Order } from './order-service';

describe('OrderService', () => {
  const sampleOrder: Order = {
    id: 'ORD-001',
    items: [
      { name: 'Widget', quantity: 2, priceInCents: 1500 },
      { name: 'Gadget', quantity: 1, priceInCents: 3000 },
    ],
    createdAt: new Date('2025-01-15'),
    status: 'pending',
  };

  it('should calculate order total', () => {
    expect(calculateOrderTotal(sampleOrder.items)).toBe(6000);
  });

  it('should generate order summary', () => {
    const summary = getOrderSummary(sampleOrder);
    expect(summary).toContain('ORD-001');
    expect(summary).toContain('$60.00');
    expect(summary).toContain('pending');
  });
});
