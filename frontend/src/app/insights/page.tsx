"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import api from "@/lib/api";
import type { Recommendation, Forecast } from "@/types";
import { formatPercent, formatCurrency, timeAgo, getStatusColor, getStatusBg } from "@/lib/utils";

const PRIORITY_COLORS = {
  critical: "border-rose-500/30 bg-rose-500/5",
  high: "border-amber-500/30 bg-amber-500/5",
  medium: "border-blue-500/30 bg-blue-500/5",
  low: "border-slate-500/30 bg-slate-500/5",
};

const PRIORITY_TEXT = {
  critical: "text-rose-400",
  high: "text-amber-400",
  medium: "text-blue-400",
  low: "text-slate-400",
};

export default function InsightsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedRec, setExpandedRec] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [recs, fcs] = await Promise.all([
          api.getRecommendations(),
          api.getForecasts(),
        ]);
        setRecommendations(recs);
        setForecasts(fcs);
      } catch {
        // Demo data
        setRecommendations([
          { id: "1", agent_name: "demand_forecast", type: "alert", title: "Restock Wireless Headphones", description: "Stock levels at 3 stores are below safety threshold. Immediate restock recommended to prevent stockout.", reason: "Current stock is below reorder point across Manhattan, LA, and Seattle stores. Forecasted demand exceeds available supply within the next 3 days. Historical analysis shows 95% probability of stockout without action.", confidence_score: 0.93, factors_used: { low_stock: 0.85, high_demand: 0.72, seasonal_trend: 0.45, historical_pattern: 0.88 }, priority: "critical", status: "pending", estimated_cost: 2400, estimated_savings: 18500, estimated_revenue_impact: 24000, created_at: new Date(Date.now() - 3600000).toISOString() },
          { id: "2", agent_name: "warehouse_agent", type: "transfer", title: "Transfer Apparel Stock: West → Midwest", description: "West Coast warehouses are overstocked on apparel while Midwest stores show increasing demand.", reason: "Inventory imbalance detected. West Coast utilization at 92% while Midwest at 58%. Transfer would optimize both regions.", confidence_score: 0.87, factors_used: { utilization_gap: 0.78, demand_trend: 0.65, shipping_cost: 0.42 }, priority: "high", status: "pending", estimated_cost: 1800, estimated_savings: 8500, estimated_revenue_impact: 12000, created_at: new Date(Date.now() - 7200000).toISOString() },
          { id: "3", agent_name: "store_agent", type: "optimize", title: "Adjust Safety Stock: Groceries Category", description: "Current safety stock levels for groceries are too conservative, tying up capital unnecessarily.", reason: "Analysis of 90 days of sales data shows actual demand variance is 30% lower than safety stock assumptions.", confidence_score: 0.81, factors_used: { demand_variance: 0.72, carrying_cost: 0.68, service_level: 0.85 }, priority: "medium", status: "pending", estimated_cost: 0, estimated_savings: 5200, estimated_revenue_impact: 0, created_at: new Date(Date.now() - 14400000).toISOString() },
          { id: "4", agent_name: "orchestrator", type: "alert", title: "Seasonal Preparation: Winter Sports", description: "Winter sports equipment demand expected to surge in 3 weeks based on historical patterns.", reason: "Multi-year seasonal analysis shows 2.8x demand increase for Sports/Outdoor category starting November. Pre-positioning inventory now would reduce emergency shipping by 40%.", confidence_score: 0.76, factors_used: { seasonality: 0.92, weather_forecast: 0.65, historical_sales: 0.88, current_stock: 0.55 }, priority: "medium", status: "pending", estimated_cost: 4500, estimated_savings: 12000, estimated_revenue_impact: 35000, created_at: new Date(Date.now() - 28800000).toISOString() },
        ]);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Prepare chart data from factors
  const getFactorChartData = (factors: Record<string, number> | null) => {
    if (!factors) return [];
    return Object.entries(factors).map(([key, value]) => ({
      factor: key.replace(/_/g, " "),
      influence: Math.round(value * 100),
    }));
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-3xl font-bold"><span className="gradient-text">AI Insights</span></h1>
        <p className="text-sm text-slate-400 mt-1">Explainable AI — understand every decision</p>
      </motion.div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Pending Actions", value: recommendations.filter(r => r.status === "pending").length, color: "text-amber-400" },
          { label: "Avg Confidence", value: `${formatPercent(recommendations.reduce((a, r) => a + r.confidence_score, 0) / Math.max(recommendations.length, 1) * 100)}`, color: "text-emerald-400" },
          { label: "Potential Savings", value: formatCurrency(recommendations.reduce((a, r) => a + (r.estimated_savings || 0), 0)), color: "text-cyan-400" },
          { label: "Revenue at Risk", value: formatCurrency(recommendations.reduce((a, r) => a + (r.estimated_revenue_impact || 0), 0)), color: "text-rose-400" },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-4 text-center"
          >
            <p className="text-xs text-slate-500 uppercase tracking-wider">{stat.label}</p>
            <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Recommendations */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">AI Recommendations</h3>
        {recommendations.map((rec, i) => (
          <motion.div
            key={rec.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            className={`glass-card overflow-hidden border ${PRIORITY_COLORS[rec.priority as keyof typeof PRIORITY_COLORS] || ""}`}
          >
            {/* Header */}
            <div
              className="p-5 cursor-pointer"
              onClick={() => setExpandedRec(expandedRec === rec.id ? null : rec.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`text-xs px-2.5 py-1 rounded-full font-semibold uppercase tracking-wider ${PRIORITY_TEXT[rec.priority as keyof typeof PRIORITY_TEXT]} bg-current/10`}
                      style={{ background: rec.priority === "critical" ? "rgba(244,63,94,0.1)" : rec.priority === "high" ? "rgba(245,158,11,0.1)" : "rgba(59,130,246,0.1)" }}>
                      {rec.priority}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-500">{rec.agent_name.replace("_", " ")}</span>
                    <span className="text-[10px] text-slate-600">{timeAgo(rec.created_at)}</span>
                  </div>
                  <h4 className="text-base font-semibold text-slate-200">{rec.title}</h4>
                  <p className="text-sm text-slate-400 mt-1">{rec.description}</p>
                </div>
                <div className="text-right ml-6 shrink-0">
                  <div className="w-14 h-14 rounded-full flex items-center justify-center border-2"
                    style={{
                      borderColor: rec.confidence_score > 0.85 ? "#10B981" : rec.confidence_score > 0.7 ? "#F59E0B" : "#64748B",
                      color: rec.confidence_score > 0.85 ? "#10B981" : rec.confidence_score > 0.7 ? "#F59E0B" : "#64748B",
                    }}>
                    <span className="text-sm font-bold">{Math.round(rec.confidence_score * 100)}%</span>
                  </div>
                </div>
              </div>

              {/* Financial Row */}
              <div className="flex gap-6 mt-4">
                {rec.estimated_cost !== null && rec.estimated_cost > 0 && (
                  <div className="text-xs"><span className="text-slate-500">Cost: </span><span className="text-rose-400 font-semibold">{formatCurrency(rec.estimated_cost ?? 0)}</span></div>
                )}
                {rec.estimated_savings !== null && rec.estimated_savings > 0 && (
                  <div className="text-xs"><span className="text-slate-500">Savings: </span><span className="text-emerald-400 font-semibold">{formatCurrency(rec.estimated_savings ?? 0)}</span></div>
                )}
                {rec.estimated_revenue_impact !== null && rec.estimated_revenue_impact > 0 && (
                  <div className="text-xs"><span className="text-slate-500">Revenue Impact: </span><span className="text-cyan-400 font-semibold">{formatCurrency(rec.estimated_revenue_impact ?? 0)}</span></div>
                )}
              </div>
            </div>

            {/* Expanded: "Why did AI decide this?" */}
            {expandedRec === rec.id && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="border-t border-white/5 p-5 bg-slate-900/30"
              >
                <h5 className="text-sm font-semibold text-blue-400 mb-3">💡 Why did the AI make this decision?</h5>
                <p className="text-sm text-slate-300 leading-relaxed mb-4 p-3 rounded-lg bg-slate-800/30 border border-white/5 italic">
                  &ldquo;{rec.reason}&rdquo;
                </p>

                {/* Factor Influence Chart */}
                {rec.factors_used && Object.keys(rec.factors_used).length > 0 && (
                  <div>
                    <h5 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">Decision Factors</h5>
                    <ResponsiveContainer width="100%" height={160}>
                      <BarChart data={getFactorChartData(rec.factors_used)} layout="vertical" margin={{ left: 80 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
                        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10, fill: "#64748B" }} unit="%" />
                        <YAxis dataKey="factor" type="category" tick={{ fontSize: 11, fill: "#94A3B8" }} width={80} />
                        <Tooltip
                          contentStyle={{ background: "#1A1F35", border: "1px solid rgba(148,163,184,0.1)", borderRadius: "8px", fontSize: "12px" }}
                          formatter={(value: any) => `${value}%`}
                        />
                        <Bar dataKey="influence" fill="#3B82F6" radius={[0, 6, 6, 0]} barSize={16}>
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 mt-4">
                  <button className="px-4 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold hover:bg-emerald-500/20 transition-colors cursor-pointer">
                    ✓ Accept
                  </button>
                  <button className="px-4 py-2 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold hover:bg-rose-500/20 transition-colors cursor-pointer">
                    ✕ Reject
                  </button>
                  <button className="px-4 py-2 rounded-lg bg-slate-500/10 border border-slate-500/30 text-slate-400 text-xs font-semibold hover:bg-slate-500/20 transition-colors cursor-pointer">
                    ↻ Re-analyze
                  </button>
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
