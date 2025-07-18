import { useState, useEffect } from 'react';
import { FileText, Folder, FileCode, Upload, Shield, Target, Search, Eye, Brain, Activity, Lock, AlertTriangle, Users, Layers, Info } from 'lucide-react';
import './Sidebar.css';

const mockFiles = [
  { id: '1', name: 'banking_system.txt', type: 'text', icon: FileText },
  { id: '2', name: 'src/', type: 'folder', icon: Folder },
  { id: '3', name: 'api_spec.yaml', type: 'code', icon: FileCode },
];

const analysisTypes = [
  { 
    id: 'stpa-sec', 
    name: 'STPA-Sec', 
    icon: Shield, 
    enabled: true,
    description: 'System-Theoretic Process Analysis for Security'
  },
  { 
    id: 'stride', 
    name: 'STRIDE', 
    icon: Target, 
    enabled: true,
    description: 'Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation'
  },
  { 
    id: 'pasta', 
    name: 'PASTA', 
    icon: Activity, 
    enabled: false,
    description: 'Process for Attack Simulation and Threat Analysis'
  },
  { 
    id: 'maestro', 
    name: 'MAESTRO', 
    icon: Brain, 
    enabled: false,
    description: 'Multi-Agent Evaluated Securely Through Rigorous Oversight'
  },
  { 
    id: 'dread', 
    name: 'DREAD', 
    icon: AlertTriangle, 
    enabled: false,
    description: 'Damage, Reproducibility, Exploitability, Affected, Discoverability'
  },
  { 
    id: 'linddun', 
    name: 'LINDDUN', 
    icon: Eye, 
    enabled: false,
    description: 'Privacy threat modeling framework'
  },
  { 
    id: 'hazop', 
    name: 'HAZOP', 
    icon: AlertTriangle, 
    enabled: false,
    description: 'Hazard and Operability Study'
  },
  { 
    id: 'octave', 
    name: 'OCTAVE', 
    icon: Layers, 
    enabled: false,
    description: 'Operationally Critical Threat, Asset, and Vulnerability Evaluation'
  },
  { 
    id: 'cve', 
    name: 'CVE Search', 
    icon: Search, 
    enabled: false,
    description: 'Common Vulnerabilities and Exposures database search'
  },
];

interface SidebarProps {
  selectedProject: any;
  onProjectSelect: (project: any) => void;
  onAnalysisTypesChange?: (enabledTypes: Record<string, boolean>) => void;
}

export default function Sidebar({ selectedProject, onProjectSelect, onAnalysisTypesChange }: SidebarProps) {
  const [selectedFile, setSelectedFile] = useState('1');
  const [enabledAnalyses, setEnabledAnalyses] = useState(
    analysisTypes.reduce((acc, type) => ({ ...acc, [type.id]: type.enabled }), {})
  );
  
  // Initialize with the passed state on mount
  useEffect(() => {
    onAnalysisTypesChange?.(enabledAnalyses);
  }, []);
  const [showRecommendations, setShowRecommendations] = useState(true);
  
  // Based on system being a Digital Banking Platform, these are recommended
  const recommendedAnalyses = ['pasta', 'maestro', 'dread', 'octave'];

  const handleFileUpload = () => {
    // TODO: Implement file upload
    console.log('Upload file');
  };

  const toggleAnalysis = (analysisId: string) => {
    setEnabledAnalyses(prev => {
      const newState = {
        ...prev,
        [analysisId]: !prev[analysisId]
      };
      onAnalysisTypesChange?.(newState);
      return newState;
    });
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-title">System Files</div>
        <div className="file-tree">
          {mockFiles.map(file => {
            const Icon = file.icon;
            return (
              <div
                key={file.id}
                className={`file-item ${selectedFile === file.id ? 'selected' : ''}`}
                onClick={() => setSelectedFile(file.id)}
              >
                <Icon size={14} />
                <span>{file.name}</span>
              </div>
            );
          })}
          <button className="file-item upload-btn" onClick={handleFileUpload}>
            <Upload size={14} />
            <span>Upload Files</span>
          </button>
        </div>
      </div>
      
      <div className="sidebar-section">
        <div className="sidebar-title">Analysis Types</div>
        <div className="analysis-options">
          {analysisTypes.map(type => {
            const Icon = type.icon;
            const isRecommended = recommendedAnalyses.includes(type.id);
            return (
              <label
                key={type.id}
                className={`analysis-option ${enabledAnalyses[type.id] ? 'active' : ''} ${isRecommended && showRecommendations ? 'recommended' : ''}`}
                title={type.description}
              >
                <input
                  type="checkbox"
                  checked={enabledAnalyses[type.id]}
                  onChange={() => toggleAnalysis(type.id)}
                />
                <Icon size={16} />
                <span>{type.name}</span>
                {isRecommended && showRecommendations && (
                  <span className="recommendation-badge" title="Recommended for your system">★</span>
                )}
              </label>
            );
          })}
        </div>
        {showRecommendations && (
          <div className="recommendation-note">
            <Info size={14} />
            <span>★ Recommended based on your Digital Banking Platform</span>
          </div>
        )}
      </div>
    </aside>
  );
}