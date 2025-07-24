import { useState } from 'react';
import { Save, X } from 'lucide-react';
import { useAnalysisStore } from '../../stores/analysisStore';
import './Dialog.css';

interface SaveAnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, description?: string) => void;
}

export default function SaveAnalysisDialog({ isOpen, onClose, onSave }: SaveAnalysisDialogProps) {
  const { currentAnalysisId, analysisResults } = useAnalysisStore();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  
  const completedFrameworks = Object.keys(analysisResults)
    .filter(fw => analysisResults[fw]?.status?.status === 'completed');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onSave(name.trim(), description.trim() || undefined);
      handleClose();
    }
  };
  
  const handleClose = () => {
    setName('');
    setDescription('');
    onClose();
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="dialog-overlay" onClick={handleClose}>
      <div className="dialog-content" onClick={e => e.stopPropagation()}>
        <div className="dialog-header">
          <h2>Save Analysis</h2>
          <button className="dialog-close" onClick={handleClose}>
            <X size={20} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="dialog-body">
            <div className="form-group">
              <label htmlFor="analysis-name">Analysis Name *</label>
              <input
                id="analysis-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., E-commerce Security Analysis"
                required
                autoFocus
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="analysis-description">Description</label>
              <textarea
                id="analysis-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional description of this analysis..."
                rows={3}
              />
            </div>
            
            <div className="save-info">
              <p className="info-text">
                This will save the following completed analyses:
              </p>
              <ul className="framework-list">
                {completedFrameworks.map(fw => (
                  <li key={fw}>{fw.toUpperCase()}</li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="dialog-footer">
            <button type="button" className="btn-secondary" onClick={handleClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={!name.trim()}>
              <Save size={16} />
              Save Analysis
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}