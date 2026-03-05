/**
 * FlowCanvas — the main React Flow canvas component.
 *
 * FE-03/04/05: node types, drag-to-add, edge connections.
 * FE-10 (M3): accepts nodeStatusMap prop to apply runtime execution status
 *   overlays to agent nodes without lifting node state out of this component.
 *
 * Wraps ReactFlow with project node types and wires drop/connect handlers.
 *
 * Coding Standard 2: React Flow state (nodes/edges) managed via useState;
 *   useCallback for handlers to avoid unnecessary re-renders.
 * Coding Standard 6: one component, one job — canvas rendering + interaction.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  Edge,
  MiniMap,
  Node,
  ReactFlowInstance,
  addEdge,
  useEdgesState,
  useNodesState,
} from "reactflow";
import type { Connection } from "reactflow";
import "reactflow/dist/style.css";
import { useCanvasDrop } from "../../hooks/useCanvasDrop";
import { useFlowStore } from "../../store/flowStore";
import type { AgentNodeData, NodeStatus } from "../../types/canvas";
import AgentConfigPanel from "./AgentConfigPanel";
import AgentNode from "./AgentNode";
import EndNode from "./EndNode";
import NodePalette from "./NodePalette";
import StartNode from "./StartNode";

// Node type registry — maps string keys to React components
const NODE_TYPES = {
  startNode: StartNode,
  endNode: EndNode,
  agentNode: AgentNode,
};

// Initial fixed nodes: one Start and one End
const INITIAL_NODES: Node[] = [
  {
    id: "start",
    type: "startNode",
    position: { x: 80, y: 200 },
    data: { label: "Start" },
    deletable: false,
  },
  {
    id: "end",
    type: "endNode",
    position: { x: 700, y: 200 },
    data: { label: "End" },
    deletable: false,
  },
];

interface FlowCanvasProps {
  initialNodes?: Node[];
  initialEdges?: Edge[];
  /**
   * FE-10: Maps agent UUID → runtime NodeStatus for execution overlay.
   * When a key is present, the matching agentNode's data.status is updated.
   * Parent resets this to {} when a new execution starts.
   */
  nodeStatusMap?: Record<string, NodeStatus>;
}

function FlowCanvas({
  initialNodes = INITIAL_NODES,
  initialEdges = [],
  nodeStatusMap = {},
}: FlowCanvasProps): JSX.Element {
  const setIsDirty = useFlowStore((s) => s.setIsDirty);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // FE-10: apply execution status overlays to agent nodes when nodeStatusMap changes.
  // prevMapRef prevents unnecessary setNodes calls when the map hasn't changed.
  const prevMapRef = useRef<Record<string, NodeStatus>>({});
  useEffect(() => {
    // Check if any values have changed to avoid spurious updates
    const hasChanges = Object.keys(nodeStatusMap).some(
      (agentId) => prevMapRef.current[agentId] !== nodeStatusMap[agentId]
    );
    if (!hasChanges) return;

    prevMapRef.current = { ...nodeStatusMap };

    setNodes((nds) =>
      nds.map((n) => {
        if (n.type !== "agentNode") return n;
        const agentNode = n as Node<AgentNodeData>;
        const newStatus = nodeStatusMap[agentNode.data.agentId];
        if (newStatus === undefined) return n;
        return { ...n, data: { ...agentNode.data, status: newStatus } };
      })
    );
  }, [nodeStatusMap, setNodes]);

  // Currently selected AgentNode — drives config panel visibility
  const [selectedNode, setSelectedNode] = useState<Node<AgentNodeData> | null>(
    null
  );

  // React Flow instance — needed by useCanvasDrop for coord conversion
  const [rfInstance, setRfInstance] = useState<ReactFlowInstance | null>(null);

  const onNodeAdd = useCallback(
    (node: Node<AgentNodeData>): void => {
      setNodes((nds) => [...nds, node]);
      setIsDirty(true);
    },
    [setNodes, setIsDirty]
  );

  const { onDragOver, onDrop } = useCanvasDrop({ onNodeAdd });

  const onConnect = useCallback(
    (connection: Connection): void => {
      setEdges((eds) => addEdge(connection, eds));
      setIsDirty(true);
    },
    [setEdges, setIsDirty]
  );

  const onSelectionChange = useCallback(
    ({ nodes: selected }: { nodes: Node[] }): void => {
      const agentNodes = selected.filter((n) => n.type === "agentNode");
      setSelectedNode(
        agentNodes.length === 1
          ? (agentNodes[0] as Node<AgentNodeData>)
          : null
      );
    },
    []
  );

  const onUpdateNode = useCallback(
    (id: string, data: Partial<AgentNodeData>): void => {
      setNodes((nds) =>
        nds.map((n) =>
          n.id === id ? { ...n, data: { ...n.data, ...data } } : n
        )
      );
    },
    [setNodes]
  );

  return (
    <div
      style={{ display: "flex", flex: 1, height: "100%", overflow: "hidden" }}
    >
      <NodePalette />

      <div style={{ flex: 1, height: "100%" }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={NODE_TYPES}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onSelectionChange={onSelectionChange}
          onDragOver={onDragOver}
          onDrop={(e) => {
            if (rfInstance !== null) {
              onDrop(e, rfInstance);
            }
          }}
          onInit={(instance: ReactFlowInstance) => {
            setRfInstance(instance);
          }}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background />
        </ReactFlow>
      </div>

      {selectedNode !== null && (
        <AgentConfigPanel node={selectedNode} onUpdateNode={onUpdateNode} />
      )}
    </div>
  );
}

export default FlowCanvas;
