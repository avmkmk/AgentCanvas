/**
 * useCanvasDrop — handles node palette drag-and-drop onto the canvas.
 *
 * FE-04: converts screen coordinates to React Flow coordinates and creates
 * a new AgentNode with a temporary ID. The node gets a real backend UUID
 * when the flow is saved.
 *
 * Coding Standard 6: one hook, one job — drop logic only.
 * Coding Standard 2: all variables initialised before use.
 */
import { useCallback } from "react";
import type { DragEvent } from "react";
import type { Node, ReactFlowInstance } from "reactflow";
import type { AgentNodeData } from "../types/canvas";
import type { AgentRole } from "../types/index";

const DRAG_ROLE_KEY = "application/agentcanvas-role";

interface UseCanvasDropResult {
  onDragOver: (event: DragEvent<HTMLDivElement>) => void;
  onDrop: (
    event: DragEvent<HTMLDivElement>,
    reactFlowInstance: ReactFlowInstance
  ) => void;
}

interface UseCanvasDropProps {
  onNodeAdd: (node: Node<AgentNodeData>) => void;
}

export function useCanvasDrop({ onNodeAdd }: UseCanvasDropProps): UseCanvasDropResult {
  const onDragOver = useCallback(
    (event: React.DragEvent<HTMLDivElement>): void => {
      event.preventDefault();
      // Signal that a drop is accepted here
      event.dataTransfer.dropEffect = "move";
    },
    []
  );

  const onDrop = useCallback(
    (
      event: DragEvent<HTMLDivElement>,
      reactFlowInstance: ReactFlowInstance
    ): void => {
      event.preventDefault();

      const role = event.dataTransfer.getData(DRAG_ROLE_KEY) as AgentRole;
      if (!role) {
        // No role data — not a palette drag, ignore
        return;
      }

      // Convert screen position to React Flow coordinates
      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node<AgentNodeData> = {
        // Temporary ID — replaced by backend UUID on save (FE-07)
        id: `agent-${Date.now()}`,
        type: "agentNode",
        position,
        data: {
          // Empty agentId until persisted — canvas treats it as unsaved
          agentId: "",
          name: `${role.charAt(0).toUpperCase()}${role.slice(1)} Agent`,
          role,
          system_prompt: "",
          model_name: "claude-sonnet-4-6",
          status: "idle",
        },
      };

      onNodeAdd(newNode);
    },
    [onNodeAdd]
  );

  return { onDragOver, onDrop };
}

/** Key used to pass agent role data during palette drag operations. */
export { DRAG_ROLE_KEY };
