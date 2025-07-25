import { useEffect } from 'react';
import { useAnalysisStore } from '../stores/analysisStore';
import { useVersionStore } from '../stores/versionStore';

/**
 * Hook that syncs analysis data changes to the version store
 */
export function useVersionSync() {
  const activeVersionId = useVersionStore((state) => state.activeVersionId);
  const updateVersionData = useVersionStore((state) => state.updateVersionData);
  
  // Subscribe to analysis data changes
  useEffect(() => {
    const unsubscribe = useAnalysisStore.subscribe(
      (state) => ({
        systemDescription: state.systemDescription,
        losses: state.losses,
        hazards: state.hazards,
        controllers: state.controllers,
        controlActions: state.controlActions,
        ucas: state.ucas,
        scenarios: state.scenarios,
        hasUnsavedChanges: state.hasUnsavedChanges
      }),
      (data) => {
        // Only save if there are unsaved changes and not in demo mode
        if (data.hasUnsavedChanges && activeVersionId !== 'demo-v1') {
          const versionData = {
            systemDescription: data.systemDescription,
            losses: data.losses,
            hazards: data.hazards,
            controllers: data.controllers,
            controlActions: data.controlActions,
            ucas: data.ucas,
            scenarios: data.scenarios
          };
          
          updateVersionData(activeVersionId, versionData);
        }
      }
    );
    
    return unsubscribe;
  }, [activeVersionId, updateVersionData]);
}