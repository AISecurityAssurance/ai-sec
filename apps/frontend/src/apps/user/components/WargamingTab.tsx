import { useState } from 'react';
import { Shield, Target, AlertTriangle, TrendingUp } from 'lucide-react';
import './AnalysisPanel.css';

interface WargamingTabProps {
  scenarios: any[];
}

export default function WargamingTab({ scenarios }: WargamingTabProps) {
  const [selectedScenario, setSelectedScenario] = useState<any>(null);
  const [wargameMode, setWargameMode] = useState<'automated' | 'red-team' | 'blue-team' | 'training'>('automated');
  
  const renderAutomatedAnalysis = () => (
    <div className="automated-analysis">
      <h4>🤖 Automated Security Analysis</h4>
      <div className="analysis-steps">
        <div className="step">
          <h5>1. CVE Database Search</h5>
          <p>Searching for vulnerabilities related to: {selectedScenario?.causalFactors?.[0] || 'N/A'}</p>
          <p className="result">Found: CVE-2024-1234, CVE-2023-4567, CVE-2022-9876</p>
        </div>
        <div className="step">
          <h5>2. Attack Pattern Analysis</h5>
          <p>MITRE ATT&CK techniques identified:</p>
          <ul>
            <li>T1190 - Exploit Public-Facing Application</li>
            <li>T1078 - Valid Accounts</li>
            <li>T1055 - Process Injection</li>
          </ul>
        </div>
        <div className="step">
          <h5>3. Risk Assessment</h5>
          <p>Overall Risk Score: <span className="risk-score high">8.5/10</span></p>
          <p>Exploitability: High | Impact: Critical</p>
        </div>
        <div className="step">
          <h5>4. Recommended Mitigations</h5>
          <ul>
            <li>Apply security patches for identified CVEs</li>
            <li>Implement network segmentation</li>
            <li>Deploy endpoint detection and response (EDR)</li>
            <li>Enable multi-factor authentication</li>
          </ul>
        </div>
      </div>
    </div>
  );
  
  const renderRedTeamMode = () => (
    <div className="red-team-mode">
      <h4>🔴 Red Team Simulation</h4>
      <div className="attack-planning">
        <h5>Attack Objective</h5>
        <p>Exploit {selectedScenario?.description || 'selected vulnerability'} to gain unauthorized access</p>
        
        <h5>Attack Chain</h5>
        <ol>
          <li>Initial reconnaissance using OSINT tools</li>
          <li>Identify vulnerable endpoints through scanning</li>
          <li>Craft payload exploiting {selectedScenario?.causalFactors?.[0] || 'identified weakness'}</li>
          <li>Establish persistence through backdoor installation</li>
          <li>Exfiltrate sensitive data via encrypted channels</li>
        </ol>
        
        <h5>Required Resources</h5>
        <ul>
          <li>Attack infrastructure: $2,000/month</li>
          <li>Custom exploit development: 40 hours</li>
          <li>Social engineering campaign: $5,000</li>
          <li>Total estimated cost: $15,000</li>
        </ul>
        
        <h5>Success Indicators</h5>
        <ul>
          <li>Bypass authentication controls</li>
          <li>Access to sensitive customer data</li>
          <li>Maintain undetected presence for 30+ days</li>
        </ul>
      </div>
    </div>
  );
  
  const renderBlueTeamMode = () => (
    <div className="blue-team-mode">
      <h4>🔵 Blue Team Defense Strategy</h4>
      <div className="defense-planning">
        <h5>Threat Detection</h5>
        <ul>
          <li>Deploy SIEM rules for anomalous authentication patterns</li>
          <li>Implement behavioral analytics for insider threats</li>
          <li>Set up honeypots to detect lateral movement</li>
        </ul>
        
        <h5>Immediate Response Actions</h5>
        <ol>
          <li>Isolate affected systems from network</li>
          <li>Reset credentials for compromised accounts</li>
          <li>Block malicious IPs at firewall level</li>
          <li>Initiate incident response protocol</li>
        </ol>
        
        <h5>Preventive Measures</h5>
        <ul>
          <li>Patch management: Update all systems within 48 hours</li>
          <li>Access control: Implement least privilege principle</li>
          <li>Network segmentation: Isolate critical assets</li>
          <li>Security awareness: Conduct monthly training</li>
        </ul>
        
        <h5>Recovery Plan</h5>
        <ul>
          <li>Restore from secure backups if needed</li>
          <li>Forensic analysis to determine breach scope</li>
          <li>Update security policies based on lessons learned</li>
          <li>Communication plan for stakeholders</li>
        </ul>
      </div>
    </div>
  );
  
  const renderTrainingMode = () => (
    <div className="training-mode">
      <h4>🎓 Security Training Exercise</h4>
      <div className="training-scenario">
        <h5>Scenario Brief</h5>
        <p className="scenario-brief">
          You are the security analyst on duty. An alert has been triggered for:
          <br /><strong>{selectedScenario?.description || 'Suspicious activity detected'}</strong>
        </p>
        
        <h5>Your Task</h5>
        <ol>
          <li>Analyze the threat indicators</li>
          <li>Determine if this is a real attack or false positive</li>
          <li>Recommend appropriate response actions</li>
          <li>Document your findings</li>
        </ol>
        
        <h5>Available Information</h5>
        <ul>
          <li>Time of detection: 2:34 AM EST</li>
          <li>Source IP: 192.168.1.100 (internal)</li>
          <li>Affected systems: Authentication server, Database</li>
          <li>Anomaly: 500+ failed login attempts in 5 minutes</li>
        </ul>
        
        <h5>Decision Points</h5>
        <div className="decision-tree">
          <button className="decision-btn">🚨 Escalate to SOC Manager</button>
          <button className="decision-btn">🔍 Investigate Further</button>
          <button className="decision-btn">🚫 Block Source IP</button>
          <button className="decision-btn">📝 Mark as False Positive</button>
        </div>
        
        <h5>Learning Objectives</h5>
        <ul>
          <li>Recognize attack patterns</li>
          <li>Practice incident response procedures</li>
          <li>Improve decision-making under pressure</li>
          <li>Understand impact assessment</li>
        </ul>
      </div>
    </div>
  );
  
  return (
    <div className="wargaming-section">
      <div className="wargaming-header">
        <h3>Security Wargaming & Attack Simulation</h3>
        <p>Analyze causal scenarios through adversarial simulation to identify vulnerabilities and develop mitigations</p>
      </div>
      
      <div className="wargame-controls">
        <div className="mode-selector">
          <button 
            className={`mode-btn ${wargameMode === 'automated' ? 'active' : ''}`}
            onClick={() => setWargameMode('automated')}
          >
            <Shield size={16} />
            Automated Analysis
          </button>
          <button 
            className={`mode-btn ${wargameMode === 'red-team' ? 'active' : ''}`}
            onClick={() => setWargameMode('red-team')}
          >
            <Target size={16} />
            Red Team Mode
          </button>
          <button 
            className={`mode-btn ${wargameMode === 'blue-team' ? 'active' : ''}`}
            onClick={() => setWargameMode('blue-team')}
          >
            <Shield size={16} />
            Blue Team Mode
          </button>
          <button 
            className={`mode-btn ${wargameMode === 'training' ? 'active' : ''}`}
            onClick={() => setWargameMode('training')}
          >
            <TrendingUp size={16} />
            Training Mode
          </button>
        </div>
      </div>
      
      <div className="scenario-selector">
        <h4>Select Causal Scenario for Analysis</h4>
        <select 
          onChange={(e) => setSelectedScenario(scenarios.find(s => s.id === e.target.value))}
          className="scenario-select"
          value={selectedScenario?.id || ''}
        >
          <option value="">-- Select a scenario to analyze --</option>
          {scenarios.map(s => (
            <option key={s.id} value={s.id}>
              {s.id}: {s.description}
            </option>
          ))}
        </select>
      </div>
      
      {selectedScenario && (
        <div className="wargame-analysis">
          {wargameMode === 'automated' && renderAutomatedAnalysis()}
          {wargameMode === 'red-team' && renderRedTeamMode()}
          {wargameMode === 'blue-team' && renderBlueTeamMode()}
          {wargameMode === 'training' && renderTrainingMode()}
          
          <div className="scenario-details">
            <h5>Scenario Context</h5>
            <div className="context-grid">
              <div className="context-item">
                <span className="label">UCA Reference:</span>
                <span className="value">{selectedScenario.ucaId}</span>
              </div>
              <div className="context-item">
                <span className="label">Attack Vector:</span>
                <span className="value">{selectedScenario.causalFactors?.[0] || 'Multiple vectors'}</span>
              </div>
              <div className="context-item">
                <span className="label">Confidence:</span>
                <span className="value">{selectedScenario.confidence || 'Medium'}%</span>
              </div>
              <div className="context-item">
                <span className="label">STRIDE Category:</span>
                <span className="value">{selectedScenario.strideCategory || 'Multiple'}</span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {!selectedScenario && (
        <div className="wargame-placeholder">
          <AlertTriangle size={48} />
          <p>Select a causal scenario above to begin wargaming analysis</p>
          <p className="hint">Each scenario can be analyzed from different perspectives to develop comprehensive security strategies</p>
        </div>
      )}
    </div>
  );
}