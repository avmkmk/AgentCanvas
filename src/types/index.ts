/**
 * AgentCanvas — shared TypeScript types.
 *
 * These mirror the Pydantic schemas in backend/app/schemas/.
 * Any change here must be reflected in the backend schema and vice versa.
 * Coding Standard 3: explicit types — no `any`, no implicit coercion.
 */

// ─── Enums ────────────────────────────────────────────────────────────────────

export type AgentRole =
  | "researcher"
  | "analyst"
  | "writer"
  | "critic"
  | "planner"
  | "custom";

export type ExecutionStatus =
  | "pending"
  | "running"
  | "paused_hitl"
  | "completed"
  | "failed"
  | "cancelled";

export type GateType = "before" | "after" | "on_demand";

export type ReviewStatus = "pending" | "approved" | "rejected";

// ─── Flow ─────────────────────────────────────────────────────────────────────

export interface FlowConfig {
  /**
   * React Flow graph serialised as JSON.
   *
   * Typed as unknown[] rather than FlowNode[]/FlowEdge[] because the canvas
   * uses React Flow's Node<T>/Edge types which are incompatible with the
   * domain types here. Hooks cast to Node[]/Edge[] after loading.
   */
  nodes: unknown[];
  edges: unknown[];
}

export interface Flow {
  id: string;
  name: string;
  description: string | null;
  flow_config: FlowConfig;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FlowCreateRequest {
  name: string;
  description?: string | null;
  flow_config?: FlowConfig;
}

export interface FlowUpdateRequest {
  name?: string;
  description?: string | null;
  flow_config?: FlowConfig;
  is_active?: boolean;
}

// ─── Agent ────────────────────────────────────────────────────────────────────

export interface AgentConfig {
  /** Model-specific parameters — temperature, max_tokens, hitl gate, etc. */
  temperature?: number;
  max_tokens?: number;
  hitl_gate?: GateType | null;
}

/**
 * Agent — reconciled with AgentResponse schema (BA-15).
 *
 * Changed vs M1:
 *   Added:   type, system_prompt, model_name
 *   Removed: agent_type, step_order, is_active
 */
export interface Agent {
  id: string;
  flow_id: string | null;
  name: string;
  role: AgentRole;
  /** Agent implementation type — "conversational" only in MVP */
  type: string;
  system_prompt: string;
  model_name: string;
  config: AgentConfig | null;
  created_at: string;
}

export interface AgentCreateRequest {
  name: string;
  role: AgentRole;
  type?: string;
  system_prompt: string;
  model_name: string;
  config?: AgentConfig;
}

export interface AgentUpdateRequest {
  name?: string;
  role?: AgentRole;
  type?: string;
  system_prompt?: string;
  model_name?: string;
  config?: AgentConfig;
}

// ─── React Flow canvas types ───────────────────────────────────────────────────

export interface FlowNodeData {
  label: string;
  agentId: string;
  role: AgentRole;
  isActive: boolean;
}

export interface FlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: FlowNodeData;
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
}

// ─── Execution ────────────────────────────────────────────────────────────────

export interface FlowExecution {
  id: string;
  flow_id: string;
  status: ExecutionStatus;
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown> | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  execution_time_ms: number | null;
  success_rate: number | null;
  step_count: number;
  created_at: string;
}

export interface ExecutionStartRequest {
  flow_id: string;
  input_data: Record<string, unknown>;
}

// ─── HITL Review ──────────────────────────────────────────────────────────────

export interface HITLReview {
  id: string;
  execution_id: string | null;
  step_id: string | null;
  agent_id: string | null;
  gate_type: GateType;
  status: ReviewStatus;
  output_to_review: Record<string, unknown>;
  reviewer_comments: string | null;
  created_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
}

export interface HITLDecisionRequest {
  /** "approved" or "rejected" */
  decision: "approved" | "rejected";
  // Allow null explicitly — backend Optional[str] serialises Python None as JSON null
  reviewer_comments?: string | null;
  reviewed_by?: string | null;
}

// ─── Analytics ────────────────────────────────────────────────────────────────

export interface AgentAnalytics {
  id: string;
  agent_id: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  avg_execution_time_ms: number;
  min_execution_time_ms: number | null;
  max_execution_time_ms: number | null;
  total_llm_calls: number;
  total_hitl_reviews: number;
  last_run_at: string | null;
}

// ─── API Response wrappers ────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  detail: string;
}
