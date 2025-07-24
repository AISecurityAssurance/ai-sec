import { useState } from 'react';
import { X } from 'lucide-react';
import { useAnalysisStore } from '../../stores/analysisStore';
import './AddAnalysisDialog.css';

interface AddAnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (frameworks: string[]) => void;
  completedFrameworks: string[];
}

const frameworks = [
  { id: 'stpa-sec', name: 'STPA-Sec', description: 'Systems Theoretic Process Analysis for Security' },
  { id: 'stride', name: 'STRIDE', description: 'Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation' },
  { id: 'pasta', name: 'PASTA', description: 'Process for Attack Simulation and Threat Analysis' },
  { id: 'dread', name: 'DREAD', description: 'Damage, Reproducibility, Exploitability, Affected Users, Discoverability' },
  { id: 'maestro', name: 'MAESTRO', description: 'AI/ML-specific security framework' },
  { id: 'linddun', name: 'LINDDUN', description: 'Privacy threat modeling framework' },
  { id: 'hazop', name: 'HAZOP', description: 'Hazard and Operability Study' },
  { id: 'octave', name: 'OCTAVE', description: 'Operationally Critical Threat, Asset, and Vulnerability Evaluation' }
];

export function AddAnalysisDialog({ isOpen, onClose, onSubmit, completedFrameworks }: AddAnalysisDialogProps) {
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>([]);
  
  if (!isOpen) return null;
  
  const availableFrameworks = frameworks.filter(f => !completedFrameworks.includes(f.id));
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFrameworks.length > 0) {
      onSubmit(selectedFrameworks);
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
      <div className="dialog-content add-analysis-dialog" onClick={e => e.stopPropagation()}>
        <div className="dialog-header">
          <h2>Add Security Analysis</h2>
          <button className="dialog-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Select Additional Analyses to Run</label>
            {availableFrameworks.length === 0 ? (
              <p className="no-frameworks">All available analyses have been completed.</p>
            ) : (
              <div className="frameworks-list">
                {availableFrameworks.map(framework => (
                  <label key={framework.id} className="framework-option">
                    <input
                      type="checkbox"
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
            )}
          </div>
          
          <div className="dialog-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-primary"
              disabled={selectedFrameworks.length === 0}
            >
              Run Analysis ({selectedFrameworks.length})
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}