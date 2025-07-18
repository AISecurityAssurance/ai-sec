import { useCallback, useState } from 'react';
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  addEdge,
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  MarkerType,
  type Node,
  type Edge,
  type Connection,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './ProcessControlDiagram.css';

interface ProcessControlDiagramProps {
  controllers: any[];
  controlActions: any[];
  isEditMode?: boolean;
}

const initialNodes: Node[] = [
  {
    id: 'operator',
    position: { x: 100, y: 50 },
    data: { label: 'Human Operator' },
    type: 'input',
    style: {
      background: '#4CAF50',
      color: 'white',
      border: '1px solid #388E3C',
      width: 180,
    }
  },
  {
    id: 'auth-service',
    position: { x: 400, y: 50 },
    data: { label: 'Authentication Service' },
    style: {
      background: '#2196F3',
      color: 'white',
      border: '1px solid #1976D2',
      width: 180,
    }
  },
  {
    id: 'transaction-processor',
    position: { x: 700, y: 50 },
    data: { label: 'Transaction Processor' },
    style: {
      background: '#2196F3',
      color: 'white',
      border: '1px solid #1976D2',
      width: 180,
    }
  },
  {
    id: 'api-gateway',
    position: { x: 400, y: 200 },
    data: { label: 'API Gateway' },
    style: {
      background: '#9C27B0',
      color: 'white',
      border: '1px solid #7B1FA2',
      width: 180,
    }
  },
  {
    id: 'database',
    position: { x: 550, y: 350 },
    data: { label: 'Customer Database' },
    type: 'output',
    style: {
      background: '#FF9800',
      color: 'white',
      border: '1px solid #F57C00',
      width: 180,
    }
  },
  {
    id: 'monitoring',
    position: { x: 100, y: 350 },
    data: { label: 'Security Monitoring' },
    style: {
      background: '#F44336',
      color: 'white',
      border: '1px solid #D32F2F',
      width: 180,
    }
  },
  {
    id: 'firewall',
    position: { x: 250, y: 500 },
    data: { label: 'Firewall' },
    style: {
      background: '#795548',
      color: 'white',
      border: '1px solid #5D4037',
      width: 180,
    }
  }
];

const initialEdges: Edge[] = [
  {
    id: 'e1-2',
    source: 'operator',
    target: 'auth-service',
    label: 'Configure Policies',
    type: 'smoothstep',
    animated: true,
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: 'e2-4',
    source: 'auth-service',
    target: 'api-gateway',
    label: 'Auth Tokens',
    type: 'smoothstep',
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: 'e3-4',
    source: 'transaction-processor',
    target: 'api-gateway',
    label: 'Transaction Status',
    type: 'smoothstep',
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: 'e4-3',
    source: 'api-gateway',
    target: 'transaction-processor',
    label: 'Approve Transaction',
    type: 'smoothstep',
    animated: true,
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: 'e3-5',
    source: 'transaction-processor',
    target: 'database',
    label: 'Update Balance',
    type: 'smoothstep',
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: 'e6-1',
    source: 'monitoring',
    target: 'operator',
    label: 'Security Alerts',
    type: 'smoothstep',
    style: { stroke: '#F44336' },
    animated: true,
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: 'e6-7',
    source: 'monitoring',
    target: 'firewall',
    label: 'Block IP',
    type: 'smoothstep',
    style: { stroke: '#F44336' },
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: 'e7-4',
    source: 'firewall',
    target: 'api-gateway',
    label: 'Filter Traffic',
    type: 'smoothstep',
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  }
];

export default function ProcessControlDiagram({ 
  controllers, 
  controlActions,
  isEditMode = false 
}: ProcessControlDiagramProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => {
      if (isEditMode) {
        setEdges((eds) => addEdge(params, eds));
      }
    },
    [isEditMode, setEdges]
  );

  return (
    <div className="process-control-diagram">
      <div className="diagram-info">
        <h3>System Control Structure</h3>
        <p>This diagram shows the control relationships between system components</p>
        {isEditMode && (
          <div className="edit-hint">
            <p>🔧 Edit Mode: Drag nodes to reposition, click and drag between nodes to create connections</p>
          </div>
        )}
      </div>
      
      <div className="diagram-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={isEditMode ? onNodesChange : undefined}
          onEdgesChange={isEditMode ? onEdgesChange : undefined}
          onConnect={onConnect}
          fitView
          attributionPosition="bottom-left"
        >
          <Background 
            variant={BackgroundVariant.Dots} 
            gap={12} 
            size={1} 
            color="#e0e0e0"
          />
          <MiniMap 
            nodeStrokeColor={(node) => node.style?.background as string || '#000'}
            nodeColor={(node) => node.style?.background as string || '#fff'}
            nodeBorderRadius={2}
          />
          <Controls />
        </ReactFlow>
      </div>

      <div className="legend">
        <h4>Legend</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#4CAF50' }}></div>
            <span>Human Controllers</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#2196F3' }}></div>
            <span>Software Controllers</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#9C27B0' }}></div>
            <span>Network Components</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#FF9800' }}></div>
            <span>Data Storage</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#F44336' }}></div>
            <span>Security Systems</span>
          </div>
        </div>
      </div>
    </div>
  );
}