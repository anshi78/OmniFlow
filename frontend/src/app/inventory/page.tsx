"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import api from "@/lib/api";
import type { InventoryItem } from "@/types";
import { formatNumber, getStatusColor, getStatusBg, formatPercent } from "@/lib/utils";

const STATUS_OPTIONS = ["all", "normal", "low", "critical", "overstock"];
const LOCATION_OPTIONS = ["all", "store", "warehouse"];

export default function InventoryPage() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [locationFilter, setLocationFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [categories, setCategories] = useState<string[]>([]);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [inv, cats] = await Promise.all([
        api.getInventory({
          status: statusFilter !== "all" ? statusFilter : undefined,
          location_type: locationFilter !== "all" ? locationFilter : undefined,
          category: categoryFilter !== "all" ? categoryFilter : undefined,
          search: search || undefined,
        }),
        api.getProductCategories(),
      ]);
      setInventory(inv);
      setCategories(cats);
    } catch (err) {
      console.error("Failed to load inventory:", err);
      // Fallback demo data
      setInventory([
        { id: "1", product_id: "p1", store_id: "s1", warehouse_id: null, location_type: "store", quantity: 45, reserved_quantity: 5, safety_stock: 50, reorder_point: 100, max_stock: 500, daily_sales_avg: 12.5, days_of_supply: 3.6, status: "critical", last_restocked: null, last_updated: new Date().toISOString(), product_name: "Wireless Headphones", product_sku: "ELEC-001", location_name: "OmniStore Manhattan", health_score: 22 },
        { id: "2", product_id: "p2", store_id: "s2", warehouse_id: null, location_type: "store", quantity: 85, reserved_quantity: 10, safety_stock: 40, reorder_point: 80, max_stock: 400, daily_sales_avg: 8.3, days_of_supply: 10.2, status: "low", last_restocked: null, last_updated: new Date().toISOString(), product_name: "Smart Watch Pro", product_sku: "ELEC-004", location_name: "OmniStore Los Angeles", health_score: 48 },
        { id: "3", product_id: "p3", store_id: null, warehouse_id: "w1", location_type: "warehouse", quantity: 2450, reserved_quantity: 200, safety_stock: 200, reorder_point: 500, max_stock: 8000, daily_sales_avg: 0, days_of_supply: 0, status: "normal", last_restocked: null, last_updated: new Date().toISOString(), product_name: "Premium Cotton T-Shirt", product_sku: "APRL-001", location_name: "East Coast Distribution Center", health_score: 78 },
        { id: "4", product_id: "p4", store_id: "s3", warehouse_id: null, location_type: "store", quantity: 320, reserved_quantity: 0, safety_stock: 30, reorder_point: 60, max_stock: 300, daily_sales_avg: 15.2, days_of_supply: 21.1, status: "overstock", last_restocked: null, last_updated: new Date().toISOString(), product_name: "Organic Quinoa 1kg", product_sku: "GROC-001", location_name: "OmniStore Chicago", health_score: 55 },
        { id: "5", product_id: "p5", store_id: "s4", warehouse_id: null, location_type: "store", quantity: 178, reserved_quantity: 20, safety_stock: 50, reorder_point: 100, max_stock: 600, daily_sales_avg: 6.7, days_of_supply: 26.6, status: "normal", last_restocked: null, last_updated: new Date().toISOString(), product_name: "Yoga Mat Premium", product_sku: "SPRT-001", location_name: "OmniStore Houston", health_score: 72 },
        { id: "6", product_id: "p6", store_id: "s5", warehouse_id: null, location_type: "store", quantity: 12, reserved_quantity: 0, safety_stock: 25, reorder_point: 50, max_stock: 300, daily_sales_avg: 9.1, days_of_supply: 1.3, status: "critical", last_restocked: null, last_updated: new Date().toISOString(), product_name: "4K Ultra HD Smart TV", product_sku: "ELEC-002", location_name: "OmniStore Phoenix", health_score: 12 },
      ]);
      setCategories(["Electronics", "Groceries", "Apparel", "Home", "Sports"]);
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, locationFilter, categoryFilter]);

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold"><span className="gradient-text">Inventory</span></h1>
          <p className="text-sm text-slate-400 mt-1">Track products across stores and warehouses</p>
        </div>
        <div className="text-xs text-slate-500">{inventory.length} items</div>
      </motion.div>

      {/* Filters */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        className="glass-card p-4 flex flex-wrap items-center gap-4">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800/50 text-sm text-slate-200 px-4 py-2.5 rounded-lg border border-white/5 focus:border-blue-500/50 focus:outline-none transition-colors placeholder:text-slate-600"
            id="inventory-search"
          />
        </div>
        {/* Status filter */}
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-800/50 text-sm text-slate-300 px-4 py-2.5 rounded-lg border border-white/5 focus:border-blue-500/50 focus:outline-none"
          id="status-filter">
          {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s === "all" ? "All Status" : s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
        </select>
        {/* Location filter */}
        <select value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)}
          className="bg-slate-800/50 text-sm text-slate-300 px-4 py-2.5 rounded-lg border border-white/5 focus:border-blue-500/50 focus:outline-none"
          id="location-filter">
          {LOCATION_OPTIONS.map(l => <option key={l} value={l}>{l === "all" ? "All Locations" : l.charAt(0).toUpperCase() + l.slice(1)}</option>)}
        </select>
        {/* Category filter */}
        <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}
          className="bg-slate-800/50 text-sm text-slate-300 px-4 py-2.5 rounded-lg border border-white/5 focus:border-blue-500/50 focus:outline-none"
          id="category-filter">
          <option value="all">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </motion.div>

      {/* Inventory Table */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
        className="glass-card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="w-8 h-8 rounded-full border-2 border-blue-500/30 border-t-blue-500 animate-spin" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left py-4 px-5 text-xs uppercase tracking-wider text-slate-500 font-semibold">Product</th>
                  <th className="text-left py-4 px-5 text-xs uppercase tracking-wider text-slate-500 font-semibold">Location</th>
                  <th className="text-right py-4 px-5 text-xs uppercase tracking-wider text-slate-500 font-semibold">Quantity</th>
                  <th className="text-right py-4 px-5 text-xs uppercase tracking-wider text-slate-500 font-semibold">Days Supply</th>
                  <th className="text-center py-4 px-5 text-xs uppercase tracking-wider text-slate-500 font-semibold">Health</th>
                  <th className="text-center py-4 px-5 text-xs uppercase tracking-wider text-slate-500 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map((item, i) => (
                  <motion.tr
                    key={item.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 + i * 0.05 }}
                    className="border-b border-white/3 hover:bg-white/2 transition-colors"
                  >
                    <td className="py-4 px-5">
                      <div>
                        <p className="text-slate-200 font-medium">{item.product_name || "Unknown"}</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">{item.product_sku}</p>
                      </div>
                    </td>
                    <td className="py-4 px-5">
                      <div>
                        <p className="text-slate-300 text-xs">{item.location_name || "—"}</p>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-500 mt-0.5 inline-block">
                          {item.location_type}
                        </span>
                      </div>
                    </td>
                    <td className="py-4 px-5 text-right">
                      <span className="text-slate-200 font-mono font-semibold">{formatNumber(item.quantity)}</span>
                      <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2">
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{
                            width: `${Math.min(100, (item.quantity / item.max_stock) * 100)}%`,
                            background: item.status === "critical" ? "#F43F5E"
                              : item.status === "low" ? "#F59E0B"
                              : item.status === "overstock" ? "#3B82F6"
                              : "#10B981",
                          }}
                        />
                      </div>
                    </td>
                    <td className="py-4 px-5 text-right">
                      <span className={`font-mono ${item.days_of_supply < 5 ? "text-rose-400" : item.days_of_supply < 10 ? "text-amber-400" : "text-slate-300"}`}>
                        {item.days_of_supply.toFixed(1)}d
                      </span>
                    </td>
                    <td className="py-4 px-5 text-center">
                      <div className="inline-flex items-center gap-1.5">
                        <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                          style={{
                            background: item.health_score > 70 ? "rgba(16,185,129,0.15)"
                              : item.health_score > 40 ? "rgba(245,158,11,0.15)"
                              : "rgba(244,63,94,0.15)",
                            color: item.health_score > 70 ? "#10B981"
                              : item.health_score > 40 ? "#F59E0B"
                              : "#F43F5E",
                          }}>
                          {Math.round(item.health_score)}
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-5 text-center">
                      <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${getStatusBg(item.status)} ${getStatusColor(item.status)}`}>
                        {item.status}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
}
