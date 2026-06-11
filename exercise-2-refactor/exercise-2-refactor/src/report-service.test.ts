import { describe, it, expect } from 'vitest';
import { generateReport } from './report-service';

describe('ReportService', () => {
  it('should generate a report', () => {
    const report = generateReport({
      title: 'Q1 Revenue',
      startDate: new Date('2025-01-01'),
      endDate: new Date('2025-03-31'),
      recipientEmail: 'boss@example.com',
      totalRevenue: 150000,
    });
    expect(report).toContain('Q1 Revenue');
    expect(report).toContain('2025-01-01');
    expect(report).toContain('$1,500.00');
  });

  it('should throw on invalid email', () => {
    expect(() =>
      generateReport({
        title: 'Test',
        startDate: new Date(),
        endDate: new Date(),
        recipientEmail: 'bad-email',
        totalRevenue: 0,
      })
    ).toThrow('Invalid recipient email');
  });
});
