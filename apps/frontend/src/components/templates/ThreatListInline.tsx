import { AlertTriangle, Shield, Target, X } from 'lucide-react';
import './ThreatListInline.css';

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

interface ThreatListInlineProps {
  title: string;
  threats: Threat[];
  onClose: () => void;
}

export function ThreatListInline({ title, threats, onClose }: ThreatListInlineProps) {
  const getRiskColor = (riskLevel: string | undefined) => {
    switch (riskLevel?.toLowerCase()) {
      case 'critical': return 'var(--risk-critical)';
      case 'high': return 'var(--risk-high)';
      case 'medium': return 'var(--risk-medium)';
      case 'low': return 'var(--risk-low)';
      default: return 'var(--text-secondary)';
    }
  };

  const getStatusIcon = (status: string | undefined) => {
    switch (status?.toLowerCase()) {
      case 'mitigated': return <Shield size={16} color="var(--success)" />;
      case 'mitigating': return <Target size={16} color="var(--warning)" />;
      default: return <AlertTriangle size={16} color="var(--danger)" />;
    }
  };

  return (
    <div className="threat-list-inline">
      <div className="threat-list-header">
        <h4>{title}</h4>
        <button onClick={onClose} className="close-btn" title="Close">
          <X size={16} />
        </button>
      </div>
      
      <div className="threat-list-summary">
        <p>Found {threats.length} threat{threats.length !== 1 ? 's' : ''} in this risk category</p>
      </div>
      
      <div className="threat-list-content">
        {threats.map((threat) => (
          <div key={threat.id} className="threat-card-inline">
            <div className="threat-card-header">
              <div className="threat-id-section">
                <span className="threat-id">{threat.id}</span>
                <span className="threat-type-badge">{threat.threatType}</span>
                {threat.status && (
                  <span className="threat-status-badge">
                    {getStatusIcon(threat.status)}
                    <span>{threat.status}</span>
                  </span>
                )}
              </div>
              {threat.riskLevel && (
                <div 
                  className="threat-risk-level"
                  style={{ 
                    backgroundColor: getRiskColor(threat.riskLevel),
                    color: 'white'
                  }}
                >
                  {threat.riskLevel.toUpperCase()}
                </div>
              )}
            </div>
            
            <div className="threat-card-body">
              <div className="threat-field">
                <span className="threat-label">Component:</span>
                <span className="threat-value">{threat.component}</span>
              </div>
              <div className="threat-field">
                <span className="threat-label">Threat:</span>
                <span className="threat-value">{threat.description}</span>
              </div>
              <div className="threat-field">
                <span className="threat-label">Impact:</span>
                <span className="threat-value">{threat.impact}</span>
              </div>
              
              {threat.mitigations && threat.mitigations.length > 0 && (
                <div className="threat-mitigations">
                  <span className="threat-label">Mitigations:</span>
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
  );
}