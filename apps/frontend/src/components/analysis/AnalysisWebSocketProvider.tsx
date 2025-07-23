import { useEffect } from 'react';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import type { AnalysisUpdate, SectionUpdate } from '../../utils/websocket';

interface AnalysisWebSocketProviderProps {
  children: React.ReactNode;
}

export function AnalysisWebSocketProvider({ children }: AnalysisWebSocketProviderProps) {
  const { 
    currentAnalysisId, 
    updateAnalysisStatus, 
    updateSectionResult,
    updateAnalysisResult 
  } = useAnalysisStore();
  
  const { isConnected } = useWebSocket({
    analysisId: currentAnalysisId || undefined,
    
    onAnalysisUpdate: (update: AnalysisUpdate) => {
      // Update global analysis status
      updateAnalysisStatus({
        status: update.status as any,
        progress: update.progress,
        message: update.message
      });
    },
    
    onSectionUpdate: (update: SectionUpdate) => {
      // Update specific section result
      updateSectionResult(
        update.framework,
        update.section_id,
        {
          status: update.status as any,
          content: update.content,
          error: update.error
        }
      );
      
      // If this is the first section, initialize the framework result
      const store = useAnalysisStore.getState();
      if (!store.analysisResults[update.framework]) {
        updateAnalysisResult(update.framework, {
          framework: update.framework,
          sections: [],
          status: { status: 'in_progress', progress: 0 }
        });
      }
    },
    
    onNotification: (data) => {
      console.log('Analysis notification:', data);
      // Could show a toast notification here
    },
    
    onError: (error) => {
      console.error('WebSocket error:', error);
      // Could show an error notification here
    }
  });
  
  // Log connection status changes
  useEffect(() => {
    console.log(`WebSocket connection status: ${isConnected ? 'connected' : 'disconnected'}`);
  }, [isConnected]);
  
  return <>{children}</>;
}