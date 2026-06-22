/* OmniFlow AI — API Client */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = `${baseUrl}/api`;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    if (response.status === 204) return {} as T;
    return response.json();
  }

  // ── Dashboard ──
  async getDashboard() {
    return this.request<import("@/types").DashboardData>("/dashboard");
  }

  // ── Products ──
  async getProducts(params?: { category?: string; search?: string }) {
    const query = new URLSearchParams();
    if (params?.category) query.set("category", params.category);
    if (params?.search) query.set("search", params.search);
    const qs = query.toString();
    return this.request<import("@/types").Product[]>(`/products${qs ? `?${qs}` : ""}`);
  }

  async getProductCategories() {
    return this.request<string[]>("/products/categories");
  }

  // ── Stores ──
  async getStores(region?: string) {
    const qs = region ? `?region=${region}` : "";
    return this.request<import("@/types").Store[]>(`/stores${qs}`);
  }

  // ── Warehouses ──
  async getWarehouses() {
    return this.request<import("@/types").Warehouse[]>("/warehouses");
  }

  // ── Inventory ──
  async getInventory(params?: {
    location_type?: string;
    status?: string;
    category?: string;
    search?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.location_type) query.set("location_type", params.location_type);
    if (params?.status) query.set("status", params.status);
    if (params?.category) query.set("category", params.category);
    if (params?.search) query.set("search", params.search);
    const qs = query.toString();
    return this.request<import("@/types").InventoryItem[]>(`/inventory${qs ? `?${qs}` : ""}`);
  }

  async getInventoryHealth() {
    return this.request<import("@/types").InventoryHealth>("/inventory/health");
  }

  // ── Forecasts ──
  async getForecasts(productId?: string) {
    const qs = productId ? `?product_id=${productId}` : "";
    return this.request<import("@/types").Forecast[]>(`/forecasts${qs}`);
  }

  async getForecastSeries(productId: string, days = 7) {
    return this.request<import("@/types").ForecastSeries>(
      `/forecasts/series/${productId}?days=${days}`
    );
  }

  // ── Simulations ──
  async getScenarios() {
    return this.request<import("@/types").SimulationScenario[]>("/simulations/scenarios");
  }

  async runSimulation(scenarioType: string, parameters: Record<string, unknown> = {}) {
    return this.request<import("@/types").SimulationResult>("/simulations", {
      method: "POST",
      body: JSON.stringify({ scenario_type: scenarioType, parameters }),
    });
  }

  async getSimulations() {
    return this.request<import("@/types").SimulationResult[]>("/simulations");
  }

  // ── Agents ──
  async getAgentsStatus() {
    return this.request<import("@/types").Agent[]>("/agents/status");
  }

  async getAgentEvents(params?: { agent_name?: string; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.agent_name) query.set("agent_name", params.agent_name);
    if (params?.limit) query.set("limit", String(params.limit));
    const qs = query.toString();
    return this.request<import("@/types").AgentEvent[]>(`/agents/events${qs ? `?${qs}` : ""}`);
  }

  async getAgentGraph() {
    return this.request<import("@/types").AgentGraphData>("/agents/graph");
  }

  async getRecommendations(params?: { status?: string; priority?: string }) {
    const query = new URLSearchParams();
    if (params?.status) query.set("status", params.status);
    if (params?.priority) query.set("priority", params.priority);
    const qs = query.toString();
    return this.request<import("@/types").Recommendation[]>(
      `/agents/recommendations${qs ? `?${qs}` : ""}`
    );
  }

  // ── Shipments ──
  async getShipments(status?: string) {
    const qs = status ? `?status=${status}` : "";
    return this.request<import("@/types").Shipment[]>(`/shipments${qs}`);
  }

  // ── Auth ──
  async login(email: string, password: string) {
    return this.request<import("@/types").AuthToken>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }
}

export const api = new ApiClient(API_BASE);
export default api;
