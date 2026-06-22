"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { 
  Search, Bell, HelpCircle, Calendar, Download, AlertTriangle, CheckCircle2,
  TrendingUp, Layers, Heart, Cpu, Lightbulb, Target, Activity, Play, ArrowRight
} from "lucide-react";
import api from "@/lib/api";
import type { DashboardData } from "@/types";
import { formatNumber, formatCurrency, timeAgo } from "@/lib/utils";

const CATEGORY_COLORS = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EF4444"];

const FORECAST_DATA = [
  { date: "Jun 15", predicted: 1200, actual: 1150 },
  { date: "Jun 16", predicted: 1450, actual: 1390 },
  { date: "Jun 17", predicted: 1300, actual: 1420 },
  { date: "Jun 18", predicted: 1700, actual: 1680 },
  { date: "Jun 19", predicted: 1600, actual: 1590 },
  { date: "Jun 20", predicted: 1900, actual: 1850 },
  { date: "Jun 21", predicted: 2100, actual: 2150 },
];

// ── Animated Counter ──
function AnimatedCounter({ value, duration = 1000, prefix = "", suffix = "", isDecimal = false }: {
  value: number; duration?: number; prefix?: string; suffix?: string; isDecimal?: boolean;
}) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const end = value;
    if (start === end) return;
    const increment = end / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(start);
      }
    }, 16);
    return () => clearInterval(timer);
  }, [value, duration]);
  
  const displayVal = isDecimal ? count.toFixed(1) : Math.floor(count).toLocaleString();
  return <span>{prefix}{displayVal}{suffix}</span>;
}

