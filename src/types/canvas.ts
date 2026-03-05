/**
 * Canvas-specific types for React Flow nodes and edges.
 *
 * Coding Standard 3: explicit types for all node/edge data shapes.
 * NodeData is separate from the Agent domain type so canvas state can
 * carry status info that doesn't exist in the backend model.
 */
import type { AgentRole } from "./index";

// ─── Node data shapes ─────────────────────────────────────────────────────────

/** Status of an agent node during or after execution. */
export type NodeStatus = "idle" | "running" | "done" | "error";

/** Data payload attached to every AgentNode in the canvas. */
export interface AgentNodeData {
  /** Backend agent UUID — present after the agent is persisted. */
  agentId: string;
  name: string;
  role: AgentRole;
  system_prompt: string;
  model_name: string;
  /** Runtime execution status — not persisted to the backend. */
  status: NodeStatus;
}

/** Data payload for the fixed Start node. */
export interface StartNodeData {
  label: "Start";
}

/** Data payload for the fixed End node. */
export interface EndNodeData {
  label: "End";
}

// ─── Edge data ────────────────────────────────────────────────────────────────

/** Optional label rendered on a React Flow edge. */
export interface EdgeData {
  label?: string;
}
