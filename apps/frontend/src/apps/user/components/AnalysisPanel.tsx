import { useState } from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';
import './AnalysisPanel.css';

interface AnalysisPanelProps {
  activeAnalysis: string;
  onAnalysisChange: (analysis: string) => void;
  isAnalyzing: boolean;
}

const mockLosses = [
  {
    id: 'L1',
    description: 'Financial data breach leading to customer financial loss',
    severity: 'high' as const,
  },
  {
    id: 'L2',
    description: 'Service unavailability affecting customer transactions',
    severity: 'medium' as const,
  },
  {
    id: 'L3',
    description: 'Regulatory compliance violations resulting in fines',
    severity: 'high' as const,
  },
  {
    id: 'L4',
    description: 'Reputational damage from security incidents',
    severity: 'medium' as const,
  },
  {
    id: 'L5',
    description: 'Intellectual property theft affecting competitive advantage',
    severity: 'high' as const,
  },
];

const mockHazards = [
  {
    id: 'H1',
    description: 'Unauthorized access to customer financial data',
    severity: 'high' as const,
    relatedLosses: ['L1'],
  },
  {
    id: 'H2',
    description: 'System overload causing service disruption',
    severity: 'medium' as const,
    relatedLosses: ['L2'],
  },
  {
    id: 'H3',
    description: 'Inadequate logging preventing incident investigation',
    severity: 'medium' as const,
    relatedLosses: ['L3'],
  },
  {
    id: 'H4',
    description: 'Weak authentication mechanisms allowing impersonation',
    severity: 'high' as const,
    relatedLosses: ['L1', 'L4'],
  },
  {
    id: 'H5',
    description: 'Unencrypted data transmission exposing sensitive information',
    severity: 'high' as const,
    relatedLosses: ['L1', 'L5'],
  },
  {
    id: 'H6',
    description: 'Insufficient access controls on critical resources',
    severity: 'high' as const,
    relatedLosses: ['L1', 'L3', 'L5'],
  },
];

export default function AnalysisPanel({ activeAnalysis, onAnalysisChange, isAnalyzing }: AnalysisPanelProps) {
  const [activeTab, setActiveTab] = useState('stpa-sec');

  const tabs = [
    { id: 'stpa-sec', label: 'STPA-Sec' },
    { id: 'stride', label: 'STRIDE' },
    { id: 'overview', label: 'Overview' },
  ];

  return (
    <main className="analysis-panel">
      <div className="tabs">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => {
              setActiveTab(tab.id);
              onAnalysisChange(tab.id);
            }}
          >
            {tab.label}
          </div>
        ))}
      </div>
      
      <div className="analysis-content">
        {isAnalyzing ? (
          <div className="analyzing-state">
            <div className="analyzing-spinner" />
            <p>Analyzing your system...</p>
            <div className="progress-bar mt-4">
              <div className="progress-fill" style={{ width: '40%' }} />
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'stpa-sec' && (
              <>
                <div className="analysis-section">
                  <h3 className="section-header">
                    <AlertTriangle size={20} className="text-error" />
                    Identified Losses
                  </h3>
                  {mockLosses.map(loss => (
                    <div key={loss.id} className="finding-card">
                      <div className="finding-header">
                        <span className="finding-id">{loss.id}</span>
                        <span className={`badge badge-${loss.severity === 'high' ? 'error' : 'warning'}`}>
                          {loss.severity.toUpperCase()}
                        </span>
                      </div>
                      <p className="finding-description">{loss.description}</p>
                      <div className="action-buttons">
                        <button className="btn btn-sm btn-secondary">
                          Refine
                        </button>
                        <button className="btn btn-sm btn-secondary">
                          Explore Impact
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="analysis-section mt-8">
                  <h3 className="section-header">
                    <ShieldAlert size={20} className="text-warning" />
                    Security Hazards
                  </h3>
                  {mockHazards.map(hazard => (
                    <div key={hazard.id} className="finding-card">
                      <div className="finding-header">
                        <span className="finding-id">{hazard.id}</span>
                        <span className={`badge badge-${hazard.severity === 'high' ? 'error' : 'warning'}`}>
                          {hazard.severity.toUpperCase()}
                        </span>
                      </div>
                      <p className="finding-description">{hazard.description}</p>
                      <div className="finding-meta">
                        Related to: {hazard.relatedLosses.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
            
            {activeTab === 'stride' && (
              <div className="analysis-section">
                <h3>STRIDE Analysis</h3>
                <p className="text-secondary">STRIDE analysis results will appear here...</p>
              </div>
            )}
            
            {activeTab === 'overview' && (
              <div className="analysis-section">
                <h3>Analysis Overview</h3>
                <p className="text-secondary">Combined analysis overview will appear here...</p>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}