/**
 * Axios API client for AgentCanvas backend.
 *
 * Coding Standard 8: wrap third-party clients in service classes.
 * All requests include the X-API-Key header from the environment.
 * Responses are validated: only 2xx are resolved; errors always include detail.
 */
import axios, { AxiosError, AxiosInstance, AxiosResponse } from "axios";
import type {
  Agent,
  AgentAnalytics,
  ExecutionStartRequest,
  FlowExecution,
  FlowCreateRequest,
  FlowUpdateRequest,
  Flow,
  HITLDecisionRequest,
  HITLReview,
  PaginatedResponse,
} from "../types/index";

// API key is injected at build time via Vite env vars (VITE_ prefix required).
// SECURITY NOTE (M1 known limitation): VITE_ vars are embedded in the browser
// bundle. This is acceptable for localhost development only. Before any
// non-localhost deployment, replace with a backend-for-frontend (BFF) proxy
// that holds the secret server-side, or implement short-lived token auth.
// Tracked in GitHub issue #29 (S-04 — token auth).
const API_KEY = import.meta.env.VITE_API_KEY as string;
const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api/v1";

function buildClient(): AxiosInstance {
  const client = axios.create({
    baseURL: BASE_URL,
    timeout: 30_000, // 30 s — Coding Standard 8: always set timeouts
    headers: {
      "Content-Type": "application/json",
      // API key auth — matches backend verify_api_key dependency
      "X-API-Key": API_KEY,
    },
  });

  // Response interceptor: normalize all errors to { detail: string }
  client.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError<{ detail: string }>) => {
      const detail =
        error.response?.data?.detail ??
        error.message ??
        "An unexpected error occurred";
      return Promise.reject(new Error(detail));
    }
  );

  return client;
}

const http = buildClient();

// ─── Flow endpoints ───────────────────────────────────────────────────────────

export async function listFlows(): Promise<PaginatedResponse<Flow>> {
  const res = await http.get<PaginatedResponse<Flow>>("/flows");
  return res.data;
}

export async function getFlow(flowId: string): Promise<Flow> {
  const res = await http.get<Flow>(`/flows/${flowId}`);
  return res.data;
}

export async function createFlow(payload: FlowCreateRequest): Promise<Flow> {
  const res = await http.post<Flow>("/flows", payload);
  return res.data;
}

export async function updateFlow(
  flowId: string,
  payload: FlowUpdateRequest
): Promise<Flow> {
  const res = await http.patch<Flow>(`/flows/${flowId}`, payload);
  return res.data;
}

export async function deleteFlow(flowId: string): Promise<void> {
  await http.delete(`/flows/${flowId}`);
}

// ─── Agent endpoints ──────────────────────────────────────────────────────────

export async function listAgents(flowId: string): Promise<Agent[]> {
  const res = await http.get<Agent[]>(`/flows/${flowId}/agents`);
  return res.data;
}

// ─── Execution endpoints ──────────────────────────────────────────────────────

export async function startExecution(
  payload: ExecutionStartRequest
): Promise<FlowExecution> {
  const res = await http.post<FlowExecution>("/executions", payload);
  return res.data;
}

export async function getExecution(executionId: string): Promise<FlowExecution> {
  const res = await http.get<FlowExecution>(`/executions/${executionId}`);
  return res.data;
}

export async function cancelExecution(
  executionId: string
): Promise<FlowExecution> {
  const res = await http.post<FlowExecution>(
    `/executions/${executionId}/cancel`
  );
  return res.data;
}

// ─── HITL endpoints ───────────────────────────────────────────────────────────

export async function listPendingReviews(): Promise<HITLReview[]> {
  const res = await http.get<HITLReview[]>("/hitl/pending");
  return res.data;
}

export async function submitReviewDecision(
  reviewId: string,
  payload: HITLDecisionRequest
): Promise<HITLReview> {
  const res = await http.post<HITLReview>(
    `/hitl/${reviewId}/decision`,
    payload
  );
  return res.data;
}

// ─── Analytics endpoints ──────────────────────────────────────────────────────

export async function getAgentAnalytics(
  agentId: string
): Promise<AgentAnalytics> {
  const res = await http.get<AgentAnalytics>(`/analytics/agents/${agentId}`);
  return res.data;
}
