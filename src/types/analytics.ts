/**
 * Analytics TypeScript types — mirrors backend AgentAnalyticsSummary schema.
 *
 * Field names use snake_case to match backend JSON response directly.
 * The apiClient does not perform camelCase conversion — all existing types
 * (Flow, Agent, HITLReview) use snake_case to match backend output.
 *
 * Coding Standard 3: explicit types — no `any`, no implicit coercion.
 */

export interface AgentAnalyticsSummary {
  agent_id: string;
  agent_name: string;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  /** 0.0–1.0 — defaults to 0.0 when total_executions is 0 */
  success_rate: number;
  avg_execution_time_ms: number | null;
  last_executed_at: string | null;
}

export interface AgentAnalyticsListResponse {
  items: AgentAnalyticsSummary[];
  total: number;
}
