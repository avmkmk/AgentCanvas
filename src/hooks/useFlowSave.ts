/**
 * useFlowSave — serializes canvas state to flow_config and PATCHes the API.
 *
 * FE-07: canvas save via PATCH /api/v1/flows/:id
 * Clears the isDirty flag on success.
 *
 * Coding Standard 5: errors captured in state — caller decides how to present.
 * Coding Standard 6: one hook, one job — save logic only.
 */
import { useCallback, useState } from "react";
import type { Edge, Node } from "reactflow";
import { useFlowStore } from "../store/flowStore";

interface UseFlowSaveResult {
  isSaving: boolean;
  saveError: string | null;
  save: (flowId: string, nodes: Node[], edges: Edge[]) => Promise<void>;
}

export function useFlowSave(): UseFlowSaveResult {
  const setIsDirty = useFlowStore((s) => s.setIsDirty);
  const updateFlowInStore = useFlowStore((s) => s.updateFlow);

  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const save = useCallback(
    async (flowId: string, nodes: Node[], edges: Edge[]): Promise<void> => {
      setIsSaving(true);
      setSaveError(null);
      try {
        // Serialize React Flow state into the flow_config JSON blob
        const flow_config = { nodes, edges };
        await updateFlowInStore(flowId, { flow_config });
        // Clear dirty flag — canvas is now in sync with the backend
        setIsDirty(false);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to save flow";
        setSaveError(message);
      } finally {
        setIsSaving(false);
      }
    },
    [setIsDirty, updateFlowInStore]
  );

  return { isSaving, saveError, save };
}
