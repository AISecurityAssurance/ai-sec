import { useState } from 'react';
import { FileText, Folder, FileCode, Upload, Shield, Target, Search } from 'lucide-react';
import './Sidebar.css';

const mockFiles = [
  { id: '1', name: 'banking_system.txt', type: 'text', icon: FileText },
  { id: '2', name: 'src/', type: 'folder', icon: Folder },
  { id: '3', name: 'api_spec.yaml', type: 'code', icon: FileCode },
];

const analysisTypes = [
  { id: 'stpa-sec', name: 'STPA-Sec', icon: Shield, enabled: true },
  { id: 'stride', name: 'STRIDE', icon: Target, enabled: true },
  { id: 'cve', name: 'CVE Search', icon: Search, enabled: false },
];

interface SidebarProps {
  selectedProject: any;
  onProjectSelect: (project: any) => void;
}

export default function Sidebar({ selectedProject, onProjectSelect }: SidebarProps) {
  const [selectedFile, setSelectedFile] = useState('1');
  const [enabledAnalyses, setEnabledAnalyses] = useState(
    analysisTypes.reduce((acc, type) => ({ ...acc, [type.id]: type.enabled }), {})
  );

  const handleFileUpload = () => {
    // TODO: Implement file upload
    console.log('Upload file');
  };

  const toggleAnalysis = (analysisId: string) => {
    setEnabledAnalyses(prev => ({
      ...prev,
      [analysisId]: !prev[analysisId]
    }));
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
            return (
              <label
                key={type.id}
                className={`analysis-option ${enabledAnalyses[type.id] ? 'active' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={enabledAnalyses[type.id]}
                  onChange={() => toggleAnalysis(type.id)}
                />
                <Icon size={16} />
                <span>{type.name}</span>
              </label>
            );
          })}
        </div>
      </div>
    </aside>
  );
}