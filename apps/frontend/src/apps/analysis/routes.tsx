import { Routes, Route, useParams } from 'react-router-dom';
import AnalysisApp from './AnalysisApp';
import InputSelectionPanel from '../../components/analysis/InputSelectionPanel';
import AnalysisCanvas from '../../components/analysis/AnalysisCanvas';
import ChatPanel from '../user/components/ChatPanel';
import CollapsibleAnalysisSection from '../../components/analysis/CollapsibleAnalysisSection';
import StandaloneWrapper from '../../components/common/StandaloneWrapper';
import { useAnalysisStore } from '../../stores/analysisStore';

// Component to render a single analysis plugin
function StandaloneAnalysisPlugin() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const { enabledAnalyses } = useAnalysisStore();
  
  const analysisLabels: Record<string, string> = {
    'stpa-sec': 'STPA-Sec',
    'stride': 'STRIDE',
    'pasta': 'PASTA',
    'dread': 'DREAD',
    'maestro': 'MAESTRO',
    'linddun': 'LINDDUN',
    'hazop': 'HAZOP',
    'octave': 'OCTAVE'
  };
  
  const label = analysisLabels[analysisId || ''] || analysisId;
  
  return (
    <StandaloneWrapper title={`${label} Analysis`}>
      <div style={{ padding: 0 }}>
        <CollapsibleAnalysisSection
          analysisId={analysisId || ''}
          analysisLabel={label}
          enabledAnalyses={enabledAnalyses}
          isExpanded={true}
          onToggle={() => {}}
        />
      </div>
    </StandaloneWrapper>
  );
}

export default function AnalysisRoutes() {
  return (
    <Routes>
      <Route index element={<AnalysisApp />} />
      <Route path="input-selection" element={
        <StandaloneWrapper title="Input Selection">
          <InputSelectionPanel />
        </StandaloneWrapper>
      } />
      <Route path="canvas" element={
        <StandaloneWrapper title="Analysis Canvas">
          <AnalysisCanvas />
        </StandaloneWrapper>
      } />
      <Route path="agent" element={
        <StandaloneWrapper title="SA Agent">
          <ChatPanel activeAnalysis="stpa-sec" />
        </StandaloneWrapper>
      } />
      <Route path="plugin/:analysisId" element={<StandaloneAnalysisPlugin />} />
    </Routes>
  );
}