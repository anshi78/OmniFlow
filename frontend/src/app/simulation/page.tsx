"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import api from "@/lib/api";
import type { SimulationResult, SimulationScenario } from "@/types";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/utils";

const SCENARIO_ICONS: Record<string, string> = {
  demand_spike: "📈",
  supplier_strike: "🏭",
  warehouse_shutdown: "🚧",
  weather_disaster: "🌪️",
  viral_trend: "🔥",
};

const SCENARIO_COLORS: Record<string, string> = {
  demand_spike: "from-blue-500/20 to-violet-500/20 border-blue-500/30",
  supplier_strike: "from-amber-500/20 to-orange-500/20 border-amber-500/30",
  warehouse_shutdown: "from-rose-500/20 to-red-500/20 border-rose-500/30",
  weather_disaster: "from-cyan-500/20 to-blue-500/20 border-cyan-500/30",
  viral_trend: "from-pink-500/20 to-rose-500/20 border-pink-500/30",
};

export default function SimulationPage() {
  const [scenarios, setScenarios] = useState<SimulationScenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [pastSimulations, setPastSimulations] = useState<SimulationResult[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const [s, p] = await Promise.all([api.getScenarios(), api.getSimulations()]);
        setScenarios(s);
        setPastSimulations(p);
      } catch {
        setScenarios([
          { type: "demand_spike", title: "Demand Spike", description: "Simulates a 3-5x demand increase for a product category." },
          { type: "supplier_strike", title: "Supplier Strike", description: "Key supplier goes offline, disrupting supply." },
          { type: "warehouse_shutdown", title: "Warehouse Shutdown", description: "A warehouse loses capacity due to emergency." },
          { type: "weather_disaster", title: "Weather Disaster", description: "Severe weather disrupts regional deliveries." },
          { type: "viral_trend", title: "Viral Product Trend", description: "Social media drives unexpected demand." },
        ]);
      }
    })();
  }, []);

  const runSimulation = async (scenarioType: string) => {
    setRunning(true);
    setResult(null);
    setSelectedScenario(scenarioType);
    try {
      const res = await api.runSimulation(scenarioType, {
        magnitude: 3.0,
        duration_days: 7,
        category: "Electronics",
        region: "West",
      });
      setResult(res);
    } catch (err) {
      // Demo fallback
      setResult({
        id: "demo-1",
        scenario_type: scenarioType,
        title: `${scenarioType.replace("_", " ")} Simulation`,
        description: "Demo simulation result",
        parameters: { magnitude: 3.0, duration_days: 7 },
        status: "completed",
        inventory_impact: { products_affected: 12, stores_affected: 5, stockouts_predicted: 3, total_units_impact: -1850, recovery_time_days: 8 },
        financial_impact: { lost_revenue: 28500, additional_costs: 8200, emergency_shipping: 4100, total_impact: -40800 },
        agent_actions: [
          { agent: "demand_forecast", action: "spike_alert", target: "12 products", reasoning: "Detected 3x demand anomaly. Historical analysis suggests 7-day impact.", confidence: 0.91, timestamp: new Date().toISOString() },
          { agent: "store_agent", action: "emergency_restock", target: "5 stores", reasoning: "Stock projected to drop below safety threshold within 48 hours.", confidence: 0.88, timestamp: new Date().toISOString() },
          { agent: "warehouse_agent", action: "reallocation", target: "Cross-warehouse transfer", reasoning: "Reallocating 1850 units from surplus warehouses to cover shortfall.", confidence: 0.85, timestamp: new Date().toISOString() },
          { agent: "orchestrator", action: "coordination", target: "All agents", reasoning: "Coordinated response. Prioritized stores by revenue and severity.", confidence: 0.94, timestamp: new Date().toISOString() },
        ],
        carbon_impact: 285,
        duration_seconds: 2.4,
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
      });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-3xl font-bold"><span className="gradient-text">Simulation Center</span></h1>
        <p className="text-sm text-slate-400 mt-1">Digital Twin — test supply chain scenarios in real-time</p>
      </motion.div>

      {/* Scenario Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {scenarios.map((scenario, i) => (
          <motion.button
            key={scenario.type}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            onClick={() => runSimulation(scenario.type)}
            disabled={running}
            className={`glass-card p-5 text-left cursor-pointer transition-all duration-300 hover:scale-[1.02] border
              ${selectedScenario === scenario.type ? "border-blue-500/50 shadow-lg shadow-blue-500/10" : "border-white/5"}
              ${running ? "opacity-50 cursor-not-allowed" : ""}
              bg-gradient-to-br ${SCENARIO_COLORS[scenario.type] || ""}`}
            id={`scenario-${scenario.type}`}
          >
            <span className="text-3xl">{SCENARIO_ICONS[scenario.type] || "🔮"}</span>
            <h3 className="text-sm font-semibold mt-3 text-slate-200">{scenario.title}</h3>
            <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">{scenario.description}</p>
          </motion.button>
        ))}
      </div>

      {/* Running indicator */}
      <AnimatePresence>
        {running && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="glass-card p-6 flex items-center gap-4"
          >
            <div className="w-8 h-8 rounded-full border-2 border-blue-500/30 border-t-blue-500 animate-spin" />
            <div>
              <p className="text-sm font-medium text-slate-200">Running simulation...</p>
              <p className="text-xs text-slate-500">Agents analyzing scenario and generating responses</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Impact Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Inventory Impact */}
              <div className="glass-card p-5">
                <h4 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">📦 Inventory Impact</h4>
                <div className="space-y-2">
                  {Object.entries(result.inventory_impact || {}).filter(([k]) => typeof (result.inventory_impact as any)?.[k] === "number").map(([key, val]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-slate-400">{key.replace(/_/g, " ")}</span>
                      <span className={`font-mono font-semibold ${Number(val) < 0 ? "text-rose-400" : "text-slate-200"}`}>
                        {typeof val === "number" ? formatNumber(val) : String(val)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Financial Impact */}
              <div className="glass-card p-5">
                <h4 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">💰 Financial Impact</h4>
                <div className="space-y-2">
                  {Object.entries(result.financial_impact || {}).map(([key, val]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-slate-400">{key.replace(/_/g, " ")}</span>
                      <span className={`font-mono font-semibold ${Number(val) < 0 ? "text-rose-400" : "text-amber-400"}`}>
                        {formatCurrency(Number(val))}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Carbon Impact */}
              <div className="glass-card p-5">
                <h4 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">🌱 Environmental</h4>
                <div className="text-center py-4">
                  <p className="text-4xl font-bold text-cyan-400">{result.carbon_impact}</p>
                  <p className="text-xs text-slate-500 mt-1">kg CO₂ additional emissions</p>
                  <p className="text-xs text-slate-600 mt-3">Completed in {result.duration_seconds}s</p>
                </div>
              </div>
            </div>

            {/* Agent Actions */}
            <div className="glass-card p-6">
              <h4 className="text-lg font-semibold mb-4">🤖 Agent Responses</h4>
              <div className="space-y-4">
                {(result.agent_actions as any[] || []).map((action: any, i: number) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.15 }}
                    className="flex items-start gap-4 p-4 rounded-xl bg-slate-800/30 border border-white/5"
                  >
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0"
                      style={{ background: "linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))" }}>
                      {action.agent === "orchestrator" ? "🎯" : action.agent === "demand_forecast" ? "📊" : action.agent === "store_agent" ? "🏪" : "🏭"}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-semibold text-slate-200">{action.agent.replace("_", " ")}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          {action.action}
                        </span>
                        <span className="text-[10px] text-emerald-400 ml-auto font-mono">
                          {formatPercent(action.confidence * 100)} confident
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">{action.reasoning}</p>
                      <p className="text-[10px] text-slate-600 mt-1">Target: {action.target}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
