import { useState } from 'react';
import { Shield, AlertTriangle, Database, Users, Settings, Target } from 'lucide-react';
import AnalysisTable from './AnalysisTable';
import {
  octaveAssets,
  octaveThreats,
  octaveVulnerabilities,
  octaveRisks,
  octaveProtectionStrategies,
  getAssetById,
  getThreatsByAsset,
  getVulnerabilitiesByAsset,
  getRisksByAsset,
  getCriticalRisks,
  getHighValueAssets,
  getThreatById,
  getVulnerabilityById,
  getStrategiesByAsset,
  riskMatrix
} from '../mockData/octaveData';
import './AnalysisPanel.css';

interface OctaveAnalysisProps {
  onElementSelect?: (element: any, type: string) => void;
}

export default function OctaveAnalysis({ onElementSelect }: OctaveAnalysisProps) {
  const [activeTab, setActiveTab] = useState<'assets' | 'threats' | 'vulnerabilities' | 'risks' | 'strategies' | 'details'>('assets');
  const [selectedAsset, setSelectedAsset] = useState<any>(null);
  const [selectedThreat, setSelectedThreat] = useState<any>(null);
  const [selectedRisk, setSelectedRisk] = useState<any>(null);
  const [viewFilter, setViewFilter] = useState<'all' | 'critical' | 'high-value'>('all');

  const renderAssets = () => {
    const assetsToShow = viewFilter === 'high-value' ? getHighValueAssets() : octaveAssets;

    return (
      <div className="octave-assets">
        <div className="assets-overview">
          <h3>Critical Assets Inventory</h3>
          <p>Operationally critical assets requiring protection</p>
        </div>

        <div className="view-controls">
          <button
            className={`view-button ${viewFilter === 'all' ? 'active' : ''}`}
            onClick={() => setViewFilter('all')}
          >
            <Database size={16} />
            All Assets
          </button>
          <button
            className={`view-button ${viewFilter === 'high-value' ? 'active' : ''}`}
            onClick={() => setViewFilter('high-value')}
          >
            <AlertTriangle size={16} />
            High Value Only
          </button>
        </div>

        <AnalysisTable
          title="Asset Register"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'name', label: 'Asset Name', width: '20%' },
            { key: 'type', label: 'Type', width: '10%' },
            { key: 'criticality', label: 'Criticality', width: '10%' },
            { key: 'owner', label: 'Owner', width: '15%' },
            { key: 'cia', label: 'CIA Requirements', width: '15%' },
            { key: 'threats', label: 'Threats', width: '10%' },
            { key: 'risks', label: 'Risks', width: '12%' },
          ]}
          data={assetsToShow.map(asset => ({
            ...asset,
            cia: `C:${asset.securityRequirements.confidentiality[0].toUpperCase()} I:${asset.securityRequirements.integrity[0].toUpperCase()} A:${asset.securityRequirements.availability[0].toUpperCase()}`,
            threats: getThreatsByAsset(asset.id).length,
            risks: getRisksByAsset(asset.id).length
          }))}
          onRowSelect={(asset) => {
            setSelectedAsset(asset);
            setActiveTab('details');
            onElementSelect?.(asset, 'octave-asset');
          }}
          selectedRowId={selectedAsset?.id}
          getRowClassName={(row) => 
            row.criticality === 'critical' ? 'criticality-critical' : 
            row.criticality === 'high' ? 'criticality-high' : 
            row.criticality === 'medium' ? 'criticality-medium' : 'criticality-low'
          }
        />
      </div>
    );
  };

  const renderThreats = () => {
    return (
      <div className="octave-threats">
        <div className="threats-overview">
          <h3>Threat Scenarios</h3>
          <p>Identified threats to critical assets</p>
        </div>

        <AnalysisTable
          title="Threat Register"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'assetName', label: 'Asset', width: '15%' },
            { key: 'source', label: 'Source', width: '15%' },
            { key: 'actor', label: 'Threat Actor', width: '15%' },
            { key: 'outcome', label: 'Outcome', width: '22%' },
            { key: 'probability', label: 'Probability', width: '10%' },
            { key: 'maxImpact', label: 'Max Impact', width: '8%' },
            { key: 'gaps', label: 'Gaps', width: '7%' },
          ]}
          data={octaveThreats.map(threat => ({
            ...threat,
            assetName: getAssetById(threat.assetId)?.name,
            maxImpact: Math.max(...Object.values(threat.impact)),
            gaps: threat.controlGaps.length
          }))}
          onRowSelect={(threat) => {
            setSelectedThreat(threat);
            setSelectedAsset(getAssetById(threat.assetId));
            setActiveTab('details');
            onElementSelect?.(threat, 'octave-threat');
          }}
          selectedRowId={selectedThreat?.id}
          getRowClassName={(row) => {
            if (row.probability === 'very-high' || row.probability === 'high') return 'probability-high';
            if (row.probability === 'medium') return 'probability-medium';
            return 'probability-low';
          }}
        />
      </div>
    );
  };

  const renderVulnerabilities = () => {
    return (
      <div className="octave-vulnerabilities">
        <div className="vulnerabilities-overview">
          <h3>Vulnerability Assessment</h3>
          <p>Technical, physical, and organizational vulnerabilities</p>
        </div>

        <AnalysisTable
          title="Vulnerability Register"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'assetName', label: 'Asset', width: '15%' },
            { key: 'type', label: 'Type', width: '12%' },
            { key: 'category', label: 'Category', width: '15%' },
            { key: 'description', label: 'Description', width: '25%' },
            { key: 'severity', label: 'Severity', width: '10%' },
            { key: 'exploitability', label: 'Exploitability', width: '10%' },
            { key: 'status', label: 'Status', width: '5%' },
          ]}
          data={octaveVulnerabilities.map(vuln => ({
            ...vuln,
            assetName: getAssetById(vuln.assetId)?.name
          }))}
          onRowSelect={(vuln) => {
            setSelectedAsset(getAssetById(vuln.assetId));
            setActiveTab('details');
            onElementSelect?.(vuln, 'octave-vulnerability');
          }}
          getRowClassName={(row) => 
            row.severity === 'critical' ? 'severity-critical' : 
            row.severity === 'high' ? 'severity-high' : 
            row.severity === 'medium' ? 'severity-medium' : 'severity-low'
          }
        />
      </div>
    );
  };

  const renderRisks = () => {
    const risksToShow = viewFilter === 'critical' ? getCriticalRisks() : octaveRisks;

    return (
      <div className="octave-risks">
        <div className="view-controls">
          <button
            className={`view-button ${viewFilter === 'all' ? 'active' : ''}`}
            onClick={() => setViewFilter('all')}
          >
            <Target size={16} />
            All Risks
          </button>
          <button
            className={`view-button ${viewFilter === 'critical' ? 'active' : ''}`}
            onClick={() => setViewFilter('critical')}
          >
            <AlertTriangle size={16} />
            Critical Only
          </button>
        </div>

        <AnalysisTable
          title="Risk Register"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'assetName', label: 'Asset', width: '15%' },
            { key: 'description', label: 'Risk Description', width: '25%' },
            { key: 'likelihood', label: 'Likelihood', width: '10%' },
            { key: 'impact', label: 'Impact', width: '10%' },
            { key: 'riskLevel', label: 'Risk Level', width: '10%' },
            { key: 'strategy', label: 'Strategy', width: '10%' },
            { key: 'residualRisk', label: 'Residual', width: '12%' },
          ]}
          data={risksToShow.map(risk => ({
            ...risk,
            assetName: getAssetById(risk.assetId)?.name,
            residualRisk: risk.residualRisk || 'N/A'
          }))}
          onRowSelect={(risk) => {
            setSelectedRisk(risk);
            setSelectedAsset(getAssetById(risk.assetId));
            setSelectedThreat(getThreatById(risk.threatId));
            setActiveTab('details');
            onElementSelect?.(risk, 'octave-risk');
          }}
          selectedRowId={selectedRisk?.id}
          getRowClassName={(row) => 
            row.riskLevel === 'critical' ? 'risk-critical' : 
            row.riskLevel === 'high' ? 'risk-high' : 
            row.riskLevel === 'medium' ? 'risk-medium' : 'risk-low'
          }
        />

        <div className="risk-matrix-container">
          <h4>Risk Heat Map</h4>
          <table className="risk-matrix-table">
            <thead>
              <tr>
                <th>Impact \ Likelihood</th>
                {riskMatrix.likelihood.map(l => (
                  <th key={l}>{l}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...riskMatrix.impact].reverse().map(impact => (
                <tr key={impact}>
                  <td className="impact-label">{impact}</td>
                  {riskMatrix.likelihood.map(likelihood => {
                    const level = riskMatrix.getRiskLevel(likelihood, impact);
                    const count = octaveRisks.filter(
                      r => r.likelihood === likelihood && r.impact === impact
                    ).length;
                    
                    return (
                      <td key={likelihood} className={`risk-cell risk-${level}`}>
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
      </div>
    );
  };

  const renderStrategies = () => {
    return (
      <div className="octave-strategies">
        <div className="strategies-overview">
          <h3>Protection Strategies</h3>
          <p>Security controls and mitigation strategies</p>
        </div>

        <AnalysisTable
          title="Protection Strategy Register"
          columns={[
            { key: 'id', label: 'ID', width: '8%' },
            { key: 'name', label: 'Strategy Name', width: '20%' },
            { key: 'type', label: 'Type', width: '12%' },
            { key: 'description', label: 'Description', width: '25%' },
            { key: 'coverage', label: 'Assets', width: '8%' },
            { key: 'effectiveness', label: 'Effectiveness', width: '10%' },
            { key: 'timeframe', label: 'Timeframe', width: '10%' },
            { key: 'status', label: 'Status', width: '7%' },
          ]}
          data={octaveProtectionStrategies.map(strategy => ({
            ...strategy,
            coverage: strategy.coverage.length
          }))}
          onRowSelect={(strategy) => {
            onElementSelect?.(strategy, 'octave-strategy');
          }}
          getRowClassName={(row) => {
            if (row.status === 'operational') return 'status-operational';
            if (row.status === 'implementing') return 'status-implementing';
            return '';
          }}
        />
      </div>
    );
  };

  const renderDetails = () => {
    if (!selectedAsset) {
      return (
        <div className="octave-details empty">
          <p>Select an asset, threat, or risk to view details</p>
        </div>
      );
    }

    return (
      <div className="octave-details">
        <div className="asset-detail">
          <h2>{selectedAsset.name}</h2>
          <div className="detail-grid">
            <div className="detail-section">
              <h3>Asset Information</h3>
              <p><strong>ID:</strong> {selectedAsset.id}</p>
              <p><strong>Type:</strong> {selectedAsset.type}</p>
              <p><strong>Criticality:</strong> {selectedAsset.criticality}</p>
              <p><strong>Owner:</strong> {selectedAsset.owner}</p>
              <p><strong>Description:</strong> {selectedAsset.description}</p>
              <p><strong>Business Rationale:</strong> {selectedAsset.rationale}</p>
            </div>

            <div className="detail-section">
              <h3>Security Requirements</h3>
              <div className="cia-requirements">
                <div className="cia-item">
                  <span className="cia-label">Confidentiality</span>
                  <span className={`cia-value ${selectedAsset.securityRequirements.confidentiality}`}>
                    {selectedAsset.securityRequirements.confidentiality}
                  </span>
                </div>
                <div className="cia-item">
                  <span className="cia-label">Integrity</span>
                  <span className={`cia-value ${selectedAsset.securityRequirements.integrity}`}>
                    {selectedAsset.securityRequirements.integrity}
                  </span>
                </div>
                <div className="cia-item">
                  <span className="cia-label">Availability</span>
                  <span className={`cia-value ${selectedAsset.securityRequirements.availability}`}>
                    {selectedAsset.securityRequirements.availability}
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>Asset Containers</h3>
              <div className="container-list">
                {selectedAsset.containers.map((container: string, idx: number) => (
                  <span key={idx} className="container-badge">{container}</span>
                ))}
              </div>
            </div>
          </div>

          {selectedThreat && (
            <div className="threat-detail">
              <h3>Selected Threat: {selectedThreat.id}</h3>
              <div className="threat-info">
                <p><strong>Source:</strong> {selectedThreat.source}</p>
                <p><strong>Actor:</strong> {selectedThreat.actor}</p>
                <p><strong>Means:</strong> {selectedThreat.means}</p>
                <p><strong>Motive:</strong> {selectedThreat.motive}</p>
                <p><strong>Outcome:</strong> {selectedThreat.outcome}</p>
                
                <div className="impact-matrix">
                  <h4>Impact Assessment</h4>
                  <div className="impact-grid">
                    {Object.entries(selectedThreat.impact).map(([category, score]) => (
                      <div key={category} className="impact-item">
                        <span className="impact-category">{category}</span>
                        <div className="impact-bar">
                          <div 
                            className={`impact-fill impact-${score}`} 
                            style={{ width: `${(score as number) * 20}%` }}
                          />
                        </div>
                        <span className="impact-score">{String(score)}/5</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="control-analysis">
                  <div className="current-controls">
                    <h4>Current Controls</h4>
                    <ul>
                      {selectedThreat.currentControls.map((control: string, idx: number) => (
                        <li key={idx}>{control}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="control-gaps">
                    <h4>Control Gaps</h4>
                    <ul className="gaps-list">
                      {selectedThreat.controlGaps.map((gap: string, idx: number) => (
                        <li key={idx} className="gap-item">{gap}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedRisk && (
            <div className="risk-detail">
              <h3>Risk Assessment: {selectedRisk.id}</h3>
              <div className="risk-info">
                <p><strong>Description:</strong> {selectedRisk.description}</p>
                <div className="risk-metrics">
                  <span className={`metric-badge ${selectedRisk.likelihood}`}>
                    Likelihood: {selectedRisk.likelihood}
                  </span>
                  <span className={`metric-badge ${selectedRisk.impact}`}>
                    Impact: {selectedRisk.impact}
                  </span>
                  <span className={`metric-badge risk-${selectedRisk.riskLevel}`}>
                    Risk Level: {selectedRisk.riskLevel}
                  </span>
                </div>
                <p><strong>Strategy:</strong> {selectedRisk.strategy}</p>
                {selectedRisk.mitigationPlan && (
                  <div className="mitigation-plan">
                    <h4>Mitigation Plan</h4>
                    <p>{selectedRisk.mitigationPlan}</p>
                  </div>
                )}
                {selectedRisk.residualRisk && (
                  <p><strong>Residual Risk:</strong> <span className={`risk-badge ${selectedRisk.residualRisk}`}>{selectedRisk.residualRisk}</span></p>
                )}
                <p><strong>Risk Owner:</strong> {selectedRisk.owner}</p>
                <p><strong>Review Date:</strong> {selectedRisk.reviewDate}</p>
              </div>
            </div>
          )}

          <div className="related-items">
            <div className="related-threats">
              <h3>Threats ({getThreatsByAsset(selectedAsset.id).length})</h3>
              <div className="threat-list">
                {getThreatsByAsset(selectedAsset.id).map(threat => (
                  <div 
                    key={threat.id}
                    className={`threat-item ${selectedThreat?.id === threat.id ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedThreat(threat);
                      onElementSelect?.(threat, 'octave-threat');
                    }}
                  >
                    <span className="threat-id">{threat.id}</span>
                    <span className="threat-source">{threat.source}</span>
                    <span className="threat-actor">{threat.actor}</span>
                    <span className={`probability-badge ${threat.probability}`}>
                      {threat.probability}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="related-vulnerabilities">
              <h3>Vulnerabilities ({getVulnerabilitiesByAsset(selectedAsset.id).length})</h3>
              <div className="vuln-list">
                {getVulnerabilitiesByAsset(selectedAsset.id).map(vuln => (
                  <div key={vuln.id} className="vuln-item">
                    <span className="vuln-id">{vuln.id}</span>
                    <span className="vuln-type">{vuln.type}</span>
                    <span className="vuln-desc">{vuln.description}</span>
                    <span className={`severity-badge ${vuln.severity}`}>
                      {vuln.severity}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="related-strategies">
              <h3>Protection Strategies</h3>
              <div className="strategy-list">
                {getStrategiesByAsset(selectedAsset.id).map(strategy => (
                  <div key={strategy.id} className="strategy-item">
                    <span className="strategy-name">{strategy.name}</span>
                    <span className={`strategy-type ${strategy.type}`}>{strategy.type}</span>
                    <span className={`effectiveness ${strategy.effectiveness}`}>
                      {strategy.effectiveness} effectiveness
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="octave-analysis">
      <p className="analysis-description">
        Operationally Critical Threat, Asset, and Vulnerability Evaluation - Risk-based strategic assessment
      </p>

      <div className="analysis-tabs">
        <button
          className={`tab-button ${activeTab === 'assets' ? 'active' : ''}`}
          onClick={() => setActiveTab('assets')}
        >
          Critical Assets
        </button>
        <button
          className={`tab-button ${activeTab === 'threats' ? 'active' : ''}`}
          onClick={() => setActiveTab('threats')}
        >
          Threats
        </button>
        <button
          className={`tab-button ${activeTab === 'vulnerabilities' ? 'active' : ''}`}
          onClick={() => setActiveTab('vulnerabilities')}
        >
          Vulnerabilities
        </button>
        <button
          className={`tab-button ${activeTab === 'risks' ? 'active' : ''}`}
          onClick={() => setActiveTab('risks')}
        >
          Risk Analysis
        </button>
        <button
          className={`tab-button ${activeTab === 'strategies' ? 'active' : ''}`}
          onClick={() => setActiveTab('strategies')}
        >
          Protection Strategies
        </button>
        <button
          className={`tab-button ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'assets' && renderAssets()}
        {activeTab === 'threats' && renderThreats()}
        {activeTab === 'vulnerabilities' && renderVulnerabilities()}
        {activeTab === 'risks' && renderRisks()}
        {activeTab === 'strategies' && renderStrategies()}
        {activeTab === 'details' && renderDetails()}
      </div>
    </div>
  );
}