import { useState } from 'react';
import SimpleLayout from '../../components/common/SimpleLayout';
import ThreePanelLayout from '../../components/common/ThreePanelLayout';
import InputSelectionPanel from '../../components/analysis/InputSelectionPanel';
import AnalysisCanvas from '../../components/analysis/AnalysisCanvas';
import ChatPanel from '../user/components/ChatPanel';
import './AnalysisApp.css';

export default function AnalysisApp() {
  const [activeAnalysis, setActiveAnalysis] = useState('stpa-sec');
  
  const handleOpenInNewWindow = (panel: 'left' | 'center' | 'right') => {
    const urls = {
      left: '/analysis/input-selection',
      center: '/analysis/canvas',
      right: '/analysis/agent'
    };
    
    const sizes = {
      left: { width: 400, height: 600 },
      center: { width: 800, height: 600 },
      right: { width: 400, height: 600 }
    };
    
    const size = sizes[panel];
    const features = `width=${size.width},height=${size.height},menubar=no,toolbar=no,location=no,status=no`;
    window.open(urls[panel], `analysis-${panel}`, features);
  };

  return (
    <SimpleLayout>
      <ThreePanelLayout
        leftPanel={<InputSelectionPanel />}
        centerPanel={<AnalysisCanvas />}
        rightPanel={<ChatPanel activeAnalysis={activeAnalysis} />}
        onOpenInNewWindow={handleOpenInNewWindow}
      />
    </SimpleLayout>
  );
}