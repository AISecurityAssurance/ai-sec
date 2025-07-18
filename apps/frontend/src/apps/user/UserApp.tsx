import { useState } from 'react';
import { Menu } from 'lucide-react';
import AppLayout from '../../components/common/AppLayout';
import Sidebar from './components/Sidebar';
import AnalysisPanel from './components/AnalysisPanel';
import ChatPanel from './components/ChatPanel';
import './UserApp.css';

export default function UserApp() {
  const [selectedProject, setSelectedProject] = useState(null);
  const [activeAnalysis, setActiveAnalysis] = useState('stpa-sec');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [selectedElement, setSelectedElement] = useState<any>(null);
  const [enabledAnalyses, setEnabledAnalyses] = useState<Record<string, boolean>>({
    'stpa-sec': true,
    'stride': true,
    'pasta': false,
    'maestro': false,
    'dread': false,
    'linddun': false,
    'hazop': false,
    'octave': false,
    'cve': false
  });

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    // Simulate analysis
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 3000);
  };

  const header = (
    <header className="user-header">
      <div className="header-left">
        <button 
          className="sidebar-toggle"
          onClick={() => setSidebarVisible(!sidebarVisible)}
          title={sidebarVisible ? 'Hide sidebar' : 'Show sidebar'}
        >
          <Menu size={20} />
        </button>
        <h1 className="heading-3">🛡️ Security Analysis Platform</h1>
      </div>
      <button 
        className="btn btn-primary"
        onClick={handleRunAnalysis}
        disabled={isAnalyzing}
      >
        {isAnalyzing ? (
          <>
            <div className="spinner" />
            Analyzing...
          </>
        ) : (
          <>
            <span>▶</span>
            Run Analysis
          </>
        )}
      </button>
    </header>
  );

  return (
    <AppLayout header={header}>
      <div className="user-layout">
        {sidebarVisible && (
          <Sidebar 
            selectedProject={selectedProject}
            onProjectSelect={setSelectedProject}
            onAnalysisTypesChange={setEnabledAnalyses}
          />
        )}
        
        <div className="user-main">
          <AnalysisPanel 
            activeAnalysis={activeAnalysis}
            onAnalysisChange={setActiveAnalysis}
            isAnalyzing={isAnalyzing}
            onElementSelect={(element, type) => setSelectedElement({ element, type })}
            enabledAnalyses={enabledAnalyses}
          />
        </div>
        
        <ChatPanel 
          projectId={selectedProject?.id}
          activeAnalysis={activeAnalysis}
          selectedElement={selectedElement}
        />
      </div>
    </AppLayout>
  );
}