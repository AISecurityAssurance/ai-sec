import { useState } from 'react';
import { Bot, Shield, AlertTriangle, Eye } from 'lucide-react';
import AnalysisTable from './AnalysisTable';
import { 
  maestroAgents,
  maestroThreats,
  maestroControls,
  maestroCategories,
  getAgentById,
  getThreatsByAgent,
  getThreatsByCategory,
  getControlsByAgent,
  getCriticalThreats
} from '../mockData/maestroData';
import './AnalysisPanel.css';

interface MaestroAnalysisProps {
  onElementSelect?: (element: any, type: string) => void;
}

export default function MaestroAnalysis({ onElementSelect }: MaestroAnalysisProps) {
  const [activeTab, setActiveTab] = useState<'agents' | 'threats' | 'controls' | 'details'>('agents');
  const [selectedAgent, setSelectedAgent] = useState<any>(null);
  const [selectedThreat, setSelectedThreat] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'all' | 'critical'>('all');

  const renderAgents = () => {
    return (
      <div className="maestro-agents">
        <div className="agents-grid">
          {maestroAgents.map(agent => {
            const threats = getThreatsByAgent(agent.id);
            const controls = getControlsByAgent(agent.id);
            const criticalThreats = threats.filter(t => t.impact === 'critical');
            
            return (
              <div 
                key={agent.id} 
                className={`agent-card ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
                onClick={() => {
                  setSelectedAgent(agent);
                  setActiveTab('details');
                  onElementSelect?.(agent, 'maestro-agent');
                }}
              >
                <div className="agent-header">
                  <Bot size={24} />
                  <h3>{agent.name}</h3>
                  <span className={`trust-badge ${agent.trustLevel}`}>
                    {agent.trustLevel}
                  </span>
                </div>
                <p className="agent-type">{agent.type}</p>
                <p className="agent-purpose">{agent.purpose}</p>
                <div className="agent-stats">
                  <div className="stat">
                    <span className="stat-value">{threats.length}</span>
                    <span className="stat-label">Threats</span>
                  </div>
                  <div className="stat critical">
                    <span className="stat-value">{criticalThreats.length}</span>
                    <span className="stat-label">Critical</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{controls.length}</span>
                    <span className="stat-label">Controls</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderThreats = () => {
    const threatsToShow = viewMode === 'critical' ? getCriticalThreats() : maestroThreats;

    return (
      <div className="maestro-threats">
        <div className="threat-categories">
          {maestroCategories.map(category => {
            const count = getThreatsByCategory(category.name).length;
            return (
              <div key={category.name} className="category-card">
                <div className="category-icon">{category.icon}</div>
                <h4>{category.name}</h4>
                <p>{category.description}</p>
                <div className="category-count">{count} threats</div>
              </div>
            );
          })}
        </div>

        <div className="view-controls">
          <button 
            className={`view-button ${viewMode === 'all' ? 'active' : ''}`}
            onClick={() => setViewMode('all')}
          >
            <Shield size={16} />
            All Threats
          </button>
          <button 
            className={`view-button ${viewMode === 'critical' ? 'active' : ''}`}
            onClick={() => setViewMode('critical')}
          >
            <AlertTriangle size={16} />
            Critical Only
          </button>
        </div>

        <AnalysisTable
          title="AI/ML Security Threats"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'agentId', label: 'Agent', width: '10%' },
            { key: 'category', label: 'Category', width: '15%' },
            { key: 'threat', label: 'Threat', width: '30%' },
            { key: 'likelihood', label: 'Likelihood', width: '10%' },
            { key: 'impact', label: 'Impact', width: '10%' },
            { key: 'detectionDifficulty', label: 'Detection', width: '10%' },
          ]}
          data={threatsToShow.map(threat => ({
            ...threat,
            agentName: getAgentById(threat.agentId)?.name
          }))}
          onRowSelect={(threat) => {
            setSelectedThreat(threat);
            setSelectedAgent(getAgentById(threat.agentId));
            setActiveTab('details');
            onElementSelect?.(threat, 'maestro-threat');
          }}
          selectedRowId={selectedThreat?.id}
          getRowClassName={(row) => row.impact === 'critical' ? 'risk-critical' : row.impact === 'high' ? 'risk-high' : 'risk-medium'}
        />
      </div>
    );
  };

  const renderControls = () => {
    return (
      <div className="maestro-controls">
        <div className="controls-overview">
          <h3>Security Controls for AI/ML Systems</h3>
          <p>Preventive, detective, and corrective controls to mitigate AI-specific risks</p>
        </div>

        <AnalysisTable
          title="AI Security Controls"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'name', label: 'Control Name', width: '25%' },
            { key: 'type', label: 'Type', width: '12%' },
            { key: 'description', label: 'Description', width: '30%' },
            { key: 'effectiveness', label: 'Effectiveness', width: '12%' },
            { key: 'coverage', label: 'Coverage', width: '13%' },
          ]}
          data={maestroControls.map(control => ({
            ...control,
            coverage: `${control.coverage.length} agents`
          }))}
          onRowSelect={(control) => {
            onElementSelect?.(control, 'maestro-control');
          }}
        />
      </div>
    );
  };

  const renderDetails = () => {
    if (!selectedAgent) return null;

    const agentThreats = getThreatsByAgent(selectedAgent.id);
    const agentControls = getControlsByAgent(selectedAgent.id);

    return (
      <div className="maestro-details">
        <div className="detail-header">
          <Bot size={32} />
          <div>
            <h2>{selectedAgent.name}</h2>
            <p className="agent-type">{selectedAgent.type} - {selectedAgent.purpose}</p>
          </div>
          <span className={`trust-badge large ${selectedAgent.trustLevel}`}>
            {selectedAgent.trustLevel.toUpperCase()}
          </span>
        </div>

        <div className="detail-grid">
          <div className="detail-section">
            <h3>Capabilities</h3>
            <ul className="capability-list">
              {selectedAgent.capabilities.map((cap: string, idx: number) => (
                <li key={idx}>{cap}</li>
              ))}
            </ul>
          </div>

          <div className="detail-section">
            <h3>Data Access</h3>
            <div className="data-access-list">
              {selectedAgent.dataAccess.map((data: string, idx: number) => (
                <span key={idx} className="data-badge">{data}</span>
              ))}
            </div>
          </div>

          <div className="detail-section">
            <h3>System Interactions</h3>
            <div className="interaction-list">
              {selectedAgent.interactions.map((system: string, idx: number) => (
                <span key={idx} className="system-badge">{system}</span>
              ))}
            </div>
          </div>
        </div>

        {selectedThreat && (
          <div className="threat-detail">
            <h3>Selected Threat: {selectedThreat.id}</h3>
            <div className="threat-info">
              <p><strong>Category:</strong> {selectedThreat.category}</p>
              <p><strong>Threat:</strong> {selectedThreat.threat}</p>
              <p><strong>Scenario:</strong> {selectedThreat.scenario}</p>
              <div className="risk-assessment">
                <span className={`risk-badge ${selectedThreat.likelihood}`}>
                  Likelihood: {selectedThreat.likelihood}
                </span>
                <span className={`risk-badge ${selectedThreat.impact}`}>
                  Impact: {selectedThreat.impact}
                </span>
                <span className={`risk-badge detection-${selectedThreat.detectionDifficulty}`}>
                  Detection: {selectedThreat.detectionDifficulty}
                </span>
              </div>
            </div>
            <div className="mitigations">
              <h4>Mitigations</h4>
              <ul>
                {selectedThreat.mitigations.map((mit: string, idx: number) => (
                  <li key={idx}>{mit}</li>
                ))}
              </ul>
            </div>
            <div className="monitoring">
              <h4>Monitoring Required</h4>
              <ul>
                {selectedThreat.monitoringRequired.map((mon: string, idx: number) => (
                  <li key={idx}>{mon}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        <div className="agent-threats">
          <h3>Threats ({agentThreats.length})</h3>
          <div className="threat-list">
            {agentThreats.map(threat => (
              <div 
                key={threat.id} 
                className={`threat-item ${selectedThreat?.id === threat.id ? 'selected' : ''}`}
                onClick={() => {
                  setSelectedThreat(threat);
                  onElementSelect?.(threat, 'maestro-threat');
                }}
              >
                <span className="threat-id">{threat.id}</span>
                <span className="threat-category">{threat.category}</span>
                <span className="threat-desc">{threat.threat}</span>
                <span className={`impact-badge ${threat.impact}`}>{threat.impact}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="agent-controls">
          <h3>Applied Controls ({agentControls.length})</h3>
          <div className="control-list">
            {agentControls.map(control => (
              <div key={control.id} className="control-item">
                <span className="control-name">{control.name}</span>
                <span className={`control-type ${control.type}`}>{control.type}</span>
                <span className={`effectiveness ${control.effectiveness}`}>
                  {control.effectiveness} effectiveness
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="maestro-analysis">
      <p className="analysis-description">
        Multi-Agent Evaluated Securely Through Rigorous Oversight - Security analysis for AI/ML systems
      </p>

      <div className="analysis-tabs">
        <button 
          className={`tab-button ${activeTab === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveTab('agents')}
        >
          AI Agents
        </button>
        <button 
          className={`tab-button ${activeTab === 'threats' ? 'active' : ''}`}
          onClick={() => setActiveTab('threats')}
        >
          Threat Analysis
        </button>
        <button 
          className={`tab-button ${activeTab === 'controls' ? 'active' : ''}`}
          onClick={() => setActiveTab('controls')}
        >
          Security Controls
        </button>
        <button 
          className={`tab-button ${activeTab === 'details' ? 'active' : ''} ${!selectedAgent ? 'disabled' : ''}`}
          onClick={() => selectedAgent && setActiveTab('details')}
          disabled={!selectedAgent}
        >
          Agent Details {selectedAgent && `(${selectedAgent.name})`}
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'agents' && renderAgents()}
        {activeTab === 'threats' && renderThreats()}
        {activeTab === 'controls' && renderControls()}
        {activeTab === 'details' && renderDetails()}
      </div>
    </div>
  );
}