import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Folder, FileCode, Upload, Shield, Target, Search, Eye, Brain, Activity, Lock, AlertTriangle, Users, Layers, Info } from 'lucide-react';
import { useAnalysisStore } from '../stores/analysisStore';
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
  const [showRecommendations, setShowRecommendations] = useState(true);
  
  // Get enabledAnalyses from the store
  const { enabledAnalyses } = useAnalysisStore();
  
  // Based on system being a Digital Banking Platform, these are recommended
  const recommendedAnalyses = ['pasta', 'maestro', 'dread', 'octave'];

  const handleFileUpload = () => {
    // TODO: Implement file upload
    console.log('Upload file');
  };

  const toggleAnalysis = (analysisId: string) => {
    const newState = {
      ...enabledAnalyses,
      [analysisId]: !enabledAnalyses[analysisId]
    };
    onAnalysisTypesChange?.(newState);
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
              <Link
                key={type.id}
                to={`/analysis/view/${type.id}`}
                className={`analysis-option ${enabledAnalyses[type.id] ? 'active' : ''} ${isRecommended && showRecommendations ? 'recommended' : ''}`}
                title={type.description}
                onClick={(e) => {
                  // Allow normal click to toggle checkbox
                  if (!e.ctrlKey && !e.metaKey && e.button === 0) {
                    e.preventDefault();
                    toggleAnalysis(type.id);
                  }
                  // Right-click or ctrl/cmd-click will use browser's default behavior
                }}
              >
                <input
                  type="checkbox"
                  checked={enabledAnalyses[type.id]}
                  onChange={() => toggleAnalysis(type.id)}
                  onClick={(e) => e.stopPropagation()}
                />
                <Icon size={16} />
                <span>{type.name}</span>
                {isRecommended && showRecommendations && (
                  <span className="recommendation-badge" title="Recommended for your system">★</span>
                )}
              </Link>
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