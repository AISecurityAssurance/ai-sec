import React, { useState } from 'react';
import { X } from 'lucide-react';
import './NewAnalysisDialog.css';

interface NewAnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { description: string; frameworks: string[] }) => void;
}

const FRAMEWORKS = [
  { id: 'STPA_SEC', name: 'STPA-SEC', description: 'Systems-Theoretic Process Analysis for Security' },
  { id: 'STRIDE', name: 'STRIDE', description: 'Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation' },
  { id: 'PASTA', name: 'PASTA', description: 'Process for Attack Simulation and Threat Analysis' },
  { id: 'DREAD', name: 'DREAD', description: 'Damage, Reproducibility, Exploitability, Affected Users, Discoverability' },
  { id: 'MAESTRO', name: 'MAESTRO', description: 'AI/ML-specific security framework' },
  { id: 'LINDDUN', name: 'LINDDUN', description: 'Privacy threat modeling framework' },
  { id: 'HAZOP', name: 'HAZOP', description: 'Hazard and Operability Study' },
  { id: 'OCTAVE', name: 'OCTAVE', description: 'Operationally Critical Threat, Asset, and Vulnerability Evaluation' }
];

export function NewAnalysisDialog({ isOpen, onClose, onSubmit }: NewAnalysisDialogProps) {
  const [description, setDescription] = useState('');
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>([]);

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
            <label htmlFor="description">System Description</label>
            <textarea
              id="description"
              placeholder="Describe your system..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
              required
            />
          </div>

          <div className="form-group">
            <label>Select Frameworks</label>
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