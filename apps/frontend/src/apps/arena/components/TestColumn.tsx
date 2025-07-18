import './ArenaComponents.css';

interface TestColumnProps {
  variant: string;
  label: string;
  isRunning: boolean;
  isExperimental?: boolean;
}

export default function TestColumn({ variant, label, isRunning, isExperimental }: TestColumnProps) {
  const metrics = isExperimental ? {
    completeness: 98,
    time: 3.2,
    accuracy: 94,
    cost: 0.12,
  } : {
    completeness: 92,
    time: 2.1,
    accuracy: 88,
    cost: 0.08,
  };

  return (
    <div className="test-column">
      <div className="variant-header">
        <h3>Variant {variant}</h3>
        <span className={`variant-badge ${isExperimental ? 'experimental' : ''}`}>
          {label}
        </span>
      </div>
      
      <div className="test-controls">
        <button className="btn btn-sm btn-secondary">Re-run</button>
        <button className="btn btn-sm btn-secondary">Export</button>
      </div>
      
      <div className="test-output">
        {isRunning ? (
          <div className="analyzing-state">
            <div className="spinner" />
            <p>Running analysis...</p>
          </div>
        ) : (
          <>
            <div className="output-header">== STPA-Sec Analysis ==</div>
            <div className="output-section">
              <div>Losses Identified: {isExperimental ? 5 : 3}</div>
              <div>- L1: Financial data breach</div>
              <div>- L2: Service unavailability</div>
              <div>- L3: Regulatory non-compliance</div>
              {isExperimental && (
                <>
                  <div>- L4: Reputation damage</div>
                  <div>- L5: Operational disruption</div>
                </>
              )}
            </div>
            <div className="output-section">
              <div>Hazards Identified: {isExperimental ? 12 : 7}</div>
              <div>- H1: SQL injection vulnerability</div>
              <div>- H2: Weak authentication</div>
              <div>- H3: Unencrypted data transmission</div>
              {isExperimental && (
                <>
                  <div>- H4: Session hijacking</div>
                  <div>- H5: API rate limit bypass</div>
                  <div>- H6: Insufficient input validation</div>
                  <div>- H7: Missing security headers</div>
                  <div>- H8: Insecure direct object references</div>
                  <div>- H9: Cross-site scripting (XSS)</div>
                  <div>- H10: Broken access control</div>
                  <div>- H11: Security misconfiguration</div>
                  <div>- H12: Using components with known vulnerabilities</div>
                </>
              )}
              {!isExperimental && (
                <>
                  <div>- H4: Missing rate limiting</div>
                  <div>- H5: Weak session management</div>
                  <div>- H6: Improper error handling</div>
                  <div>- H7: Insufficient logging</div>
                </>
              )}
            </div>
            
            <div className="output-section">
              <div className="output-header">== STRIDE Analysis ==</div>
              <div>Threats Identified: {isExperimental ? 15 : 9}</div>
              <div>- Spoofing: 3 vulnerabilities</div>
              <div>- Tampering: 2 vulnerabilities</div>
              <div>- Repudiation: 1 vulnerability</div>
              <div>- Information Disclosure: 4 vulnerabilities</div>
              <div>- Denial of Service: 2 vulnerabilities</div>
              <div>- Elevation of Privilege: {isExperimental ? 3 : 1} vulnerabilities</div>
            </div>
            
            <div className="output-section">
              <div className="output-header">== Detailed Findings ==</div>
              <div>Critical Security Issues:</div>
              <div>1. Authentication bypass via JWT manipulation</div>
              <div>2. SQL injection in user search endpoint</div>
              <div>3. Unencrypted PII in database</div>
              <div>4. Missing CSRF protection on state-changing operations</div>
              {isExperimental && (
                <>
                  <div>5. XML External Entity (XXE) vulnerability</div>
                  <div>6. Server-Side Request Forgery (SSRF) in webhook handler</div>
                  <div>7. Insecure deserialization in API endpoints</div>
                  <div>8. Path traversal vulnerability in file upload</div>
                </>
              )}
            </div>
          </>
        )}
      </div>
      
      <div className="metrics-row compact">
        <div className="mini-metric">
          <span className="metric-label">Completeness:</span>
          <span className={`metric-value ${isExperimental ? 'better' : ''}`}>
            {metrics.completeness}%
          </span>
        </div>
        <div className="mini-metric">
          <span className="metric-label">Accuracy:</span>
          <span className={`metric-value ${isExperimental ? 'better' : ''}`}>
            {metrics.accuracy}%
          </span>
        </div>
      </div>
    </div>
  );
}