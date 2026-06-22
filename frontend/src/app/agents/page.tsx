"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import api from "@/lib/api";
import type { Agent, AgentEvent, AgentGraphData } from "@/types";
import { timeAgo, getSeverityIcon, formatPercent } from "@/lib/utils";

const AGENT_COLORS: Record<string, string> = {
  orchestrator: "#3B82F6",
  demand_forecast: "#10B981",
  store_agent: "#F59E0B",
  warehouse_agent: "#8B5CF6",
  supplier_agent: "#06B6D4",
  logistics_agent: "#EC4899",
  trend_agent: "#F43F5E",
  optimizer_agent: "#14B8A6",
};

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [graphData, setGraphData] = useState<AgentGraphData | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [a, e, g] = await Promise.all([
          api.getAgentsStatus(),
          api.getAgentEvents({ limit: 30 }),
          api.getAgentGraph(),
        ]);
        setAgents(a);
        setEvents(e);
        setGraphData(g);
      } catch {
        // Fallback data
        setAgents([
          { id: "orchestrator", name: "Orchestrator Agent", description: "Coordinates all agents", status: "active", icon: "🎯", total_events: 45, last_activity: new Date(Date.now() - 120000).toISOString(), last_action: "Coordinated restock across 3 stores" },
          { id: "demand_forecast", name: "Demand Forecast Agent", description: "Predicts demand using ML", status: "active", icon: "📊", total_events: 82, last_activity: new Date(Date.now() - 300000).toISOString(), last_action: "Generated 7-day forecast for Electronics" },
          { id: "store_agent", name: "Store Agent", description: "Monitors store inventory", status: "active", icon: "🏪", total_events: 67, last_activity: new Date(Date.now() - 600000).toISOString(), last_action: "Low stock alert: NYC Store" },
          { id: "warehouse_agent", name: "Warehouse Agent", description: "Manages warehouse allocation", status: "active", icon: "🏭", total_events: 38, last_activity: new Date(Date.now() - 1800000).toISOString(), last_action: "Processed 5 restock requests" },
          { id: "supplier_agent", name: "Supplier Agent", description: "Monitors supplier reliability", status: "standby", icon: "🚚", total_events: 0, last_activity: null, last_action: null },
          { id: "logistics_agent", name: "Logistics Agent", description: "Route optimization", status: "standby", icon: "🗺️", total_events: 0, last_activity: null, last_action: null },
          { id: "trend_agent", name: "Trend Agent", description: "Social trend analysis", status: "standby", icon: "📈", total_events: 0, last_activity: null, last_action: null },
          { id: "optimizer_agent", name: "Optimizer Agent", description: "Dynamic safety stock", status: "standby", icon: "⚡", total_events: 0, last_activity: null, last_action: null },
        ]);
        setEvents([
          { id: "1", agent_name: "orchestrator", event_type: "decision", severity: "info", title: "Coordinated restock for West region", description: null, reasoning: "Multiple stores in West region approaching reorder points. Coordinated warehouse allocation to minimize shipping costs.", confidence_score: 0.92, payload: null, timestamp: new Date(Date.now() - 120000).toISOString() },
          { id: "2", agent_name: "demand_forecast", event_type: "alert", severity: "warning", title: "Demand spike predicted: Electronics Q4", description: null, reasoning: "Historical patterns and seasonal analysis indicate 2.5x demand surge for electronics in next 14 days.", confidence_score: 0.87, payload: null, timestamp: new Date(Date.now() - 300000).toISOString() },
          { id: "3", agent_name: "store_agent", event_type: "alert", severity: "critical", title: "Critical stock: Headphones at Manhattan store", description: null, reasoning: "Current stock 12 units, daily demand 15 units. Estimated stockout in less than 1 day.", confidence_score: 0.95, payload: null, timestamp: new Date(Date.now() - 600000).toISOString() },
          { id: "4", agent_name: "warehouse_agent", event_type: "decision", severity: "info", title: "Allocated 500 units to East Coast stores", description: null, reasoning: "Based on demand forecasts and current utilization levels, distributed inventory optimally.", confidence_score: 0.88, payload: null, timestamp: new Date(Date.now() - 1800000).toISOString() },
        ]);
        setGraphData({
          nodes: [
            { id: "orchestrator", label: "Orchestrator", icon: "🎯", status: "active" },
            { id: "demand_forecast", label: "Demand Forecast", icon: "📊", status: "active" },
            { id: "store_agent", label: "Store Agent", icon: "🏪", status: "active" },
            { id: "warehouse_agent", label: "Warehouse", icon: "🏭", status: "active" },
          ],
          edges: [
            { from: "orchestrator", to: "demand_forecast", label: "forecast_request" },
            { from: "orchestrator", to: "store_agent", label: "inventory_check" },
            { from: "orchestrator", to: "warehouse_agent", label: "allocation" },
            { from: "demand_forecast", to: "orchestrator", label: "forecast_result" },
            { from: "store_agent", to: "orchestrator", label: "restock_request" },
            { from: "warehouse_agent", to: "orchestrator", label: "allocation_result" },
          ],
        });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const filteredEvents = selectedAgent
    ? events.filter((e) => e.agent_name === selectedAgent)
    : events;

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-3xl font-bold"><span className="gradient-text">Agent Monitoring</span></h1>
        <p className="text-sm text-slate-400 mt-1">Real-time multi-agent communication and decision flow</p>
      </motion.div>

      {/* Agent Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map((agent, i) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
            className={`glass-card p-4 cursor-pointer transition-all ${selectedAgent === agent.id ? "border-blue-500/50 shadow-lg shadow-blue-500/10" : ""}`}
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">{agent.icon}</span>
              <div className="flex-1">
                <p className="text-sm font-semibold text-slate-200">{agent.name}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className={`status-dot ${agent.status === "active" ? "status-dot-active" : "bg-slate-600"}`} />
                  <span className={`text-[10px] ${agent.status === "active" ? "text-emerald-400" : "text-slate-500"}`}>
                    {agent.status}
                  </span>
                </div>
              </div>
            </div>
            <p className="text-[11px] text-slate-500 mb-2">{agent.description}</p>
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-slate-600">{agent.total_events} events</span>
              <span className="text-slate-600">
                {agent.last_activity ? timeAgo(agent.last_activity) : "—"}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Agent Graph Visualization */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-card p-6"
      >
        <h3 className="text-lg font-semibold mb-4">Agent Communication Graph</h3>
        <div className="relative h-[300px] flex items-center justify-center">
          {/* Simple graph visualization using positioned divs */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 800 300">
            {/* Connection lines */}
            {graphData?.edges.map((edge, i) => {
              const positions: Record<string, [number, number]> = {
                orchestrator: [400, 150],
                demand_forecast: [200, 60],
                store_agent: [600, 60],
                warehouse_agent: [400, 270],
                supplier_agent: [100, 200],
                logistics_agent: [700, 200],
                trend_agent: [200, 270],
                optimizer_agent: [600, 270],
              };
              const from = positions[edge.from] || [400, 150];
              const to = positions[edge.to] || [400, 150];
              return (
                <g key={i}>
                  <line
                    x1={from[0]} y1={from[1]} x2={to[0]} y2={to[1]}
                    stroke={AGENT_COLORS[edge.from] || "#3B82F6"}
                    strokeWidth="1.5"
                    strokeOpacity="0.3"
                    strokeDasharray="4 4"
                  />
                  {/* Animated dot */}
                  <circle r="3" fill={AGENT_COLORS[edge.from] || "#3B82F6"} opacity="0.8">
                    <animateMotion dur={`${2 + i * 0.5}s`} repeatCount="indefinite" path={`M${from[0]},${from[1]} L${to[0]},${to[1]}`} />
                  </circle>
                </g>
              );
            })}
            {/* Agent nodes */}
            {graphData?.nodes.map((node) => {
              const positions: Record<string, [number, number]> = {
                orchestrator: [400, 150],
                demand_forecast: [200, 60],
                store_agent: [600, 60],
                warehouse_agent: [400, 270],
                supplier_agent: [100, 200],
                logistics_agent: [700, 200],
                trend_agent: [200, 270],
                optimizer_agent: [600, 270],
              };
              const [x, y] = positions[node.id] || [400, 150];
              return (
                <g key={node.id}>
                  <circle cx={x} cy={y} r="28" fill={AGENT_COLORS[node.id] || "#3B82F6"} opacity="0.15" />
                  <circle cx={x} cy={y} r="22" fill="#1A1F35" stroke={AGENT_COLORS[node.id] || "#3B82F6"} strokeWidth="2" />
                  <text x={x} y={y + 4} textAnchor="middle" fontSize="16" fill="white">{node.icon}</text>
                  <text x={x} y={y + 42} textAnchor="middle" fontSize="10" fill="#94A3B8">{node.label}</text>
                </g>
              );
            })}
          </svg>
        </div>
      </motion.div>

      {/* Event Timeline */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Event Timeline</h3>
          {selectedAgent && (
            <button onClick={() => setSelectedAgent(null)} className="text-xs text-blue-400 hover:text-blue-300 cursor-pointer">
              Clear filter
            </button>
          )}
        </div>
        <div className="space-y-3">
          {filteredEvents.map((event, i) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex items-start gap-4 p-4 rounded-xl hover:bg-white/2 transition-colors"
            >
              <div className="flex flex-col items-center gap-1">
                <span>{getSeverityIcon(event.severity)}</span>
                <div className="w-px h-8 bg-white/5" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-slate-200">{event.title}</span>
                </div>
                {event.reasoning && (
                  <p className="text-xs text-slate-500 leading-relaxed mb-2 italic">
                    &ldquo;{event.reasoning}&rdquo;
                  </p>
                )}
                <div className="flex items-center gap-3 text-[10px]">
                  <span className="px-2 py-0.5 rounded-full border"
                    style={{
                      borderColor: `${AGENT_COLORS[event.agent_name]}40`,
                      background: `${AGENT_COLORS[event.agent_name]}10`,
                      color: AGENT_COLORS[event.agent_name],
                    }}>
                    {event.agent_name.replace("_", " ")}
                  </span>
                  <span className="text-slate-600">{event.event_type}</span>
                  {event.confidence_score && (
                    <span className="text-emerald-500">{formatPercent(event.confidence_score * 100)}</span>
                  )}
                  <span className="text-slate-600 ml-auto">{timeAgo(event.timestamp)}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
