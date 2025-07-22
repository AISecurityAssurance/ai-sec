import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { X, Maximize2, Minimize2 } from 'lucide-react';
import CollapsibleAnalysisContentWithTemplates from '../../../components/analysis/CollapsibleAnalysisContentWithTemplates';
import { useAnalysisStore } from '../../../stores/analysisStore';
import { useBroadcastChannel } from '../hooks/useBroadcastChannel';
import './StandaloneComponent.css';

const ANALYSIS_NAMES = {
  'stpa-sec': 'STPA-Sec Analysis',
  'stride': 'STRIDE Analysis',
  'pasta': 'PASTA Analysis',
  'dread': 'DREAD Analysis',
  'maestro': 'MAESTRO Analysis',
  'linddun': 'LINDDUN Analysis',
  'hazop': 'HAZOP Analysis',
  'octave': 'OCTAVE Analysis'
} as const;

export default function StandaloneTemplateView() {
  const { analysisType, sectionId } = useParams<{ analysisType: string; sectionId?: string }>();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const { enabledAnalyses } = useAnalysisStore();
  
  // Set up broadcast channel for state sync
  useBroadcastChannel();
  
  // Update window title
  useEffect(() => {
    const title = analysisType && ANALYSIS_NAMES[analysisType as keyof typeof ANALYSIS_NAMES] 
      ? ANALYSIS_NAMES[analysisType as keyof typeof ANALYSIS_NAMES]
      : 'Security Analysis';
    const sectionTitle = sectionId ? ` - ${sectionId.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}` : '';
    document.title = `${title}${sectionTitle} - Security Analysis Platform`;
  }, [analysisType, sectionId]);
  
  // Handle fullscreen toggle
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };
  
  // Close window handler
  const handleClose = () => {
    window.close();
  };
  
  if (!analysisType || !ANALYSIS_NAMES[analysisType as keyof typeof ANALYSIS_NAMES]) {
    return <div>Invalid analysis type</div>;
  }
  
  // Get section title
  const getSectionTitle = () => {
    if (!sectionId) return ANALYSIS_NAMES[analysisType as keyof typeof ANALYSIS_NAMES];
    return sectionId.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  };
  
  return (
    <div className="standalone-container">
      <header className="standalone-header">
        <h1>{getSectionTitle()}</h1>
        <div className="standalone-controls">
          <button 
            className="btn-icon" 
            onClick={toggleFullscreen}
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>
          <button 
            className="btn-icon btn-close" 
            onClick={handleClose}
            title="Close window"
          >
            <X size={18} />
          </button>
        </div>
      </header>
      
      <main className="standalone-content">
        {sectionId ? (
          <CollapsibleAnalysisContentWithTemplates 
            analysisId={analysisType}
            enabledAnalyses={enabledAnalyses}
            focusedSection={sectionId}
          />
        ) : (
          <CollapsibleAnalysisContentWithTemplates 
            analysisId={analysisType}
            enabledAnalyses={enabledAnalyses}
          />
        )}
      </main>
    </div>
  );
}