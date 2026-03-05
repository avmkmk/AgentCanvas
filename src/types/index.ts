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
  /** React Flow node/edge graph representation */
  nodes: FlowNode[];
  edges: FlowEdge[];
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
  /** System prompt text for this agent */
  system_prompt: string;
  /** Anthropic model ID — e.g. "claude-sonnet-4-6" */
  model?: string;
  /** Max tokens for LLM responses */
  max_tokens?: number;
  /** HITL gate configuration */
  hitl_gate?: GateType | null;
}

export interface Agent {
  id: string;
  flow_id: string;
  name: string;
  role: AgentRole;
  agent_type: string;
  config: AgentConfig;
  step_order: number;
  is_active: boolean;
  created_at: string;
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
