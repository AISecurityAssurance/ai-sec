import { useAnalysisStore } from '../stores/analysisStore';
import { useMemo } from 'react';
import type { UCA } from '../apps/user/mockData/stpaSecData';
import { controlActions, ucas as defaultUCAs } from '../apps/user/mockData/stpaSecData';

interface HeatMapCell {
  row: string;
  col: string;
  value: number;
  label?: string;
  tooltip?: string;
  data?: UCA[];
}

export function useUCAData(analysisId: string) {
  const { analysisResults } = useAnalysisStore();
  const updateSectionResult = useAnalysisStore(state => state.updateSectionResult);
  
  // Single source of truth for UCA data
  const ucaData = useMemo(() => {
    const frameworkResult = analysisResults[analysisId];
    const ucasSection = frameworkResult?.sections.find(s => s.id === 'ucas');
    // Use default UCAs if no data in store yet
    return ucasSection?.content?.ucas || defaultUCAs;
  }, [analysisResults, analysisId]);
  
  // Map UCA types for display
  const typeMap: Record<string, string> = {
    'not-provided': 'Not Provided',
    'provided': 'Provided Unsafely',
    'wrong-timing': 'Wrong Timing',
    'wrong-duration': 'Wrong Duration'
  };
  
  // Heat map data generation
  const heatMapData = useMemo(() => {
    const cells: HeatMapCell[] = [];
    
    controlActions.forEach(ca => {
      ['not-provided', 'provided', 'wrong-timing', 'wrong-duration'].forEach(type => {
        // Find UCAs for this control action/type combination
        const ucasForCell = ucaData.filter((u: UCA) => 
          u.controlActionId === ca.id && u.type === type
        );
        
        // Calculate risk value based on severity
        let value = 0;
        if (ucasForCell.length > 0) {
          const severityScores = ucasForCell.map(u => 
            u.severity === 'critical' ? 5 :
            u.severity === 'high' ? 4 :
            u.severity === 'medium' ? 3 : 2
          );
          value = Math.round(severityScores.reduce((a, b) => a + b, 0) / severityScores.length);
        }
        
        cells.push({
          row: ca.action,
          col: typeMap[type],
          value,
          label: ucasForCell.length.toString(),
          tooltip: `${ucasForCell.length} UCA${ucasForCell.length !== 1 ? 's' : ''} identified`,
          data: ucasForCell
        });
      });
    });
    
    return cells;
  }, [ucaData]);
  
  const updateUCAData = (newData: any[]) => {
    updateSectionResult(analysisId, 'ucas', {
      content: { ucas: newData },
      status: 'completed'
    });
  };
  
  return {
    ucaData,
    heatMapData,
    updateUCAData
  };
}