/* OmniFlow AI — Utility functions */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toLocaleString();
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "normal":
    case "healthy":
    case "active":
    case "delivered":
      return "text-emerald-400";
    case "low":
    case "warning":
    case "in_transit":
    case "standby":
      return "text-amber-400";
    case "critical":
    case "error":
    case "delayed":
      return "text-rose-400";
    case "overstock":
      return "text-blue-400";
    default:
      return "text-slate-400";
  }
}

export function getStatusBg(status: string): string {
  switch (status) {
    case "normal":
    case "healthy":
    case "active":
      return "bg-emerald-500/10 border-emerald-500/20";
    case "low":
    case "warning":
    case "standby":
      return "bg-amber-500/10 border-amber-500/20";
    case "critical":
    case "error":
      return "bg-rose-500/10 border-rose-500/20";
    case "overstock":
      return "bg-blue-500/10 border-blue-500/20";
    default:
      return "bg-slate-500/10 border-slate-500/20";
  }
}

export function timeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export function getSeverityIcon(severity: string): string {
  switch (severity) {
    case "critical":
      return "🔴";
    case "warning":
      return "🟡";
    case "info":
      return "🔵";
    default:
      return "⚪";
  }
}
