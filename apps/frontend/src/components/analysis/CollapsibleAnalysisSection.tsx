import { ChevronRight, ChevronDown } from 'lucide-react';
import CollapsibleAnalysisContent from './CollapsibleAnalysisContent';
import CollapsibleAnalysisContentWithTemplates from './CollapsibleAnalysisContentWithTemplates';

interface CollapsibleAnalysisSectionProps {
  analysisId: string;
  analysisLabel: string;
  enabledAnalyses: Record<string, boolean>;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function CollapsibleAnalysisSection({
  analysisId,
  analysisLabel,
  enabledAnalyses,
  isExpanded,
  onToggle
}: CollapsibleAnalysisSectionProps) {
  // Use template version for all implemented analyses
  const useTemplates = ['stpa-sec', 'dread', 'stride', 'pasta', 'maestro', 'linddun', 'hazop', 'octave'].includes(analysisId);
  
  return (
    <div className="analysis-section">
      <div 
        className="analysis-section-header"
        onClick={onToggle}
      >
        {isExpanded ? 
          <ChevronDown size={16} className="expand-icon" /> : 
          <ChevronRight size={16} className="expand-icon" />
        }
        <a 
          href={`/analysis/plugin/${analysisId}`}
          className="analysis-section-link"
          onClick={(e) => e.preventDefault()}
        >
          <h3>{analysisLabel} Analysis</h3>
        </a>
      </div>
      
      {isExpanded && (
        <div className="analysis-section-content">
          {useTemplates ? (
            <CollapsibleAnalysisContentWithTemplates
              analysisId={analysisId}
              enabledAnalyses={enabledAnalyses}
            />
          ) : (
            <CollapsibleAnalysisContent
              analysisId={analysisId}
              enabledAnalyses={enabledAnalyses}
            />
          )}
        </div>
      )}
    </div>
  );
}