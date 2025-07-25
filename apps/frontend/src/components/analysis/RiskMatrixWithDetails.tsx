import { useState } from 'react';
import { ThreatListInline } from '../templates';

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

interface RiskMatrixWithDetailsProps {
  threats: Threat[];
  onSave: (id: string, data: any) => void;
}

export function RiskMatrixWithDetails({ threats, onSave }: RiskMatrixWithDetailsProps) {
  const [selectedRiskCell, setSelectedRiskCell] = useState<{ title: string; threats: Threat[] } | null>(null);

  // Calculate threat counts for each cell
  const threatsByRisk = threats.reduce((acc, threat) => {
    const key = `${threat.likelihood}-${threat.impact}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(threat);
    return acc;
  }, {} as Record<string, Threat[]>);

  const getCellColor = (likelihood: string, impact: string) => {
    if (likelihood === 'high' && (impact === 'high' || impact === 'critical')) return 'var(--risk-critical, #ff4444)';
    if ((likelihood === 'high' && impact === 'medium') || (likelihood === 'medium' && (impact === 'high' || impact === 'critical'))) return 'var(--risk-high, #ff9944)';
    if ((likelihood === 'medium' && impact === 'medium') || (likelihood === 'low' && (impact === 'high' || impact === 'critical'))) return 'var(--risk-medium, #ffdd44)';
    return 'var(--risk-low, #44ff44)';
  };

  return (
    <>
      <div style={{ marginTop: '20px' }}>
        {/* Header row */}
        <div style={{ display: 'grid', gridTemplateColumns: '120px repeat(4, 1fr)', gap: '2px', marginBottom: '2px' }}>
          <div></div>
          <div style={{ textAlign: 'center', fontWeight: 'bold', padding: '8px', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)' }}>
            Low Impact
          </div>
          <div style={{ textAlign: 'center', fontWeight: 'bold', padding: '8px', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)' }}>
            Medium Impact
          </div>
          <div style={{ textAlign: 'center', fontWeight: 'bold', padding: '8px', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)' }}>
            High Impact
          </div>
          <div style={{ textAlign: 'center', fontWeight: 'bold', padding: '8px', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)' }}>
            Critical Impact
          </div>
        </div>
        
        {/* Risk matrix rows */}
        {['high', 'medium', 'low'].map(likelihood => {
          const likelihoodLabel = likelihood.charAt(0).toUpperCase() + likelihood.slice(1);
          return (
            <div key={likelihood} style={{ display: 'grid', gridTemplateColumns: '120px repeat(4, 1fr)', gap: '2px', marginBottom: '2px' }}>
              <div style={{ 
                fontWeight: 'bold', 
                display: 'flex', 
                alignItems: 'center',
                padding: '8px',
                backgroundColor: 'var(--bg-secondary)',
                color: 'var(--text-primary)'
              }}>
                {likelihoodLabel} Likelihood
              </div>
              {['low', 'medium', 'high', 'critical'].map(impact => {
                const cellThreats = threatsByRisk[`${likelihood}-${impact}`] || [];
                const cellColor = getCellColor(likelihood, impact);
                
                return (
                  <div
                    key={`${likelihood}-${impact}`}
                    style={{
                      backgroundColor: cellColor,
                      padding: '10px',
                      border: '1px solid var(--border-color)',
                      minHeight: '80px',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: cellThreats.length > 0 ? 'pointer' : 'default',
                      transition: 'opacity 0.2s',
                      opacity: cellThreats.length > 0 ? 1 : 0.6
                    }}
                    onMouseEnter={(e) => {
                      if (cellThreats.length > 0) {
                        e.currentTarget.style.opacity = '0.8';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.opacity = cellThreats.length > 0 ? '1' : '0.6';
                    }}
                    onClick={() => {
                      if (cellThreats.length > 0) {
                        setSelectedRiskCell({
                          title: `${likelihoodLabel} Likelihood / ${impact.charAt(0).toUpperCase() + impact.slice(1)} Impact Threats`,
                          threats: cellThreats
                        });
                      }
                    }}
                  >
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'white' }}>{cellThreats.length}</div>
                    {cellThreats.length > 0 && (
                      <div style={{ fontSize: '12px', marginTop: '5px', color: 'white' }}>Click for details</div>
                    )}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
      
      {/* Risk matrix legend */}
      <div style={{ marginTop: '20px' }}>
        <h5 style={{ color: 'var(--text-primary)' }}>Risk Matrix Legend:</h5>
        <div style={{ display: 'flex', gap: '20px', marginTop: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: 'var(--risk-critical, #ff4444)', border: '1px solid var(--border-color)' }}></div>
            <span style={{ color: 'var(--text-primary)' }}>Critical Risk</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: 'var(--risk-high, #ff9944)', border: '1px solid var(--border-color)' }}></div>
            <span style={{ color: 'var(--text-primary)' }}>High Risk</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: 'var(--risk-medium, #ffdd44)', border: '1px solid var(--border-color)' }}></div>
            <span style={{ color: 'var(--text-primary)' }}>Medium Risk</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: 'var(--risk-low, #44ff44)', border: '1px solid var(--border-color)' }}></div>
            <span style={{ color: 'var(--text-primary)' }}>Low Risk</span>
          </div>
        </div>
      </div>
      
      {selectedRiskCell && (
        <ThreatListInline
          title={selectedRiskCell.title}
          threats={selectedRiskCell.threats}
          onClose={() => setSelectedRiskCell(null)}
        />
      )}
    </>
  );
}