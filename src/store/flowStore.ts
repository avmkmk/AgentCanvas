/**
 * Zustand store for Flow and Agent state.
 *
 * Coding Standard 3: explicit interfaces for all state and actions.
 * Coding Standard 5: errors are never silent — set error state and log.
 * Components must use hooks (useFlowStore) — never import store directly.
 */
import { create } from "zustand";
import * as api from "../services/apiClient";
import type { Agent, Flow, FlowCreateRequest, FlowUpdateRequest } from "../types/index";

interface FlowState {
  // ─── Data ──────────────────────────────────────────────────────────────────
  flows: Flow[];
  selectedFlow: Flow | null;
  agents: Agent[];

  // ─── Async status ──────────────────────────────────────────────────────────
  isLoading: boolean;
  error: string | null;

  // ─── Actions ───────────────────────────────────────────────────────────────
  fetchFlows: () => Promise<void>;
  selectFlow: (flowId: string) => Promise<void>;
  createFlow: (payload: FlowCreateRequest) => Promise<Flow>;
  updateFlow: (flowId: string, payload: FlowUpdateRequest) => Promise<void>;
  deleteFlow: (flowId: string) => Promise<void>;
  clearError: () => void;
}

export const useFlowStore = create<FlowState>()((set, get) => ({
  flows: [],
  selectedFlow: null,
  agents: [],
  isLoading: false,
  error: null,

  fetchFlows: async () => {
    set({ isLoading: true, error: null });
    try {
      const result = await api.listFlows();
      set({ flows: result.items, isLoading: false });
    } catch (err) {
      // Coding Standard 5: always capture error detail — never silent
      const message = err instanceof Error ? err.message : "Failed to load flows";
      set({ error: message, isLoading: false });
    }
  },

  selectFlow: async (flowId: string) => {
    set({ isLoading: true, error: null });
    try {
      const [flow, agents] = await Promise.all([
        api.getFlow(flowId),
        api.listAgents(flowId),
      ]);
      set({ selectedFlow: flow, agents, isLoading: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load flow";
      set({ error: message, isLoading: false });
    }
  },

  createFlow: async (payload: FlowCreateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const newFlow = await api.createFlow(payload);
      // Optimistic update: prepend to list
      set((state) => ({
        flows: [newFlow, ...state.flows],
        isLoading: false,
      }));
      return newFlow;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create flow";
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  updateFlow: async (flowId: string, payload: FlowUpdateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await api.updateFlow(flowId, payload);
      set((state) => ({
        flows: state.flows.map((f) => (f.id === flowId ? updated : f)),
        selectedFlow:
          state.selectedFlow?.id === flowId ? updated : state.selectedFlow,
        isLoading: false,
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to update flow";
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  deleteFlow: async (flowId: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.deleteFlow(flowId);
      set((state) => ({
        flows: state.flows.filter((f) => f.id !== flowId),
        selectedFlow:
          state.selectedFlow?.id === flowId ? null : state.selectedFlow,
        isLoading: false,
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to delete flow";
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  // set({ error: null }) is a no-op in Zustand when error is already null — no guard needed
  clearError: () => set({ error: null }),
}));
