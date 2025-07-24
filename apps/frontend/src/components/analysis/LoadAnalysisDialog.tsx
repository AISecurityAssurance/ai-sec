import { useState, useEffect } from 'react';
import { FolderOpen, X, Clock, FileText, Search } from 'lucide-react';
import './Dialog.css';

interface SavedAnalysis {
  id: string;
  name: string;
  description?: string;
  frameworks: string[];
  createdAt: string;
  updatedAt: string;
}

interface LoadAnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onLoad: (analysisId: string) => void;
}

// Mock saved analyses for demo
const mockSavedAnalyses: SavedAnalysis[] = [
  {
    id: 'analysis-1',
    name: 'E-commerce Platform Security Review',
    description: 'Comprehensive security analysis of payment processing and user data handling',
    frameworks: ['stpa-sec', 'stride', 'pasta'],
    createdAt: '2025-01-20T10:30:00Z',
    updatedAt: '2025-01-20T14:45:00Z'
  },
  {
    id: 'analysis-2',
    name: 'Mobile Banking App Threat Model',
    description: 'Security assessment focusing on authentication and transaction integrity',
    frameworks: ['stride', 'dread', 'linddun'],
    createdAt: '2025-01-18T09:00:00Z',
    updatedAt: '2025-01-19T16:20:00Z'
  },
  {
    id: 'analysis-3',
    name: 'IoT Device Firmware Analysis',
    frameworks: ['hazop', 'octave', 'maestro'],
    createdAt: '2025-01-15T13:15:00Z',
    updatedAt: '2025-01-15T17:30:00Z'
  }
];

export default function LoadAnalysisDialog({ isOpen, onClose, onLoad }: LoadAnalysisDialogProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null);
  const [savedAnalyses, setSavedAnalyses] = useState<SavedAnalysis[]>([]);
  
  useEffect(() => {
    if (isOpen) {
      // In real implementation, fetch from backend
      setSavedAnalyses(mockSavedAnalyses);
    }
  }, [isOpen]);
  
  const filteredAnalyses = savedAnalyses.filter(analysis =>
    analysis.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    analysis.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    analysis.frameworks.some(fw => fw.toLowerCase().includes(searchTerm.toLowerCase()))
  );
  
  const handleLoad = () => {
    if (selectedAnalysis) {
      onLoad(selectedAnalysis);
      handleClose();
    }
  };
  
  const handleClose = () => {
    setSearchTerm('');
    setSelectedAnalysis(null);
    onClose();
  };
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="dialog-overlay" onClick={handleClose}>
      <div className="dialog-content load-dialog" onClick={e => e.stopPropagation()}>
        <div className="dialog-header">
          <h2>Load Existing Analysis</h2>
          <button className="dialog-close" onClick={handleClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="dialog-body">
          <div className="search-wrapper">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Search analyses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="analyses-list">
            {filteredAnalyses.length === 0 ? (
              <div className="empty-state">
                <FileText size={48} />
                <p>No saved analyses found</p>
              </div>
            ) : (
              filteredAnalyses.map(analysis => (
                <div
                  key={analysis.id}
                  className={`analysis-item ${selectedAnalysis === analysis.id ? 'selected' : ''}`}
                  onClick={() => setSelectedAnalysis(analysis.id)}
                >
                  <div className="analysis-header">
                    <h3>{analysis.name}</h3>
                    <div className="analysis-meta">
                      <Clock size={14} />
                      <span>{formatDate(analysis.updatedAt)}</span>
                    </div>
                  </div>
                  
                  {analysis.description && (
                    <p className="analysis-description">{analysis.description}</p>
                  )}
                  
                  <div className="analysis-frameworks">
                    {analysis.frameworks.map(fw => (
                      <span key={fw} className="framework-tag">
                        {fw.toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        
        <div className="dialog-footer">
          <button type="button" className="btn-secondary" onClick={handleClose}>
            Cancel
          </button>
          <button 
            type="button" 
            className="btn-primary" 
            onClick={handleLoad}
            disabled={!selectedAnalysis}
          >
            <FolderOpen size={16} />
            Load Analysis
          </button>
        </div>
      </div>
    </div>
  );
}