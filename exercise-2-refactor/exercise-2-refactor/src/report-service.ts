// Report Service — generates summary reports
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

export interface ReportConfig {
  title: string;
  startDate: Date;
  endDate: Date;
  recipientEmail: string;
  totalRevenue: number;
}

export function generateReport(config: ReportConfig): string {
  if (!validateEmail(config.recipientEmail)) {
    throw new Error(`Invalid recipient email: ${config.recipientEmail}`);
  }

  const lines = [
    `Report: ${config.title}`,
    `Period: ${formatDate(config.startDate)} to ${formatDate(config.endDate)}`,
    `Revenue: ${formatPrice(config.totalRevenue)}`,
    `Recipient: ${config.recipientEmail}`,
  ];

  return lines.join('\n');
}
