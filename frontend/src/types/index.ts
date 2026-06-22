/* OmniFlow AI — TypeScript Type Definitions */

// ── Products ────────────────────────────────
export interface Product {
  id: string;
  sku: string;
  name: string;
  category: string;
  subcategory: string | null;
  unit_price: number;
  cost_price: number;
  description: string | null;
  image_url: string | null;
  weight_kg: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductWithInventory extends Product {
  total_stock: number;
  store_stock: number;
  warehouse_stock: number;
  stock_status: string;
}

// ── Stores ──────────────────────────────────
export interface Store {
  id: string;
  name: string;
  code: string;
  location: string;
  city: string;
  region: string;
  latitude: number | null;
  longitude: number | null;
  store_type: string;
  capacity: number;
  is_active: boolean;
  created_at: string;
}

export interface StoreWithStats extends Store {
  total_products: number;
  total_stock: number;
  health_score: number;
  stockout_risk: number;
}

// ── Warehouses ──────────────────────────────
export interface Warehouse {
  id: string;
  name: string;
  code: string;
  location: string;
  city: string;
  region: string;
  latitude: number | null;
  longitude: number | null;
  capacity: number;
  current_utilization: number;
  is_active: boolean;
  created_at: string;
}

// ── Inventory ───────────────────────────────
export interface InventoryItem {
  id: string;
  product_id: string;
  store_id: string | null;
  warehouse_id: string | null;
  location_type: string;
  quantity: number;
  reserved_quantity: number;
  safety_stock: number;
  reorder_point: number;
  max_stock: number;
  daily_sales_avg: number;
  days_of_supply: number;
  status: "normal" | "low" | "critical" | "overstock";
  last_restocked: string | null;
  last_updated: string;
  product_name: string | null;
  product_sku: string | null;
  location_name: string | null;
  health_score: number;
}

export interface InventoryHealth {
  total_items: number;
  total_quantity: number;
  healthy_count: number;
  low_count: number;
  critical_count: number;
  overstock_count: number;
  average_health_score: number;
  total_value: number;
  stockout_risk_percent: number;
}

// ── Shipments ───────────────────────────────
export interface Shipment {
  id: string;
  from_warehouse_id: string;
  to_store_id: string;
  product_id: string;
  quantity: number;
  status: string;
  estimated_departure: string | null;
  estimated_arrival: string | null;
  actual_departure: string | null;
  actual_arrival: string | null;
  distance_km: number | null;
  carbon_score: number | null;
  shipping_cost: number | null;
  carrier: string | null;
  product_name: string | null;
  warehouse_name: string | null;
  store_name: string | null;
  created_at: string;
  updated_at: string;
}

// ── Forecasts ───────────────────────────────
export interface Forecast {
  id: string;
  product_id: string;
  store_id: string | null;
  forecast_date: string;
  horizon_days: number;
  predicted_demand: number;
  lower_bound: number | null;
  upper_bound: number | null;
  confidence: number;
  model_version: string;
  factors_used: Record<string, number> | null;
  is_spike: boolean;
  spike_magnitude: number | null;
  created_at: string;
  product_name: string | null;
}

export interface ForecastSeries {
  product_id: string;
  product_name: string;
  dates: string[];
  predicted: number[];
  lower: number[];
  upper: number[];
  actual: (number | null)[];
}

// ── Dashboard ───────────────────────────────
export interface DashboardStats {
  total_inventory: number;
  total_products: number;
  total_stores: number;
  total_warehouses: number;
  predicted_demand_7d: number;
  predicted_demand_30d: number;
  stockout_risk_percent: number;
  inventory_health_score: number;
  active_shipments: number;
  active_agent_decisions: number;
  pending_recommendations: number;
  total_inventory_value: number;
  carbon_footprint: number;
}

export interface DashboardCategory {
  category: string;
  total_quantity: number;
  product_count: number;
  health_score: number;
  value: number;
}

export interface DashboardRegionRisk {
  region: string;
  store_count: number;
  avg_health_score: number;
  stockout_risk: number;
  critical_items: number;
}

export interface DashboardData {
  stats: DashboardStats;
  inventory_by_category: DashboardCategory[];
  region_risks: DashboardRegionRisk[];
  recent_agent_events: AgentEvent[];
  recent_recommendations: Recommendation[];
}

// ── Agents ───────────────────────────────────
export interface Agent {
  id: string;
  name: string;
  description: string;
  status: "active" | "standby" | "error";
  icon: string;
  total_events: number;
  last_activity: string | null;
  last_action: string | null;
}

export interface AgentEvent {
  id: string;
  agent_name: string;
  event_type: string;
  severity: "info" | "warning" | "critical";
  title: string;
  description: string | null;
  reasoning: string | null;
  confidence_score: number | null;
  payload: Record<string, unknown> | null;
  timestamp: string;
}

export interface AgentGraphData {
  nodes: { id: string; label: string; icon: string; status: string }[];
  edges: { from: string; to: string; label: string }[];
}

// ── Recommendations ─────────────────────────
export interface Recommendation {
  id: string;
  agent_name: string;
  type: string;
  title: string;
  description: string;
  reason: string;
  confidence_score: number;
  factors_used: Record<string, number> | null;
  priority: "low" | "medium" | "high" | "critical";
  status: string;
  estimated_cost: number | null;
  estimated_savings: number | null;
  estimated_revenue_impact: number | null;
  created_at: string;
}

// ── Simulations ─────────────────────────────
export interface SimulationScenario {
  type: string;
  title: string;
  description: string;
}

export interface SimulationResult {
  id: string;
  scenario_type: string;
  title: string;
  description: string | null;
  parameters: Record<string, unknown> | null;
  status: string;
  inventory_impact: Record<string, unknown> | null;
  financial_impact: Record<string, unknown> | null;
  agent_actions: AgentAction[] | null;
  carbon_impact: number | null;
  duration_seconds: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface AgentAction {
  agent: string;
  action: string;
  target: string;
  reasoning: string;
  confidence: number;
  timestamp: string;
}

// ── Auth ─────────────────────────────────────
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: "admin" | "manager" | "viewer";
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}
