import { X, AlertTriangle, Shield, Target } from 'lucide-react';
import './AnalysisDetail.css';

interface Threat {
  id: string;
  component: string;
  threatType: string;
  description: string;
  impact: string;
  likelihood: string;
  riskLevel?: string;
  status?: string;
  mitigations?: string[];
}

interface ThreatListDetailProps {
  title: string;
  threats: Threat[];
  onClose: () => void;
}

export function ThreatListDetail({ title, threats, onClose }: ThreatListDetailProps) {
  const getRiskColor = (riskLevel: string | undefined) => {
    switch (riskLevel?.toLowerCase()) {
      case 'critical': return '#ff4444';
      case 'high': return '#ff9944';
      case 'medium': return '#ffdd44';
      case 'low': return '#44ff44';
      default: return '#999999';
    }
  };

  const getStatusIcon = (status: string | undefined) => {
    switch (status?.toLowerCase()) {
      case 'mitigated': return <Shield size={16} color="#44ff44" />;
      case 'mitigating': return <Target size={16} color="#ffdd44" />;
      default: return <AlertTriangle size={16} color="#ff9944" />;
    }
  };

  return (
    <div className="analysis-detail-overlay" onClick={onClose}>
      <div className="analysis-detail threat-list-detail" onClick={(e) => e.stopPropagation()}>
        <div className="analysis-detail-header">
          <h2>{title}</h2>
          <div className="analysis-detail-actions">
            <button onClick={onClose} className="icon-button" title="Close">
              <X size={18} />
            </button>
          </div>
        </div>
        
        <div className="analysis-detail-content">
          <div className="threat-summary">
            <p>Found {threats.length} threat{threats.length !== 1 ? 's' : ''} in this risk category</p>
          </div>
          
          <div className="threat-list">
            {threats.map((threat) => (
              <div key={threat.id} className="threat-card">
                <div className="threat-header">
                  <div className="threat-id-section">
                    <span className="threat-id">{threat.id}</span>
                    <span className="threat-type">{threat.threatType}</span>
                    {threat.status && (
                      <span className="threat-status">
                        {getStatusIcon(threat.status)}
                        {threat.status}
                      </span>
                    )}
                  </div>
                  {threat.riskLevel && (
                    <div 
                      className="threat-risk-badge"
                      style={{ backgroundColor: getRiskColor(threat.riskLevel) }}
                    >
                      {threat.riskLevel.toUpperCase()}
                    </div>
                  )}
                </div>
                
                <div className="threat-body">
                  <div className="threat-component">
                    <strong>Component:</strong> {threat.component}
                  </div>
                  <div className="threat-description">
                    <strong>Threat:</strong> {threat.description}
                  </div>
                  <div className="threat-impact">
                    <strong>Impact:</strong> {threat.impact}
                  </div>
                  
                  {threat.mitigations && threat.mitigations.length > 0 && (
                    <div className="threat-mitigations">
                      <strong>Mitigations:</strong>
                      <ul>
                        {threat.mitigations.map((mitigation, idx) => (
                          <li key={idx}>{mitigation}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Add these styles to the existing AnalysisDetail.css or create a new file
const additionalStyles = `
.threat-list-detail {
  max-width: 900px;
}

.threat-summary {
  padding: var(--space-3);
  background: var(--surface);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-4);
}

.threat-summary p {
  margin: 0;
  color: var(--text-secondary);
}

.threat-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.threat-card {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: var(--surface);
  transition: box-shadow 0.2s ease;
}

.threat-card:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.threat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--border-light);
}

.threat-id-section {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.threat-id {
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.threat-type {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  background: var(--background);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.threat-status {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-sm);
  color: var(--text-secondary);
  text-transform: capitalize;
}

.threat-risk-badge {
  padding: 4px 12px;
  border-radius: var(--radius-sm);
  font-size: var(--font-sm);
  font-weight: 600;
  color: white;
}

.threat-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.threat-component,
.threat-description,
.threat-impact {
  color: var(--text-primary);
  line-height: 1.5;
}

.threat-component strong,
.threat-description strong,
.threat-impact strong,
.threat-mitigations strong {
  color: var(--text-secondary);
  font-weight: 600;
  margin-right: var(--space-2);
}

.threat-mitigations ul {
  margin: var(--space-2) 0 0 var(--space-4);
  padding: 0;
  list-style-type: disc;
}

.threat-mitigations li {
  margin-bottom: var(--space-1);
  color: var(--text-primary);
}
`;