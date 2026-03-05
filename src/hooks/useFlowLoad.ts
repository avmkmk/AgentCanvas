/**
 * useFlowLoad — loads a single flow and its agents by ID.
 *
 * Deserializes flow_config.nodes/edges into React Flow state.
 * Called by CanvasPage on mount when a flow ID is available.
 *
 * Coding Standard 5: errors captured in state — caller decides how to present.
 * Coding Standard 8: response validation before state update.
 */
import { useCallback, useEffect, useState } from "react";
import type { Edge, Node } from "reactflow";
import * as api from "../services/apiClient";
import { useFlowStore } from "../store/flowStore";
import type { Flow } from "../types/index";

interface UseFlowLoadResult {
  flow: Flow | null;
  nodes: Node[];
  edges: Edge[];
  isLoading: boolean;
  error: string | null;
}

export function useFlowLoad(flowId: string | undefined): UseFlowLoadResult {
  const setCurrentFlow = useFlowStore((s) => s.setCurrentFlow);

  const [flow, setFlow] = useState<Flow | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadFlow = useCallback(
    async (id: string): Promise<void> => {
      setIsLoading(true);
      setError(null);
      try {
        const loaded = await api.getFlow(id);

        // Validate response structure before using
        if (!loaded || typeof loaded.id !== "string") {
          throw new Error("Invalid flow response structure");
        }

        // Deserialize canvas graph from flow_config.
        // flow_config.nodes is typed as unknown[] — cast to Node[] after
        // validating it is an array (Coding Standard 8: validate before use).
        const config = loaded.flow_config;
        const rawNodes: Node[] = Array.isArray(config.nodes)
          ? (config.nodes as Node[])
          : [];
        const rawEdges: Edge[] = Array.isArray(config.edges)
          ? (config.edges as Edge[])
          : [];

        setFlow(loaded);
        setNodes(rawNodes);
        setEdges(rawEdges);
        // Sync to global store so canvas components can read it
        setCurrentFlow(loaded);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to load flow";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [setCurrentFlow]
  );

  useEffect(() => {
    if (flowId) {
      void loadFlow(flowId);
    }
  }, [flowId, loadFlow]);

  return { flow, nodes, edges, isLoading, error };
}
