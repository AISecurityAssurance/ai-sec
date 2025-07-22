import { useState } from 'react';
import { Shield, Eye, Link, User, FileText, AlertTriangle, Scale } from 'lucide-react';
import AnalysisTable from './AnalysisTable';
import { 
  linddunThreats,
  dataFlows,
  privacyControls,
  linddunCategories,
  getThreatsByCategory,
  getThreatsByDataFlow,
  getCriticalThreats,
  getDataFlowById
} from '../mockData/linddunData';
import './AnalysisPanel.css';

interface LinddunAnalysisProps {
  onElementSelect?: (element: any, type: string) => void;
}

export default function LinddunAnalysis({ onElementSelect }: LinddunAnalysisProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'dataflows' | 'threats' | 'controls' | 'details'>('overview');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedDataFlow, setSelectedDataFlow] = useState<any>(null);
  const [selectedThreat, setSelectedThreat] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'all' | 'critical' | 'gdpr'>('all');

  const renderOverview = () => {
    return (
      <div className="linddun-overview">
        <div className="privacy-metrics">
          <div className="metric-card">
            <h4>Total Privacy Threats</h4>
            <div className="metric-value">{linddunThreats.length}</div>
            <div className="metric-detail">Across {dataFlows.length} data flows</div>
          </div>
          <div className="metric-card critical">
            <h4>Critical Threats</h4>
            <div className="metric-value">{getCriticalThreats().length}</div>
            <div className="metric-detail">Requiring immediate attention</div>
          </div>
          <div className="metric-card">
            <h4>GDPR Articles</h4>
            <div className="metric-value">
              {new Set(linddunThreats.flatMap(t => t.gdprArticles || [])).size}
            </div>
            <div className="metric-detail">Compliance considerations</div>
          </div>
          <div className="metric-card">
            <h4>Privacy Controls</h4>
            <div className="metric-value">{privacyControls.length}</div>
            <div className="metric-detail">Implemented measures</div>
          </div>
        </div>

        <div className="category-overview">
          <h3>LINDDUN Privacy Threat Categories</h3>
          <div className="category-grid">
            {linddunCategories.map(category => {
              const threats = getThreatsByCategory(category.name);
              const criticalCount = threats.filter(t => t.privacyImpact === 'critical').length;
              
              return (
                <div 
                  key={category.name}
                  className={`category-card ${selectedCategory === category.name ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedCategory(category.name);
                    setActiveTab('threats');
                    onElementSelect?.({ ...category, threatCount: threats.length }, 'linddun-category');
                  }}
                >
                  <div className="category-icon">{category.icon}</div>
                  <h4>{category.name}</h4>
                  <p>{category.description}</p>
                  <div className="category-stats">
                    <span className="total">{threats.length} threats</span>
                    {criticalCount > 0 && (
                      <span className="critical">{criticalCount} critical</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  const renderDataFlows = () => {
    return (
      <div className="linddun-dataflows">
        <div className="dataflow-overview">
          <h3>Data Flow Analysis</h3>
          <p>Personal data processing activities and their privacy implications</p>
        </div>

        <AnalysisTable
          title="Data Flows"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'name', label: 'Data Flow', width: '20%' },
            { key: 'source', label: 'Source', width: '15%' },
            { key: 'destination', label: 'Destination', width: '15%' },
            { key: 'dataTypes', label: 'Data Types', width: '20%' },
            { key: 'retention', label: 'Retention', width: '12%' },
            { key: 'encryption', label: 'Encryption', width: '10%' },
          ]}
          data={dataFlows.map(flow => ({
            ...flow,
            dataTypes: flow.dataTypes.join(', ')
          }))}
          onRowSelect={(flow) => {
            setSelectedDataFlow(flow);
            setActiveTab('details');
            onElementSelect?.(flow, 'linddun-dataflow');
          }}
          selectedRowId={selectedDataFlow?.id}
        />
      </div>
    );
  };

  const renderThreats = () => {
    let threatsToShow = linddunThreats;
    
    if (viewMode === 'critical') {
      threatsToShow = getCriticalThreats();
    } else if (viewMode === 'gdpr') {
      threatsToShow = linddunThreats.filter(t => t.gdprArticles && t.gdprArticles.length > 0);
    }

    if (selectedCategory) {
      threatsToShow = threatsToShow.filter(t => t.category === selectedCategory);
    }

    return (
      <div className="linddun-threats">
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
          <button 
            className={`view-button ${viewMode === 'gdpr' ? 'active' : ''}`}
            onClick={() => setViewMode('gdpr')}
          >
            <Scale size={16} />
            GDPR Related
          </button>
        </div>

        <AnalysisTable
          title={selectedCategory ? `${selectedCategory} Threats` : "Privacy Threats"}
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'category', label: 'Category', width: '12%' },
            { key: 'asset', label: 'Asset', width: '15%' },
            { key: 'threat', label: 'Threat', width: '25%' },
            { key: 'privacyImpact', label: 'Impact', width: '10%' },
            { key: 'likelihood', label: 'Likelihood', width: '10%' },
            { key: 'status', label: 'Status', width: '10%' },
            { key: 'gdpr', label: 'GDPR', width: '10%' },
          ]}
          data={threatsToShow.map(threat => ({
            ...threat,
            gdpr: threat.gdprArticles ? threat.gdprArticles.length > 0 ? '⚖️' : '-' : '-'
          }))}
          onRowSelect={(threat) => {
            setSelectedThreat(threat);
            setSelectedDataFlow(getDataFlowById(threat.dataFlow));
            setActiveTab('details');
            onElementSelect?.(threat, 'linddun-threat');
          }}
          selectedRowId={selectedThreat?.id}
          getRowClassName={(row) => 
            row.privacyImpact === 'critical' ? 'risk-critical' : 
            row.privacyImpact === 'high' ? 'risk-high' : 
            row.privacyImpact === 'medium' ? 'risk-medium' : 'risk-low'
          }
        />
      </div>
    );
  };

  const renderControls = () => {
    return (
      <div className="linddun-controls">
        <div className="controls-overview">
          <h3>Privacy Controls</h3>
          <p>Technical, organizational, and legal measures to protect personal data</p>
        </div>

        <AnalysisTable
          title="Privacy Protection Controls"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'name', label: 'Control Name', width: '22%' },
            { key: 'type', label: 'Type', width: '12%' },
            { key: 'description', label: 'Description', width: '33%' },
            { key: 'effectiveness', label: 'Effectiveness', width: '12%' },
            { key: 'applicableTo', label: 'Coverage', width: '13%' },
          ]}
          data={privacyControls.map(control => ({
            ...control,
            applicableTo: control.applicableTo.join(', ')
          }))}
          onRowSelect={(control) => {
            onElementSelect?.(control, 'linddun-control');
          }}
        />
      </div>
    );
  };

  const renderDetails = () => {
    if (!selectedThreat && !selectedDataFlow) {
      return (
        <div className="linddun-details empty">
          <p>Select a threat or data flow to view details</p>
        </div>
      );
    }

    return (
      <div className="linddun-details">
        {selectedDataFlow && (
          <div className="dataflow-detail">
            <h2>Data Flow: {selectedDataFlow.name}</h2>
            <div className="detail-grid">
              <div className="detail-section">
                <h3>Flow Information</h3>
                <p><strong>ID:</strong> {selectedDataFlow.id}</p>
                <p><strong>Source:</strong> {selectedDataFlow.source}</p>
                <p><strong>Destination:</strong> {selectedDataFlow.destination}</p>
                <p><strong>Purpose:</strong> {selectedDataFlow.purpose}</p>
                <p><strong>Retention:</strong> {selectedDataFlow.retention}</p>
              </div>
              
              <div className="detail-section">
                <h3>Data Types</h3>
                <div className="data-type-list">
                  {selectedDataFlow.dataTypes?.map((type: string, idx: number) => (
                    <span key={idx} className="data-type-badge">{type}</span>
                  ))}
                </div>
              </div>

              <div className="detail-section">
                <h3>Security Measures</h3>
                <p><strong>Encryption:</strong> {selectedDataFlow.encryption}</p>
                <p><strong>Access Control:</strong> {selectedDataFlow.accessControl}</p>
              </div>
            </div>

            <div className="related-threats">
              <h3>Related Threats</h3>
              <div className="threat-list">
                {getThreatsByDataFlow(selectedDataFlow.id).map(threat => (
                  <div 
                    key={threat.id}
                    className={`threat-item ${selectedThreat?.id === threat.id ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedThreat(threat);
                      onElementSelect?.(threat, 'linddun-threat');
                    }}
                  >
                    <span className="threat-id">{threat.id}</span>
                    <span className="threat-category">{threat.category}</span>
                    <span className="threat-desc">{threat.threat}</span>
                    <span className={`impact-badge ${threat.privacyImpact}`}>
                      {threat.privacyImpact}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {selectedThreat && (
          <div className="threat-detail">
            <h3>Threat Details: {selectedThreat.id}</h3>
            <div className="threat-info">
              <p><strong>Category:</strong> {selectedThreat.category}</p>
              <p><strong>Data Flow:</strong> {selectedThreat.dataFlow} - {getDataFlowById(selectedThreat.dataFlow)?.name}</p>
              <p><strong>Asset:</strong> {selectedThreat.asset}</p>
              <p><strong>Threat:</strong> {selectedThreat.threat}</p>
              <p><strong>Scenario:</strong> {selectedThreat.scenario}</p>
              
              <div className="risk-assessment">
                <span className={`risk-badge ${selectedThreat.privacyImpact}`}>
                  Privacy Impact: {selectedThreat.privacyImpact}
                </span>
                <span className={`risk-badge ${selectedThreat.likelihood}`}>
                  Likelihood: {selectedThreat.likelihood}
                </span>
                <span className={`status-badge ${selectedThreat.status}`}>
                  Status: {selectedThreat.status}
                </span>
              </div>

              <div className="affected-parties">
                <h4>Affected Parties</h4>
                <div className="party-list">
                  {selectedThreat.affectedParties.map((party: string, idx: number) => (
                    <span key={idx} className="party-badge">{party}</span>
                  ))}
                </div>
              </div>

              {selectedThreat.gdprArticles && selectedThreat.gdprArticles.length > 0 && (
                <div className="gdpr-compliance">
                  <h4>GDPR Compliance</h4>
                  <div className="gdpr-list">
                    {selectedThreat.gdprArticles.map((article: string, idx: number) => (
                      <div key={idx} className="gdpr-article">⚖️ {article}</div>
                    ))}
                  </div>
                </div>
              )}

              <div className="mitigations">
                <h4>Mitigations</h4>
                <ul>
                  {selectedThreat.mitigations.map((mit: string, idx: number) => (
                    <li key={idx}>{mit}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="linddun-analysis">
      <p className="analysis-description">
        Linkability, Identifiability, Non-repudiation, Detectability, Disclosure, Unawareness, Non-compliance - Privacy threat modeling
      </p>

      <div className="analysis-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'dataflows' ? 'active' : ''}`}
          onClick={() => setActiveTab('dataflows')}
        >
          Data Flows
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
          Privacy Controls
        </button>
        <button 
          className={`tab-button ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'dataflows' && renderDataFlows()}
        {activeTab === 'threats' && renderThreats()}
        {activeTab === 'controls' && renderControls()}
        {activeTab === 'details' && renderDetails()}
      </div>
    </div>
  );
}