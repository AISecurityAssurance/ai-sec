import React, { useState } from 'react';
import { X, FileText, Github, Globe, Upload, Folder, FolderOpen } from 'lucide-react';
import LoadAnalysisDialog from '../../../components/analysis/LoadAnalysisDialog';
import './NewAnalysisDialog.css';

interface NewAnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { 
    description: string; 
    frameworks: string[];
    inputType: 'text' | 'file' | 'repo' | 'url';
    inputSource?: string;
    files?: File[];
  }) => void;
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

export function NewAnalysisDialogEnhanced({ isOpen, onClose, onSubmit }: NewAnalysisDialogProps) {
  const [inputType, setInputType] = useState<'text' | 'file' | 'repo' | 'url'>('text');
  const [description, setDescription] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [docUrl, setDocUrl] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>([]);
  const [showLoadDialog, setShowLoadDialog] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    let isValid = false;
    const submitData: Parameters<typeof onSubmit>[0] = {
      description: '',
      frameworks: selectedFrameworks,
      inputType
    };
    
    switch (inputType) {
      case 'text':
        if (description.trim()) {
          submitData.description = description;
          isValid = true;
        }
        break;
      case 'file':
        if (selectedFiles.length > 0) {
          submitData.description = `Analysis of ${selectedFiles.length} file(s): ${selectedFiles.map(f => f.name).join(', ')}`;
          submitData.files = selectedFiles;
          isValid = true;
        }
        break;
      case 'repo':
        if (repoUrl.trim()) {
          submitData.description = `Analysis of repository: ${repoUrl}`;
          submitData.inputSource = repoUrl;
          isValid = true;
        }
        break;
      case 'url':
        if (docUrl.trim()) {
          submitData.description = `Analysis of documentation: ${docUrl}`;
          submitData.inputSource = docUrl;
          isValid = true;
        }
        break;
    }
    
    if (isValid && selectedFrameworks.length > 0) {
      onSubmit(submitData);
      handleClose();
    }
  };
  
  const handleClose = () => {
    setDescription('');
    setRepoUrl('');
    setDocUrl('');
    setSelectedFiles([]);
    setSelectedFrameworks([]);
    setInputType('text');
    onClose();
  };

  const toggleFramework = (frameworkId: string) => {
    setSelectedFrameworks(prev =>
      prev.includes(frameworkId)
        ? prev.filter(id => id !== frameworkId)
        : [...prev, frameworkId]
    );
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  return (
    <div className="dialog-overlay" onClick={handleClose}>
      <div className="dialog-content new-analysis-enhanced" onClick={e => e.stopPropagation()}>
        <div className="dialog-header">
          <h2>New Analysis</h2>
          <div className="dialog-header-actions">
            <button 
              type="button"
              className="load-existing-btn"
              onClick={() => setShowLoadDialog(true)}
              title="Load an existing analysis"
            >
              <FolderOpen size={16} />
              Load Existing
            </button>
            <button className="dialog-close" onClick={handleClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="dialog-body">
            {/* Input Type Selector */}
            <div className="input-type-selector">
              <button
                type="button"
                className={`input-type-btn ${inputType === 'text' ? 'active' : ''}`}
                onClick={() => setInputType('text')}
              >
                <FileText size={16} />
                <span>Text Description</span>
              </button>
              <button
                type="button"
                className={`input-type-btn ${inputType === 'file' ? 'active' : ''}`}
                onClick={() => setInputType('file')}
              >
                <Upload size={16} />
                <span>Upload Files</span>
              </button>
              <button
                type="button"
                className={`input-type-btn ${inputType === 'repo' ? 'active' : ''}`}
                onClick={() => setInputType('repo')}
              >
                <Github size={16} />
                <span>GitHub Repo</span>
              </button>
              <button
                type="button"
                className={`input-type-btn ${inputType === 'url' ? 'active' : ''}`}
                onClick={() => setInputType('url')}
              >
                <Globe size={16} />
                <span>Documentation URL</span>
              </button>
            </div>

            {/* Input Fields */}
            <div className="form-group">
              {inputType === 'text' && (
                <>
                  <label htmlFor="description">
                    System Description
                    <button 
                      type="button" 
                      className="demo-button"
                      onClick={() => {
                        setDescription(DEMO_SYSTEM);
                        setSelectedFrameworks(['stpa-sec', 'stride', 'pasta', 'dread']);
                      }}
                    >
                      Try Example System
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
                </>
              )}
              
              {inputType === 'file' && (
                <>
                  <label htmlFor="file-upload">
                    Upload System Documentation
                  </label>
                  <div className="file-upload-area">
                    <input
                      id="file-upload"
                      type="file"
                      multiple
                      accept=".txt,.md,.pdf,.doc,.docx,.yaml,.yml,.json"
                      onChange={handleFileChange}
                      style={{ display: 'none' }}
                    />
                    <label htmlFor="file-upload" className="file-upload-label">
                      <Folder size={48} />
                      <p>Click to browse or drag files here</p>
                      <span>Supported: TXT, MD, PDF, DOC, YAML, JSON</span>
                    </label>
                    {selectedFiles.length > 0 && (
                      <div className="selected-files">
                        <h4>Selected Files:</h4>
                        <ul>
                          {selectedFiles.map((file, idx) => (
                            <li key={idx}>
                              {file.name} ({(file.size / 1024).toFixed(1)} KB)
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </>
              )}
              
              {inputType === 'repo' && (
                <>
                  <label htmlFor="repo-url">
                    GitHub Repository URL
                  </label>
                  <input
                    id="repo-url"
                    type="url"
                    placeholder="https://github.com/username/repository"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    required
                  />
                  <p className="input-hint">
                    Enter the URL of a public GitHub repository to analyze its architecture and security
                  </p>
                </>
              )}
              
              {inputType === 'url' && (
                <>
                  <label htmlFor="doc-url">
                    Documentation URL
                  </label>
                  <input
                    id="doc-url"
                    type="url"
                    placeholder="https://example.com/docs"
                    value={docUrl}
                    onChange={(e) => setDocUrl(e.target.value)}
                    required
                  />
                  <p className="input-hint">
                    Enter the URL of system documentation or architecture diagrams
                  </p>
                </>
              )}
            </div>

            {/* Framework Selection */}
            <div className="form-group">
              <label>Select Analysis Frameworks</label>
              <div className="framework-grid">
                {FRAMEWORKS.map(framework => (
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
            </div>
          </div>

          <div className="dialog-footer">
            <button type="button" className="btn-secondary" onClick={handleClose}>
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-primary"
              disabled={selectedFrameworks.length === 0}
            >
              Start Analysis
            </button>
          </div>
        </form>
      </div>
      
      {/* Load Analysis Dialog */}
      <LoadAnalysisDialog
        isOpen={showLoadDialog}
        onClose={() => setShowLoadDialog(false)}
        onLoad={(analysisId) => {
          console.log('Loading analysis:', analysisId);
          // Close both dialogs and notify parent
          setShowLoadDialog(false);
          handleClose();
          // TODO: Implement actual loading logic
          alert(`Loading analysis ${analysisId}...`);
        }}
      />
    </div>
  );
}