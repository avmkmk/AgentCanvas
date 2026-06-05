/**
 * Axios API client for AgentCanvas backend.
 *
 * Coding Standard 8: wrap third-party clients in service classes.
 * All requests include a Bearer token from Keycloak.
 * Responses are validated: only 2xx are resolved; errors always include detail.
 */
import axios, { AxiosError, AxiosInstance, AxiosResponse } from "axios";
import keycloak from '../auth/keycloak';
import type {
  Agent,
  AgentCreateRequest,
  AgentUpdateRequest,
  ExecutionStartRequest,
  FlowExecution,
  FlowCreateRequest,
  FlowUpdateRequest,
  Flow,
  HITLDecisionRequest,
  HITLReview,
  PaginatedResponse,
} from "../types/index";
import type { AgentAnalyticsListResponse, AgentAnalyticsSummary } from "../types/analytics";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api/v1";

function buildClient(): AxiosInstance {
  const client = axios.create({
    baseURL: BASE_URL,
    timeout: 30_000, // 30 s — Coding Standard 8: always set timeouts
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Request interceptor: attach Keycloak Bearer token to every request
  client.interceptors.request.use((config) => {
    const token = keycloak.token;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
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

export async function createAgent(
  flowId: string,
  payload: AgentCreateRequest
): Promise<Agent> {
  const res = await http.post<Agent>(`/flows/${flowId}/agents`, payload);
  return res.data;
}

export async function getAgent(
  flowId: string,
  agentId: string
): Promise<Agent> {
  const res = await http.get<Agent>(`/flows/${flowId}/agents/${agentId}`);
  return res.data;
}

export async function updateAgent(
  flowId: string,
  agentId: string,
  payload: AgentUpdateRequest
): Promise<Agent> {
  const res = await http.patch<Agent>(
    `/flows/${flowId}/agents/${agentId}`,
    payload
  );
  return res.data;
}

export async function deleteAgent(
  flowId: string,
  agentId: string
): Promise<void> {
  await http.delete(`/flows/${flowId}/agents/${agentId}`);
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

export async function listAgentAnalytics(): Promise<AgentAnalyticsListResponse> {
  const res = await http.get<AgentAnalyticsListResponse>("/analytics/agents");
  return res.data;
}

export async function getAgentAnalytics(
  agentId: string
): Promise<AgentAnalyticsSummary> {
  const res = await http.get<AgentAnalyticsSummary>(`/analytics/agents/${agentId}`);
  return res.data;
}
