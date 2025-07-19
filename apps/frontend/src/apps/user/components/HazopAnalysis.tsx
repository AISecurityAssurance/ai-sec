import { useState } from 'react';
import { AlertTriangle, Activity, Target, Shield, Clock } from 'lucide-react';
import AnalysisTable from './AnalysisTable';
import {
  hazopNodes,
  hazopDeviations,
  hazopActions,
  hazopGuideWords,
  getDeviationsByNode,
  getActionsByDeviation,
  getCriticalDeviations,
  getOpenActions,
  getNodeById,
  riskMatrix
} from '../mockData/hazopData';
import './AnalysisPanel.css';

interface HazopAnalysisProps {
  onElementSelect?: (element: any, type: string) => void;
}

export default function HazopAnalysis({ onElementSelect }: HazopAnalysisProps) {
  const [activeTab, setActiveTab] = useState<'nodes' | 'deviations' | 'actions' | 'matrix' | 'details'>('nodes');
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [selectedDeviation, setSelectedDeviation] = useState<any>(null);
  const [viewFilter, setViewFilter] = useState<'all' | 'critical' | 'open'>('all');

  const renderNodes = () => {
    return (
      <div className="hazop-nodes">
        <div className="nodes-overview">
          <h3>Process Nodes</h3>
          <p>System components and processes analyzed for deviations</p>
        </div>

        <div className="nodes-grid">
          {hazopNodes.map(node => {
            const deviations = getDeviationsByNode(node.id);
            const criticalCount = deviations.filter(d => d.riskRating === 'critical').length;
            
            return (
              <div
                key={node.id}
                className={`node-card ${selectedNode?.id === node.id ? 'selected' : ''}`}
                onClick={() => {
                  setSelectedNode(node);
                  setActiveTab('details');
                  onElementSelect?.(node, 'hazop-node');
                }}
              >
                <div className="node-header">
                  <Activity size={24} />
                  <h4>{node.name}</h4>
                  <span className={`node-type ${node.type}`}>{node.type}</span>
                </div>
                <p className="node-description">{node.description}</p>
                <div className="node-stats">
                  <div className="stat">
                    <span className="stat-value">{deviations.length}</span>
                    <span className="stat-label">Deviations</span>
                  </div>
                  {criticalCount > 0 && (
                    <div className="stat critical">
                      <span className="stat-value">{criticalCount}</span>
                      <span className="stat-label">Critical</span>
                    </div>
                  )}
                  <div className="stat">
                    <span className="stat-value">{node.parameters.length}</span>
                    <span className="stat-label">Parameters</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderDeviations = () => {
    let deviationsToShow = hazopDeviations;
    
    if (viewFilter === 'critical') {
      deviationsToShow = getCriticalDeviations();
    } else if (viewFilter === 'open') {
      deviationsToShow = hazopDeviations.filter(d => d.status === 'open' || d.status === 'in-review');
    }

    return (
      <div className="hazop-deviations">
        <div className="view-controls">
          <button
            className={`view-button ${viewFilter === 'all' ? 'active' : ''}`}
            onClick={() => setViewFilter('all')}
          >
            <Target size={16} />
            All Deviations
          </button>
          <button
            className={`view-button ${viewFilter === 'critical' ? 'active' : ''}`}
            onClick={() => setViewFilter('critical')}
          >
            <AlertTriangle size={16} />
            Critical Only
          </button>
          <button
            className={`view-button ${viewFilter === 'open' ? 'active' : ''}`}
            onClick={() => setViewFilter('open')}
          >
            <Clock size={16} />
            Open Items
          </button>
        </div>

        <AnalysisTable
          title="HAZOP Deviations"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'nodeName', label: 'Node', width: '15%' },
            { key: 'parameter', label: 'Parameter', width: '15%' },
            { key: 'guideWord', label: 'Guide Word', width: '10%' },
            { key: 'deviation', label: 'Deviation', width: '22%' },
            { key: 'riskRating', label: 'Risk', width: '10%' },
            { key: 'status', label: 'Status', width: '10%' },
            { key: 'actions', label: 'Actions', width: '10%' },
          ]}
          data={deviationsToShow.map(dev => ({
            ...dev,
            nodeName: getNodeById(dev.nodeId)?.name,
            actions: getActionsByDeviation(dev.id).length
          }))}
          onRowSelect={(deviation) => {
            setSelectedDeviation(deviation);
            setSelectedNode(getNodeById(deviation.nodeId));
            setActiveTab('details');
            onElementSelect?.(deviation, 'hazop-deviation');
          }}
          selectedRowId={selectedDeviation?.id}
          getRowClassName={(row) => 
            row.riskRating === 'critical' ? 'risk-critical' : 
            row.riskRating === 'high' ? 'risk-high' : 
            row.riskRating === 'medium' ? 'risk-medium' : 'risk-low'
          }
        />
      </div>
    );
  };

  const renderActions = () => {
    const actionsToShow = viewFilter === 'open' ? getOpenActions() : hazopActions;

    return (
      <div className="hazop-actions">
        <div className="actions-overview">
          <h3>Recommended Actions</h3>
          <p>Action items to address identified deviations</p>
        </div>

        <AnalysisTable
          title="HAZOP Actions"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'action', label: 'Action', width: '32%' },
            { key: 'responsible', label: 'Responsible', width: '15%' },
            { key: 'dueDate', label: 'Due Date', width: '12%' },
            { key: 'priority', label: 'Priority', width: '10%' },
            { key: 'status', label: 'Status', width: '13%' },
            { key: 'deviationId', label: 'Deviation', width: '10%' },
          ]}
          data={actionsToShow}
          onRowSelect={(action) => {
            const deviation = hazopDeviations.find(d => d.id === action.deviationId);
            if (deviation) {
              setSelectedDeviation(deviation);
              setSelectedNode(getNodeById(deviation.nodeId));
              setActiveTab('details');
            }
            onElementSelect?.(action, 'hazop-action');
          }}
          getRowClassName={(row) => {
            if (row.status === 'overdue') return 'status-overdue';
            if (row.priority === 'urgent') return 'priority-urgent';
            if (row.priority === 'high') return 'priority-high';
            return '';
          }}
        />
      </div>
    );
  };

  const renderRiskMatrix = () => {
    return (
      <div className="hazop-matrix">
        <div className="matrix-overview">
          <h3>Risk Assessment Matrix</h3>
          <p>Distribution of deviations by severity and likelihood</p>
        </div>

        <div className="guide-words">
          <h4>HAZOP Guide Words</h4>
          <div className="guide-words-grid">
            {hazopGuideWords.map(guide => (
              <div key={guide.word} className="guide-word-card">
                <strong>{guide.word}</strong>
                <span>{guide.description}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="risk-matrix-container">
          <h4>Risk Matrix</h4>
          <table className="risk-matrix-table">
            <thead>
              <tr>
                <th>Severity \ Likelihood</th>
                {riskMatrix.likelihood.map(l => (
                  <th key={l}>{l}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {riskMatrix.severity.map(severity => (
                <tr key={severity}>
                  <td className="severity-label">{severity}</td>
                  {riskMatrix.likelihood.map(likelihood => {
                    const rating = riskMatrix.getRating(severity, likelihood);
                    const count = hazopDeviations.filter(
                      d => d.severity === severity && d.likelihood === likelihood
                    ).length;
                    
                    return (
                      <td key={likelihood} className={`risk-cell risk-${rating}`}>
                        {count > 0 && (
                          <div className="risk-count">{count}</div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="risk-summary">
          <div className="summary-item">
            <span className="risk-indicator critical">Critical</span>
            <span>{hazopDeviations.filter(d => d.riskRating === 'critical').length} deviations</span>
          </div>
          <div className="summary-item">
            <span className="risk-indicator high">High</span>
            <span>{hazopDeviations.filter(d => d.riskRating === 'high').length} deviations</span>
          </div>
          <div className="summary-item">
            <span className="risk-indicator medium">Medium</span>
            <span>{hazopDeviations.filter(d => d.riskRating === 'medium').length} deviations</span>
          </div>
          <div className="summary-item">
            <span className="risk-indicator low">Low</span>
            <span>{hazopDeviations.filter(d => d.riskRating === 'low').length} deviations</span>
          </div>
        </div>
      </div>
    );
  };

  const renderDetails = () => {
    if (!selectedNode && !selectedDeviation) {
      return (
        <div className="hazop-details empty">
          <p>Select a node or deviation to view details</p>
        </div>
      );
    }

    return (
      <div className="hazop-details">
        {selectedNode && (
          <div className="node-detail">
            <h2>Node: {selectedNode.name}</h2>
            <div className="detail-grid">
              <div className="detail-section">
                <h3>Node Information</h3>
                <p><strong>ID:</strong> {selectedNode.id}</p>
                <p><strong>Type:</strong> {selectedNode.type}</p>
                <p><strong>Description:</strong> {selectedNode.description}</p>
                <p><strong>Normal Operation:</strong> {selectedNode.normalOperation}</p>
              </div>

              <div className="detail-section">
                <h3>Parameters Analyzed</h3>
                <ul className="parameter-list">
                  {selectedNode.parameters.map((param: string, idx: number) => (
                    <li key={idx}>{param}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="node-deviations">
              <h3>Identified Deviations</h3>
              <div className="deviation-list">
                {getDeviationsByNode(selectedNode.id).map(deviation => (
                  <div
                    key={deviation.id}
                    className={`deviation-item ${selectedDeviation?.id === deviation.id ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedDeviation(deviation);
                      onElementSelect?.(deviation, 'hazop-deviation');
                    }}
                  >
                    <span className="deviation-id">{deviation.id}</span>
                    <span className="guide-word">{deviation.guideWord}</span>
                    <span className="deviation-desc">{deviation.deviation}</span>
                    <span className={`risk-badge ${deviation.riskRating}`}>
                      {deviation.riskRating}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {selectedDeviation && (
          <div className="deviation-detail">
            <h3>Deviation Analysis: {selectedDeviation.id}</h3>
            <div className="deviation-info">
              <p><strong>Parameter:</strong> {selectedDeviation.parameter}</p>
              <p><strong>Guide Word:</strong> {selectedDeviation.guideWord}</p>
              <p><strong>Deviation:</strong> {selectedDeviation.deviation}</p>
              
              <div className="risk-assessment">
                <span className={`risk-badge ${selectedDeviation.severity}`}>
                  Severity: {selectedDeviation.severity}
                </span>
                <span className={`risk-badge ${selectedDeviation.likelihood}`}>
                  Likelihood: {selectedDeviation.likelihood}
                </span>
                <span className={`risk-badge ${selectedDeviation.riskRating}`}>
                  Risk: {selectedDeviation.riskRating}
                </span>
                <span className={`status-badge ${selectedDeviation.status}`}>
                  Status: {selectedDeviation.status}
                </span>
              </div>

              <div className="causes-section">
                <h4>Causes</h4>
                <ul>
                  {selectedDeviation.causes.map((cause: string, idx: number) => (
                    <li key={idx}>{cause}</li>
                  ))}
                </ul>
              </div>

              <div className="consequences-section">
                <h4>Consequences</h4>
                <ul>
                  {selectedDeviation.consequences.map((consequence: string, idx: number) => (
                    <li key={idx}>{consequence}</li>
                  ))}
                </ul>
              </div>

              <div className="safeguards-section">
                <h4>Existing Safeguards</h4>
                <ul>
                  {selectedDeviation.safeguards.map((safeguard: string, idx: number) => (
                    <li key={idx}>{safeguard}</li>
                  ))}
                </ul>
              </div>

              <div className="recommendations-section">
                <h4>Recommendations</h4>
                <ul>
                  {selectedDeviation.recommendations.map((rec: string, idx: number) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>

              <div className="actions-section">
                <h4>Action Items</h4>
                {getActionsByDeviation(selectedDeviation.id).map(action => (
                  <div key={action.id} className="action-item">
                    <div className="action-header">
                      <span className="action-id">{action.id}</span>
                      <span className={`priority-badge ${action.priority}`}>
                        {action.priority}
                      </span>
                      <span className={`status-badge ${action.status}`}>
                        {action.status}
                      </span>
                    </div>
                    <p className="action-desc">{action.action}</p>
                    <div className="action-meta">
                      <span>Responsible: {action.responsible}</span>
                      <span>Due: {action.dueDate}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="hazop-analysis">
      <p className="analysis-description">
        Hazard and Operability Study - Systematic examination of complex processes to identify potential problems
      </p>

      <div className="analysis-tabs">
        <button
          className={`tab-button ${activeTab === 'nodes' ? 'active' : ''}`}
          onClick={() => setActiveTab('nodes')}
        >
          Process Nodes
        </button>
        <button
          className={`tab-button ${activeTab === 'deviations' ? 'active' : ''}`}
          onClick={() => setActiveTab('deviations')}
        >
          Deviations
        </button>
        <button
          className={`tab-button ${activeTab === 'actions' ? 'active' : ''}`}
          onClick={() => setActiveTab('actions')}
        >
          Actions
        </button>
        <button
          className={`tab-button ${activeTab === 'matrix' ? 'active' : ''}`}
          onClick={() => setActiveTab('matrix')}
        >
          Risk Matrix
        </button>
        <button
          className={`tab-button ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'nodes' && renderNodes()}
        {activeTab === 'deviations' && renderDeviations()}
        {activeTab === 'actions' && renderActions()}
        {activeTab === 'matrix' && renderRiskMatrix()}
        {activeTab === 'details' && renderDetails()}
      </div>
    </div>
  );
}