/**
 * FlowCanvas — the main React Flow canvas component.
 *
 * FE-03/04/05: node types, drag-to-add, edge connections.
 * Wraps ReactFlow with project node types and wires drop/connect handlers.
 *
 * Coding Standard 2: React Flow state (nodes/edges) managed via useState;
 *   useCallback for handlers to avoid unnecessary re-renders.
 * Coding Standard 6: one component, one job — canvas rendering + interaction.
 */
import { useCallback, useState } from "react";
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
import type { AgentNodeData } from "../../types/canvas";
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
}

function FlowCanvas({
  initialNodes = INITIAL_NODES,
  initialEdges = [],
}: FlowCanvasProps): JSX.Element {
  const setIsDirty = useFlowStore((s) => s.setIsDirty);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

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
