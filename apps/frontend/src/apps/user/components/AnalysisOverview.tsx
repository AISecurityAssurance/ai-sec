import { Shield, Target, Activity, Brain, AlertTriangle, Eye, Layers, Search } from 'lucide-react';
import './AnalysisPanel.css';

interface AnalysisOverviewProps {
  enabledAnalyses: Record<string, boolean>;
}

const analysisInfo = {
  'stpa-sec': {
    name: 'STPA-Sec',
    icon: Shield,
    summary: 'System-Theoretic Process Analysis for Security',
    status: 'Complete',
    findings: { losses: 8, hazards: 12, ucas: 24, scenarios: 18 }
  },
  'stride': {
    name: 'STRIDE',
    icon: Target,
    summary: 'Threat modeling using Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation',
    status: 'In Progress',
    findings: { threats: 15, mitigated: 8, pending: 7 }
  },
  'pasta': {
    name: 'PASTA',
    icon: Activity,
    summary: 'Process for Attack Simulation and Threat Analysis',
    status: 'Complete',
    findings: { objectives: 4, scenarios: 5, critical: 2 }
  },
  'maestro': {
    name: 'MAESTRO',
    icon: Brain,
    summary: 'AI-specific threat modeling for agent systems',
    status: 'Not Started',
    findings: {}
  },
  'dread': {
    name: 'DREAD',
    icon: AlertTriangle,
    summary: 'Risk assessment scoring methodology',
    status: 'Complete',
    findings: { threats: 10, critical: 2, high: 6 }
  },
  'linddun': {
    name: 'LINDDUN',
    icon: Eye,
    summary: 'Privacy threat modeling framework',
    status: 'Not Started',
    findings: {}
  },
  'hazop': {
    name: 'HAZOP',
    icon: AlertTriangle,
    summary: 'Hazard and Operability Study',
    status: 'Not Started',
    findings: {}
  },
  'octave': {
    name: 'OCTAVE',
    icon: Layers,
    summary: 'Organizational risk assessment',
    status: 'Not Started',
    findings: {}
  },
  'cve': {
    name: 'CVE Search',
    icon: Search,
    summary: 'Vulnerability database search',
    status: 'Not Started',
    findings: {}
  }
};

export default function AnalysisOverview({ enabledAnalyses }: AnalysisOverviewProps) {
  const enabledCount = Object.values(enabledAnalyses).filter(v => v).length;
  const completedCount = Object.entries(enabledAnalyses)
    .filter(([id, enabled]) => enabled && analysisInfo[id]?.status === 'Complete')
    .length;

  return (
    <div className="analysis-overview">
      <div className="overview-header">
        <h2>Security Analysis Overview</h2>
        <p>Comprehensive view of all security analyses for the Digital Banking Platform</p>
      </div>

      <div className="overview-summary">
        <div className="summary-stat">
          <div className="stat-value">{enabledCount}</div>
          <div className="stat-label">Analyses Enabled</div>
        </div>
        <div className="summary-stat">
          <div className="stat-value">{completedCount}</div>
          <div className="stat-label">Completed</div>
        </div>
        <div className="summary-stat">
          <div className="stat-value">47</div>
          <div className="stat-label">Total Findings</div>
        </div>
        <div className="summary-stat critical">
          <div className="stat-value">8</div>
          <div className="stat-label">Critical Issues</div>
        </div>
      </div>

      <div className="analysis-grid">
        {Object.entries(analysisInfo).map(([id, info]) => {
          if (!enabledAnalyses[id]) return null;
          
          const Icon = info.icon;
          const statusClass = info.status.toLowerCase().replace(' ', '-');
          
          return (
            <div key={id} className={`analysis-card ${statusClass}`}>
              <div className="card-header">
                <Icon size={24} />
                <h3>{info.name}</h3>
                <span className={`status-indicator ${statusClass}`}>
                  {info.status}
                </span>
              </div>
              
              <p className="card-summary">{info.summary}</p>
              
              {Object.keys(info.findings).length > 0 && (
                <div className="card-findings">
                  {Object.entries(info.findings).map(([key, value]) => (
                    <div key={key} className="finding-stat">
                      <span className="finding-value">{value}</span>
                      <span className="finding-label">{key}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="recommendations-section">
        <h3>Recommendations</h3>
        <ul className="recommendations-list">
          <li>Complete MAESTRO analysis to address AI-specific threats in your system</li>
          <li>Run CVE search to identify known vulnerabilities in your technology stack</li>
          <li>Consider LINDDUN analysis for comprehensive privacy assessment</li>
          <li>Review and mitigate the 8 critical findings across completed analyses</li>
        </ul>
      </div>
    </div>
  );
}