// ── Mini Sparkline Chart ──
function Sparkline({ data, strokeColor, fillColor }: { data: number[]; strokeColor: string; fillColor: string }) {
  const chartData = data.map((val, idx) => ({ id: idx, value: val }));
  return (
    <div className="h-10 w-24 opacity-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 2, right: 2, left: 2, bottom: 2 }}>
          <defs>
            <linearGradient id={`sparkGrad-${strokeColor.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={fillColor} stopOpacity={0.25}/>
              <stop offset="95%" stopColor={fillColor} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <Area 
            type="monotone" 
            dataKey="value" 
            stroke={strokeColor} 
            strokeWidth={1.5} 
            fill={`url(#sparkGrad-${strokeColor.replace('#', '')})`}
            dot={false} 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

// ── KPI Card Component ──
function KPICard({ 
  title, value, subtitle, icon, colorClass, delay, suffix = "", prefix = "", 
  trend = "", trendUp = true, sparkData, sparkStroke, sparkFill 
}: {
  title: string; value: number; subtitle: string; icon: React.ReactNode;
  colorClass: string; delay: number; suffix?: string; prefix?: string;
  trend?: string; trendUp?: boolean; sparkData: number[]; sparkStroke: string; sparkFill: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.08, duration: 0.4 }}
      className="enterprise-card flex flex-col justify-between h-[145px] group hover:-translate-y-1 hover:border-white/15 transition-all duration-300 relative overflow-hidden"
    >
      <div className="flex items-center justify-between text-slate-400">
        <span className="text-xs font-bold text-[#94A3B8]">{title}</span>
        <div className={`p-2 rounded-xl bg-[#0F172A] border border-white/8 ${colorClass}`}>
          {icon}
        </div>
      </div>
      
      <div className="my-1 flex items-baseline justify-between">
        <span className="text-[34px] font-extrabold text-white tracking-tight leading-none">
          <AnimatedCounter value={value} prefix={prefix} suffix={suffix} isDecimal={suffix === "%" || value % 1 !== 0} />
        </span>
        <Sparkline data={sparkData} strokeColor={sparkStroke} fillColor={sparkFill} />
      </div>
      
      <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
        <span className="flex items-center gap-1">
          <span className={`text-[10px] font-bold ${trendUp ? "text-emerald-400" : "text-[#F59E0B]"}`}>
            {trendUp ? "▲" : "▼"} {trend}
          </span>
          <span>{subtitle}</span>
        </span>
      </div>
    </motion.div>
  );
}

// ── Radial Progress for System Health ──
function RadialProgress({ percent, label, color }: { percent: number; label: string; color: string }) {
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percent / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center space-y-2">
      <div className="relative w-16 h-16 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="32" cy="32" r={radius} fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="4" />
          <circle 
            cx="32" 
            cy="32" 
            r={radius} 
            fill="none" 
            stroke={color} 
            strokeWidth="4" 
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <span className="absolute text-xs font-extrabold text-white">{percent}%</span>
      </div>
      <span className="text-[11px] text-[#94A3B8] font-bold tracking-tight text-center truncate w-full">{label}</span>
    </div>
  );
}

// ── World Map SVG representation ──
function WorldMap() {
  return (
    <div className="relative w-full h-[180px] flex items-center justify-center overflow-hidden rounded-xl border border-white/5 bg-[#0A0F1D] p-2">
      <svg viewBox="0 0 1000 500" className="w-full h-full opacity-30">
        {/* Abstract vector paths for continents */}
        {/* North America */}
        <path d="M120,80 C180,60 260,90 280,140 C290,160 300,190 260,230 C220,270 170,230 140,210 C120,190 80,180 80,150 C80,110 90,90 120,80 Z" fill="#475569" />
        {/* South America */}
        <path d="M250,250 C290,270 310,310 300,360 C290,410 270,470 240,480 C210,490 200,450 210,390 C220,330 220,290 250,250 Z" fill="#475569" />
        {/* Africa */}
        <path d="M460,210 C510,190 560,210 590,260 C610,290 620,330 590,380 C560,420 520,430 480,410 C450,390 440,330 440,290 C440,250 430,230 460,210 Z" fill="#475569" />
        {/* Europe / Asia */}
        <path d="M380,120 C420,100 480,90 520,80 C570,70 650,60 740,80 C820,90 880,110 900,160 C910,210 880,260 810,270 C740,280 660,250 580,240 C520,230 440,200 420,170 C400,150 360,140 380,120 Z" fill="#475569" />
        {/* Australia */}
        <path d="M780,340 C830,350 850,380 840,410 C830,440 790,450 760,440 C730,430 730,390 750,360 C760,340 770,330 780,340 Z" fill="#475569" />
        {/* Greenland */}
        <path d="M300,40 C340,30 380,50 370,70 C350,90 310,90 290,80 C270,70 270,50 300,40 Z" fill="#475569" />
      </svg>

      {/* Heatmap overlay dots */}
      {/* North America (Critical - Red) */}
      <div className="absolute top-[28%] left-[22%]">
        <span className="flex h-5 w-5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-5 w-5 bg-rose-500 border border-white/20" />
        </span>
      </div>
      <div className="absolute top-[34%] left-[17%]">
        <span className="flex h-3.5 w-3.5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-rose-500" />
        </span>
      </div>

      {/* Europe (Medium - Orange) */}
      <div className="absolute top-[24%] left-[49%]">
        <span className="flex h-4 w-4 relative">
          <span className="relative inline-flex rounded-full h-4 w-4 bg-amber-500 border border-white/20" />
        </span>
      </div>

      {/* East Asia (Critical - Red) */}
      <div className="absolute top-[28%] left-[78%]">
        <span className="flex h-5 w-5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-5 w-5 bg-rose-500 border border-white/20" />
        </span>
      </div>

      {/* South America (Low - Green) */}
      <div className="absolute top-[68%] left-[25%]">
        <span className="flex h-3.5 w-3.5 relative">
          <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500" />
        </span>
      </div>
      
      {/* Vertical Legend on Right */}
      <div className="absolute right-3 top-3 bottom-3 flex flex-col justify-between text-[9px] font-bold text-[#94A3B8] bg-[#0F172A]/80 border border-white/5 p-2 rounded-lg">
        <span className="text-[8px] text-slate-500 uppercase tracking-widest leading-none mb-1">Risk Level</span>
        <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-rose-500" /> High</div>
        <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-amber-500" /> Medium</div>
        <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Low</div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const loadDashboard = useCallback(async () => {
    try {
      const result = await api.getDashboard();
      setData(result);
    } catch (err) {
      console.error("Failed to load dashboard:", err);
      // Fallback data for demo / hackathon presentation
      setData({
        stats: {
          total_inventory: 124500,
          total_products: 50,
          total_stores: 10,
          total_warehouses: 5,
          predicted_demand_7d: 8240,
          predicted_demand_30d: 34500,
          stockout_risk_percent: 12.4,
          inventory_health_score: 78.6,
          active_shipments: 23,
          active_agent_decisions: 36,
          pending_recommendations: 12,
          total_inventory_value: 2840000,
          carbon_footprint: 1120,
        },
        inventory_by_category: [
          { category: "Electronics", total_quantity: 32500, product_count: 10, health_score: 85, value: 1250000 },
          { category: "Groceries", total_quantity: 41200, product_count: 10, health_score: 79, value: 385000 },
          { category: "Apparel", total_quantity: 28300, product_count: 10, health_score: 81, value: 520000 },
          { category: "Home", total_quantity: 15800, product_count: 10, health_score: 88, value: 410000 },
          { category: "Sports", total_quantity: 9800, product_count: 10, health_score: 83, value: 280000 },
        ],
        region_risks: [
          { region: "Northeast", store_count: 2, avg_health_score: 82, stockout_risk: 8.5, critical_items: 3 },
          { region: "West", store_count: 3, avg_health_score: 76, stockout_risk: 15.2, critical_items: 7 },
          { region: "South", store_count: 3, avg_health_score: 80, stockout_risk: 10.1, critical_items: 4 },
          { region: "Midwest", store_count: 2, avg_health_score: 74, stockout_risk: 18.3, critical_items: 6 },
        ],
        recent_agent_events: [
          { id: "1", agent_name: "demand_forecast", event_type: "decision", severity: "info", title: "Demand spike predicted for Electronics in West region", description: null, reasoning: null, payload: null, confidence_score: 0.91, timestamp: new Date(Date.now() - 120000).toISOString() },
          { id: "2", agent_name: "store_agent", event_type: "alert", severity: "warning", title: "Low stock alert: Wireless Headphones at LA Store", description: null, reasoning: null, payload: null, confidence_score: 0.88, timestamp: new Date(Date.now() - 300000).toISOString() },
          { id: "3", agent_name: "warehouse_agent", event_type: "recommendation", severity: "info", title: "Restock request processed: 200 units to NYC Store", description: null, reasoning: null, payload: null, confidence_score: 0.85, timestamp: new Date(Date.now() - 720000).toISOString() },
          { id: "4", agent_name: "supplier_agent", event_type: "alert", severity: "critical", title: "Supplier delay detected: Acme Corp (3 days)", description: null, reasoning: null, payload: null, confidence_score: 0.78, timestamp: new Date(Date.now() - 1080000).toISOString() },
          { id: "5", agent_name: "logistics_agent", event_type: "decision", severity: "info", title: "Route optimization completed for 12 shipments", description: null, reasoning: null, payload: null, confidence_score: 0.94, timestamp: new Date(Date.now() - 1320000).toISOString() },
        ],
        recent_recommendations: [
          { id: "1", agent_name: "optimizer_agent", type: "restock", recommendation_type: "restock", title: "Restock Wireless Headphones", description: "", reason: "", status: "pending", estimated_cost: 0, estimated_revenue_impact: 0, priority: "high", confidence_score: 0.94, estimated_savings: 4200, factors_used: null, created_at: new Date(Date.now() - 7200000).toISOString() },
          { id: "2", agent_name: "logistics_agent", type: "transfer", recommendation_type: "transfer", title: "Consolidate Northeast Shipments", description: "", reason: "", status: "pending", estimated_cost: 0, estimated_revenue_impact: 0, priority: "medium", confidence_score: 0.88, estimated_savings: 1800, factors_used: null, created_at: new Date(Date.now() - 14400000).toISOString() },
          { id: "3", agent_name: "supplier_agent", type: "reorder", recommendation_type: "reorder", title: "Reroute AlliedGroup orders to backup supplier", description: "", reason: "", status: "pending", estimated_cost: 0, estimated_revenue_impact: 0, priority: "critical", confidence_score: 0.91, estimated_savings: 7500, factors_used: null, created_at: new Date(Date.now() - 21600000).toISOString() },
        ],
      } as any);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#0B1020]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl border-2 border-[#3B82F6]/30 border-t-[#3B82F6] animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-sm font-semibold">Initializing dashboard modules...</p>
        </div>
      </div>
    );
  }

  const stats = data?.stats;

  return (
    <div className="px-8 py-8 space-y-6 bg-[#0B1020] min-h-screen text-gray-100 overflow-x-hidden">
      
      {/* ── STICKY TOP NAVIGATION BAR ── */}
      <header className="sticky top-0 z-40 bg-[#0B1020]/90 backdrop-blur-md border-b border-white/8 pb-4 mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-[36px] font-extrabold tracking-tight text-white leading-tight">Dashboard</h1>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Real-time overview of your AI-powered supply chain</p>
        </div>
        
        {/* Search, Notifications, help & Profile */}
        <div className="flex items-center gap-4 flex-wrap md:flex-nowrap">
          <div className="relative w-full md:w-[260px]">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#111827] border border-white/8 rounded-xl pl-9 pr-4 py-2 text-xs text-gray-300 focus:outline-none focus:border-[#3B82F6] focus:ring-1 focus:ring-[#3B82F6]/30 transition-all placeholder-slate-600"
            />
            <span className="absolute right-3 top-2 text-[10px] text-slate-500 bg-[#0B1020] px-1.5 py-0.5 rounded border border-white/8">
              ⌘K
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Notification Badge */}
            <button className="relative p-2 bg-[#111827] hover:bg-white/5 rounded-xl border border-white/8 text-slate-400 hover:text-white transition-colors cursor-pointer">
              <Bell className="h-4.5 w-4.5" />
              <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-[#EF4444] text-[9px] font-bold text-white flex items-center justify-center ring-2 ring-[#0B1020]">
                12
              </span>
            </button>

            {/* Help */}
            <button className="p-2 bg-[#111827] hover:bg-white/5 rounded-xl border border-white/8 text-slate-400 hover:text-white transition-colors cursor-pointer">
              <HelpCircle className="h-4.5 w-4.5" />
            </button>

            {/* Avatar */}
            <div className="h-8 w-8 rounded-full bg-[#3B82F6] flex items-center justify-center font-bold text-xs text-white shadow-sm border border-white/10">
              A
            </div>

            {/* Date Range Picker */}
            <button className="flex items-center gap-2 bg-[#111827] hover:bg-white/5 border border-white/8 rounded-xl px-3.5 py-2 text-xs font-bold text-slate-300 transition-colors cursor-pointer">
              <Calendar className="h-4 w-4 text-slate-400" />
              <span>Jun 15 - Jun 21, 2025</span>
            </button>

            {/* Export Button */}
            <button className="flex items-center gap-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-bold px-4 py-2 rounded-xl transition-all shadow-md shadow-blue-500/10 cursor-pointer">
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </header>

      {/* ── ROW 1: KPI CARDS ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Inventory Value"
          value={stats?.total_inventory_value || 0}
          subtitle="vs last 7 days"
          icon={<Layers className="h-4.5 w-4.5" />}
          colorClass="text-[#3B82F6]"
          delay={0}
          prefix="$"
          trend="8.6%"
          trendUp={true}
          sparkData={[2.1, 2.3, 2.2, 2.5, 2.6, 2.8, 2.84]}
          sparkStroke="#3B82F6"
          sparkFill="#3B82F6"
        />
        <KPICard
          title="Predicted Demand (7D)"
          value={stats?.predicted_demand_7d || 0}
          subtitle="vs last 7 days"
          icon={<TrendingUp className="h-4.5 w-4.5" />}
          colorClass="text-[#8B5CF6]"
          delay={1}
          trend="12.4%"
          trendUp={true}
          sparkData={[7.5, 7.8, 8.0, 7.9, 8.2, 8.3, 8.42]}
          sparkStroke="#8B5CF6"
          sparkFill="#8B5CF6"
        />
        <KPICard
          title="Stockout Risk"
          value={stats?.stockout_risk_percent || 0}
          subtitle="vs last 7 days"
          icon={<AlertTriangle className="h-4.5 w-4.5" />}
          colorClass="text-[#F59E0B]"
          delay={2}
          suffix="%"
          trend="5.2%"
          trendUp={false}
          sparkData={[15.4, 14.8, 13.9, 14.2, 13.1, 12.8, 12.4]}
          sparkStroke="#F59E0B"
          sparkFill="#F59E0B"
        />
        <KPICard
          title="Inventory Health Score"
          value={stats?.inventory_health_score || 0}
          subtitle="vs last 7 days"
          icon={<Heart className="h-4.5 w-4.5" />}
          colorClass="text-[#10B981]"
          delay={3}
          suffix=" /100"
          trend="6.3%"
          trendUp={true}
          sparkData={[72, 74, 73, 76, 75, 77, 78.6]}
          sparkStroke="#10B981"
          sparkFill="#10B981"
        />
      </div>

      {/* ── ROW 2: DEMAND FORECAST & CATEGORY DOUGHNUT ── */}
      <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
        {/* Demand Forecast Chart (70%) */}
        <div className="enterprise-card lg:col-span-7 flex flex-col justify-between min-h-[380px]">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Demand Forecast</h3>
            </div>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-4 text-xs font-bold text-[#94A3B8]">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#3B82F6] shadow-sm shadow-blue-500/50" /> Predicted
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#10B981] shadow-sm shadow-emerald-500/50" /> Actual
                </span>
              </div>
              <select className="bg-[#0B1020] border border-white/8 text-slate-300 text-xs font-bold rounded-xl px-2.5 py-1 focus:outline-none cursor-pointer">
                <option>7 Days</option>
                <option>30 Days</option>
              </select>
            </div>
          </div>
          
          <div className="flex-1 h-[260px] min-h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={FORECAST_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="predictedGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.03)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: "#64748B", fontSize: 10, fontWeight: 600 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: "#64748B", fontSize: 10, fontWeight: 600 }} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#111827", borderColor: "rgba(255,255,255,0.08)", borderRadius: "12px", fontSize: "12px", color: "#FFFFFF" }}
                />
                <Area type="monotone" dataKey="predicted" stroke="#3B82F6" strokeWidth={2} fill="url(#predictedGrad)" fillOpacity={1} dot={false} activeDot={{ r: 4 }} />
                <Area type="monotone" dataKey="actual" stroke="#10B981" strokeWidth={2} fill="transparent" dot={{ r: 3, fill: "#10B981" }} activeDot={{ r: 4 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown (30%) */}
        <div className="enterprise-card lg:col-span-3 flex flex-col justify-between min-h-[380px]">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Inventory by Category</h3>
          </div>
          
          {/* Doughnut Chart */}
          <div className="h-[180px] flex items-center justify-center relative my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data?.inventory_by_category || []}
                  dataKey="total_quantity"
                  nameKey="category"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={4}
                  strokeWidth={0}
                >
                  {(data?.inventory_by_category || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${formatNumber(Number(value))} units`} />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-2xl font-extrabold text-white tracking-tight leading-none">127.5K</span>
              <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-1">Total Units</span>
            </div>
          </div>
          
          <div className="space-y-1.5 text-[11px] text-slate-400 mt-2">
            {(data?.inventory_by_category || []).map((cat, idx) => {
              const totalUnits = (data?.inventory_by_category || []).reduce((acc, c) => acc + c.total_quantity, 0) || 1;
              const percent = ((cat.total_quantity / totalUnits) * 100).toFixed(1);
              return (
                <div key={cat.category} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full min-w-2" style={{ backgroundColor: CATEGORY_COLORS[idx % CATEGORY_COLORS.length] }} />
                    <span className="font-semibold text-slate-300">{cat.category}</span>
                  </div>
                  <span className="text-[#94A3B8] font-bold">{(cat.total_quantity / 1000).toFixed(1)}K ({percent}%)</span>
                </div>
              );
            })}
            <div className="border-t border-white/5 pt-2 mt-1 text-center">
              <Link href="/inventory" className="text-xs text-[#3B82F6] hover:text-blue-400 font-bold transition-colors inline-flex items-center gap-1">
                View full breakdown <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* ── ROW 3: HEATMAP, TIMELINE & ALERTS ── */}
      <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
        {/* Risk Heatmap (35% or col-span-3.5) */}
        <div className="enterprise-card lg:col-span-3 flex flex-col justify-between min-h-[350px]">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Risk Heatmap by Region</h3>
          </div>
          <WorldMap />
          <p className="text-[10px] text-slate-500 font-medium">Autonomous global supply chain risk tracker</p>
        </div>

        {/* Agent Activity Timeline (35% or col-span-4) */}
        <div className="enterprise-card lg:col-span-4 flex flex-col justify-between min-h-[350px]">
          <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-2">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Agent Activity</h3>
            <Link href="/agents" className="text-xs text-[#3B82F6] hover:text-blue-400 font-bold transition-colors">View all →</Link>
          </div>

          <div className="flex-1 overflow-y-auto max-h-[220px] space-y-4 pr-1 relative pl-6 border-l border-white/8 ml-2 mt-2">
            {data?.recent_agent_events.slice(0, 5).map((event, idx) => {
              const iconMap: Record<string, string> = {
                demand_forecast: "📈",
                store_agent: "🏪",
                warehouse_agent: "🏭",
                supplier_agent: "🤝",
                logistics_agent: "🚚",
                orchestrator: "🎯",
              };
              return (
                <div key={idx} className="relative group">
                  <div className="absolute -left-[31px] top-0.5 w-5 h-5 rounded-full bg-[#111827] border border-white/10 flex items-center justify-center text-[10px] group-hover:border-[#3B82F6] transition-colors shadow-sm">
                    {iconMap[event.agent_name || ""] || "🤖"}
                  </div>
                  
                  <div className="flex items-start justify-between gap-4 hover:bg-white/3 p-1.5 rounded-xl transition-colors">
                    <div className="space-y-0.5">
                      <p className="text-xs text-white font-semibold leading-normal">{event.title}</p>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">
                        {(event.agent_name || "Agent").replace("_", " ")} • {event.timestamp ? timeAgo(event.timestamp) : "just now"}
                      </p>
                    </div>
                    {event.confidence_score && (
                      <span className="text-[9px] px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full font-bold whitespace-nowrap">
                        {Math.round(event.confidence_score * 100)}% confident
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Alerts Card (30% or col-span-3) */}
        <div className="enterprise-card lg:col-span-3 flex flex-col justify-between min-h-[350px]">
          <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-2">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Top Alerts</h3>
            <Link href="/alerts" className="text-xs text-[#3B82F6] hover:text-blue-400 font-bold transition-colors">View all →</Link>
          </div>

          <div className="flex-1 space-y-2.5 mt-2">
            {/* Alert 1 */}
            <div className="flex items-start gap-3 p-2.5 bg-[#0F172A] border border-white/5 rounded-xl">
              <div className="p-2 bg-amber-500/10 rounded-lg text-amber-400">
                <AlertTriangle className="h-4 w-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">High stockout risk for 15 SKUs</p>
                <p className="text-[10px] text-slate-500 mt-0.5">West region • 12m ago</p>
              </div>
            </div>
            {/* Alert 2 */}
            <div className="flex items-start gap-3 p-2.5 bg-[#0F172A] border border-white/5 rounded-xl">
              <div className="p-2 bg-amber-500/10 rounded-lg text-amber-400">
                <AlertTriangle className="h-4 w-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">Supplier delay expected</p>
                <p className="text-[10px] text-slate-500 mt-0.5">Acme Corp • 18m ago</p>
              </div>
            </div>
            {/* Alert 3 */}
            <div className="flex items-start gap-3 p-2.5 bg-[#0F172A] border border-white/5 rounded-xl">
              <div className="p-2 bg-rose-500/10 rounded-lg text-rose-400">
                <AlertTriangle className="h-4 w-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">Warehouse capacity at 92%</p>
                <p className="text-[10px] text-slate-500 mt-0.5">Chicago DC • 32m ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── ROW 4: FINANCIAL OVERVIEW ── */}
      <div className="enterprise-card min-h-[340px] flex flex-col justify-between">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Financial Overview</h3>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex gap-4 text-xs font-semibold text-[#94A3B8]">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#3B82F6]" /> Revenue</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#8B5CF6]" /> Cost</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#10B981]" /> Margin</span>
            </div>
            <select className="bg-[#0B1020] border border-white/8 text-slate-300 text-xs font-bold rounded-xl px-2.5 py-1 focus:outline-none cursor-pointer">
              <option>7 Days</option>
              <option>30 Days</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 border-b border-white/5 pb-4 mb-4">
          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-extrabold block">Total Revenue</span>
            <span className="text-xl font-extrabold text-white mt-1 block">$1.42M</span>
            <span className="text-[10px] text-emerald-400 font-bold">▲ 11.6% vs last week</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-extrabold block">Total Cost</span>
            <span className="text-xl font-extrabold text-white mt-1 block">$940K</span>
            <span className="text-[10px] text-emerald-400 font-bold">▲ 6.3% vs last week</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-extrabold block">Gross Margin</span>
            <span className="text-xl font-extrabold text-white mt-1 block">34.1%</span>
            <span className="text-[10px] text-emerald-400 font-bold">▲ 3.1% vs last week</span>
          </div>
        </div>

        <div className="h-[200px] my-3">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data?.inventory_by_category || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.03)" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="category" tick={{ fill: "#64748B", fontSize: 10, fontWeight: 600 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: "#64748B", fontSize: 10, fontWeight: 600 }} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: "#111827", borderColor: "rgba(255,255,255,0.08)", borderRadius: "12px", fontSize: "12px", color: "#FFFFFF" }}
                formatter={(value) => [formatCurrency(Number(value)), "Value"]} 
              />
              <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Revenue" />
              <Bar dataKey="total_quantity" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="Cost" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── ROW 5: SIMULATIONS & SYSTEM HEALTH ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recent Simulations */}
        <div className="enterprise-card min-h-[290px] flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-white/5 pb-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400" /> Recent Simulations
            </h4>
            <Link href="/simulation" className="text-xs text-[#3B82F6] hover:text-blue-400 font-bold transition-colors">View all →</Link>
          </div>
          
          <div className="space-y-2 overflow-y-auto max-h-[180px] pr-1 mt-3">
            <div className="p-3 bg-[#0F172A] border border-white/5 rounded-xl flex items-center justify-between text-xs">
              <div>
                <p className="font-semibold text-gray-200">Demand Spike — Electronics</p>
                <p className="text-[10px] text-slate-500">Jun 21, 2025 10:30 AM</p>
              </div>
              <span className="text-[9px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Completed</span>
            </div>
            <div className="p-3 bg-[#0F172A] border border-white/5 rounded-xl flex items-center justify-between text-xs">
              <div>
                <p className="font-semibold text-gray-200">Supplier Strike — Acme Corp</p>
                <p className="text-[10px] text-slate-500">Jun 21, 2025 09:15 AM</p>
              </div>
              <span className="text-[9px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Completed</span>
            </div>
            <div className="p-3 bg-[#0F172A] border border-white/5 rounded-xl flex items-center justify-between text-xs">
              <div>
                <p className="font-semibold text-gray-200">Warehouse Shutdown — West DC</p>
                <p className="text-[10px] text-slate-500">Jun 20, 2025 04:45 PM</p>
              </div>
              <span className="text-[9px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Completed</span>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="enterprise-card min-h-[290px] flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-white/5 pb-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-widest">System Health</h4>
            <Link href="/settings" className="text-xs text-[#3B82F6] hover:text-blue-400 font-bold transition-colors">View system status →</Link>
          </div>
          
          <div className="grid grid-cols-4 gap-4 py-4">
            <RadialProgress percent={98} label="Agents" color="#10B981" />
            <RadialProgress percent={96} label="Data Pipeline" color="#3B82F6" />
            <RadialProgress percent={94} label="Integrations" color="#8B5CF6" />
            <RadialProgress percent={99} label="Infrastructure" color="#F59E0B" />
          </div>
        </div>
      </div>

    </div>
  );
}
