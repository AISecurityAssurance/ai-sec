import { useState } from 'react';
import { Shield, AlertTriangle, Info } from 'lucide-react';
import AnalysisTable from './AnalysisTable';
import { 
  strideThreats, 
  strideThreatTypes,
  strideComponents,
  getStrideByType,
  getCriticalStrideThreats,
  getStrideByComponent
} from '../mockData/strideData';
import './AnalysisPanel.css';

interface StrideAnalysisProps {
  onElementSelect?: (element: any, type: string) => void;
}

export default function StrideAnalysis({ onElementSelect }: StrideAnalysisProps) {
  const [selectedThreat, setSelectedThreat] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'by-type' | 'by-component' | 'details'>('overview');
  const [viewMode, setViewMode] = useState<'all' | 'critical'>('all');
  const [selectedType, setSelectedType] = useState<string>('Spoofing');
  const [selectedComponent, setSelectedComponent] = useState<string>(strideComponents[0]);

  const renderOverview = () => {
    const criticalCount = getCriticalStrideThreats().length;
    const highCount = strideThreats.filter(t => t.riskLevel === 'high').length;
    const mediumCount = strideThreats.filter(t => t.riskLevel === 'medium').length;
    const lowCount = strideThreats.filter(t => t.riskLevel === 'low').length;

    return (
      <div className="stride-overview">
        <div className="summary-cards">
          <div className="summary-card">
            <h4>Total Threats</h4>
            <div className="summary-value">{strideThreats.length}</div>
          </div>
          <div className="summary-card critical">
            <h4>Critical</h4>
            <div className="summary-value">{criticalCount}</div>
          </div>
          <div className="summary-card high">
            <h4>High Risk</h4>
            <div className="summary-value">{highCount}</div>
          </div>
          <div className="summary-card medium">
            <h4>Medium Risk</h4>
            <div className="summary-value">{mediumCount}</div>
          </div>
        </div>

        <div className="threat-type-grid">
          <h3>Threats by Type</h3>
          <div className="type-cards">
            {strideThreatTypes.map(type => {
              const count = getStrideByType(type.type as any).length;
              return (
                <div key={type.type} className="type-card">
                  <div className="type-icon">{type.icon}</div>
                  <h4>{type.type}</h4>
                  <p className="type-description">{type.description}</p>
                  <div className="type-count">{count} threats</div>
                </div>
              );
            })}
          </div>
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
          title="STRIDE Threat Analysis"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'component', label: 'Component', width: '20%' },
            { key: 'threatType', label: 'Type', width: '15%' },
            { key: 'description', label: 'Description', width: '30%' },
            { key: 'riskLevel', label: 'Risk', width: '10%' },
            { key: 'status', label: 'Status', width: '12%' },
          ]}
          data={viewMode === 'critical' ? getCriticalStrideThreats() : strideThreats}
          onRowSelect={(threat) => {
            setSelectedThreat(threat);
            setActiveTab('details');
            onElementSelect?.(threat, 'stride-threat');
          }}
          selectedRowId={selectedThreat?.id}
          getRowClassName={(row) => `risk-${row.riskLevel}`}
        />
      </div>
    );
  };

  const renderByType = () => {
    const threats = getStrideByType(selectedType as any);

    return (
      <div className="stride-by-type">
        <div className="type-selector">
          {strideThreatTypes.map(type => (
            <button
              key={type.type}
              className={`type-button ${selectedType === type.type ? 'active' : ''}`}
              onClick={() => setSelectedType(type.type)}
            >
              <span className="type-icon">{type.icon}</span>
              {type.type}
            </button>
          ))}
        </div>

        <div className="type-info">
          <h3>{selectedType}</h3>
          <p>{strideThreatTypes.find(t => t.type === selectedType)?.description}</p>
        </div>

        <AnalysisTable
          title={`${selectedType} Threats`}
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'component', label: 'Component', width: '20%' },
            { key: 'description', label: 'Description', width: '35%' },
            { key: 'likelihood', label: 'Likelihood', width: '10%' },
            { key: 'impact', label: 'Impact', width: '10%' },
            { key: 'riskLevel', label: 'Risk', width: '10%' },
          ]}
          data={threats}
          onRowSelect={(threat) => {
            setSelectedThreat(threat);
            setActiveTab('details');
            onElementSelect?.(threat, 'stride-threat');
          }}
          selectedRowId={selectedThreat?.id}
          getRowClassName={(row) => `risk-${row.riskLevel}`}
        />
      </div>
    );
  };

  const renderByComponent = () => {
    const threats = getStrideByComponent(selectedComponent);

    return (
      <div className="stride-by-component">
        <div className="component-selector">
          <label>Select Component:</label>
          <select 
            value={selectedComponent} 
            onChange={(e) => setSelectedComponent(e.target.value)}
            className="component-dropdown"
          >
            {strideComponents.map(comp => (
              <option key={comp} value={comp}>{comp}</option>
            ))}
          </select>
        </div>

        <AnalysisTable
          title={`Threats for ${selectedComponent}`}
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'threatType', label: 'Type', width: '15%' },
            { key: 'description', label: 'Description', width: '35%' },
            { key: 'asset', label: 'Asset', width: '20%' },
            { key: 'riskLevel', label: 'Risk', width: '10%' },
            { key: 'status', label: 'Status', width: '12%' },
          ]}
          data={threats}
          onRowSelect={(threat) => {
            setSelectedThreat(threat);
            setActiveTab('details');
            onElementSelect?.(threat, 'stride-threat');
          }}
          selectedRowId={selectedThreat?.id}
          getRowClassName={(row) => `risk-${row.riskLevel}`}
        />
      </div>
    );
  };

  const renderDetails = () => {
    if (!selectedThreat) return null;

    return (
      <div className="threat-details">
        <div className="detail-header">
          <h3>{selectedThreat.id}: {selectedThreat.description}</h3>
          <span className={`risk-badge ${selectedThreat.riskLevel}`}>
            {selectedThreat.riskLevel.toUpperCase()} RISK
          </span>
        </div>

        <div className="detail-grid">
          <div className="detail-section">
            <h4>Threat Information</h4>
            <div className="detail-item">
              <label>Component:</label>
              <span>{selectedThreat.component}</span>
            </div>
            <div className="detail-item">
              <label>Threat Type:</label>
              <span>{selectedThreat.threatType}</span>
            </div>
            <div className="detail-item">
              <label>Affected Asset:</label>
              <span>{selectedThreat.asset}</span>
            </div>
            <div className="detail-item">
              <label>Status:</label>
              <span className={`status-badge ${selectedThreat.status}`}>
                {selectedThreat.status}
              </span>
            </div>
          </div>

          <div className="detail-section">
            <h4>Risk Assessment</h4>
            <div className="detail-item">
              <label>Likelihood:</label>
              <span className={`likelihood-${selectedThreat.likelihood}`}>
                {selectedThreat.likelihood}
              </span>
            </div>
            <div className="detail-item">
              <label>Impact:</label>
              <span className={`impact-${selectedThreat.impact}`}>
                {selectedThreat.impact}
              </span>
            </div>
            <div className="detail-item">
              <label>Attack Vector:</label>
              <span>{selectedThreat.attackVector}</span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h4>Mitigations</h4>
          <ul className="mitigation-list">
            {selectedThreat.mitigations.map((mitigation: string, index: number) => (
              <li key={index}>{mitigation}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  return (
    <div className="stride-analysis">
      <p className="analysis-description">
        Systematic threat modeling using Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege
      </p>

      <div className="analysis-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'by-type' ? 'active' : ''}`}
          onClick={() => setActiveTab('by-type')}
        >
          By Threat Type
        </button>
        <button 
          className={`tab-button ${activeTab === 'by-component' ? 'active' : ''}`}
          onClick={() => setActiveTab('by-component')}
        >
          By Component
        </button>
        <button 
          className={`tab-button ${activeTab === 'details' ? 'active' : ''} ${!selectedThreat ? 'disabled' : ''}`}
          onClick={() => selectedThreat && setActiveTab('details')}
          disabled={!selectedThreat}
        >
          Threat Details {selectedThreat && `(${selectedThreat.id})`}
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'by-type' && renderByType()}
        {activeTab === 'by-component' && renderByComponent()}
        {activeTab === 'details' && renderDetails()}
      </div>
    </div>
  );
}