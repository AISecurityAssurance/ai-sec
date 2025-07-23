import React, { useState } from 'react';
import { X } from 'lucide-react';
import './NewAnalysisDialog.css';

interface NewAnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { description: string; frameworks: string[] }) => void;
}

const FRAMEWORKS = [
  { id: 'stpa-sec', name: 'STPA-SEC', description: 'Systems-Theoretic Process Analysis for Security' },
  { id: 'stride', name: 'STRIDE', description: 'Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation' },
  { id: 'pasta', name: 'PASTA', description: 'Process for Attack Simulation and Threat Analysis' },
  { id: 'dread', name: 'DREAD', description: 'Damage, Reproducibility, Exploitability, Affected Users, Discoverability' },
  { id: 'maestro', name: 'MAESTRO', description: 'AI/ML-specific security framework' },
  { id: 'linddun', name: 'LINDDUN', description: 'Privacy threat modeling framework' },
  { id: 'hazop', name: 'HAZOP', description: 'Hazard and Operability Study' },
  { id: 'octave', name: 'OCTAVE', description: 'Operationally Critical Threat, Asset, and Vulnerability Evaluation' }
];

const DEMO_SYSTEM = `An integrated financial services platform that provides online banking, investment management, and payment processing services. The system consists of:

1. Web and mobile applications for customer access
2. Core banking services handling accounts, transactions, and balances
3. Investment portfolio management with real-time market data integration
4. Payment gateway supporting multiple payment methods and currencies
5. Customer data analytics for personalized financial insights
6. Third-party integrations with credit bureaus, payment networks, and market data providers

The platform serves 2 million active users and processes over $50M in daily transactions. Security and regulatory compliance are critical requirements.`;

export function NewAnalysisDialog({ isOpen, onClose, onSubmit }: NewAnalysisDialogProps) {
  const [description, setDescription] = useState('');
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>([]);
  const [showDemo, setShowDemo] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (description.trim() && selectedFrameworks.length > 0) {
      onSubmit({ description, frameworks: selectedFrameworks });
      setDescription('');
      setSelectedFrameworks([]);
      onClose();
    }
  };

  const toggleFramework = (frameworkId: string) => {
    setSelectedFrameworks(prev =>
      prev.includes(frameworkId)
        ? prev.filter(id => id !== frameworkId)
        : [...prev, frameworkId]
    );
  };

  return (
    <div className="dialog-overlay" onClick={onClose}>
      <div className="dialog-content" onClick={e => e.stopPropagation()}>
        <div className="dialog-header">
          <h2>New Analysis</h2>
          <button className="dialog-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="description">
              System Description
              <button 
                type="button" 
                className="demo-button"
                onClick={() => {
                  setDescription(DEMO_SYSTEM);
                  setSelectedFrameworks(['stpa-sec', 'stride', 'pasta', 'dread']);
                }}
                style={{
                  marginLeft: '10px',
                  fontSize: '12px',
                  padding: '4px 8px',
                  background: 'var(--bg-hover)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  color: 'var(--text-secondary)'
                }}
              >
                Load Demo System
              </button>
            </label>
            <textarea
              id="description"
              placeholder="Describe your system architecture, components, boundaries, and security requirements..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={8}
              required
            />
          </div>

          <div className="form-group">
            <label>
              Select Analysis Frameworks
              <span style={{ marginLeft: '10px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                (Choose one or more)
              </span>
            </label>
            <div className="frameworks-grid">
              {FRAMEWORKS.map(framework => (
                <label key={framework.id} className="framework-checkbox">
                  <input
                    type="checkbox"
                    value={framework.id}
                    checked={selectedFrameworks.includes(framework.id)}
                    onChange={() => toggleFramework(framework.id)}
                  />
                  <div className="framework-info">
                    <span className="framework-name">{framework.name}</span>
                    <span className="framework-desc">{framework.description}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="dialog-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-primary"
              disabled={!description.trim() || selectedFrameworks.length === 0}
            >
              Start Analysis
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}