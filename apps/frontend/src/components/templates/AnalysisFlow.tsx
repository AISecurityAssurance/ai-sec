import { useState, useCallback } from 'react';
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  addEdge,
  type Node,
  type Edge,
  type Connection
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Edit2, Download, X, Check } from 'lucide-react';
import { getSectionUrl } from './utils';
import './AnalysisFlow.css';

interface AnalysisFlowProps {
  id: string;
  title: string;
  initialNodes?: Node[];
  initialEdges?: Edge[];
  editable?: boolean;
  onSave?: (id: string, data: { nodes: Node[]; edges: Edge[] }) => void;
}

export function AnalysisFlow({
  id,
  title,
  initialNodes = [],
  initialEdges = [],
  editable = true,
  onSave
}: AnalysisFlowProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [originalNodes, setOriginalNodes] = useState(initialNodes);
  const [originalEdges, setOriginalEdges] = useState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleEdit = () => {
    setIsEditing(true);
    setOriginalNodes(nodes);
    setOriginalEdges(edges);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setNodes(originalNodes);
    setEdges(originalEdges);
  };

  const handleSave = () => {
    setIsEditing(false);
    if (onSave) {
      onSave(id, { nodes, edges });
    }
  };

  const handleExport = () => {
    const data = { nodes, edges };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${id}-flow.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="analysis-flow" style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <div className="analysis-flow-header">
        <a 
          href={getSectionUrl(id)}
          className="analysis-flow-title-link"
          onClick={(e) => e.preventDefault()}
        >
          <h3>{title}</h3>
        </a>
        {editable && (
          <div className="analysis-flow-toolbar">
            {isEditing ? (
              <>
                <button 
                  onClick={handleSave} 
                  className="icon-button"
                  title="Save"
                  aria-label="Save"
                >
                  <Check size={16} />
                </button>
                <button 
                  onClick={handleCancel} 
                  className="icon-button"
                  title="Cancel"
                  aria-label="Cancel"
                >
                  <X size={16} />
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={handleEdit} 
                  className="icon-button"
                  title="Edit"
                  aria-label="Edit"
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  onClick={handleExport} 
                  className="icon-button"
                  title="Export"
                  aria-label="Export"
                >
                  <Download size={16} />
                </button>
              </>
            )}
          </div>
        )}
      </div>
      <div className="analysis-flow-container" style={{ flex: 1, width: '100%' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={isEditing ? onNodesChange : undefined}
          onEdgesChange={isEditing ? onEdgesChange : undefined}
          onConnect={isEditing ? onConnect : undefined}
          fitView
          proOptions={{ hideAttribution: true }}
        >
          <Controls />
          <MiniMap />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>
    </div>
  );
}