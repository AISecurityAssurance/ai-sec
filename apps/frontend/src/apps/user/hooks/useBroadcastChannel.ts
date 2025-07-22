import { useEffect, useRef } from 'react';
import { useAnalysisStore } from '../../../stores/analysisStore';

type BroadcastMessage = {
  type: 'STATE_UPDATE';
  payload: {
    field: string;
    value: any;
  };
} | {
  type: 'NAVIGATION';
  payload: {
    componentId: string;
    action: 'focus' | 'highlight';
    data?: any;
  };
};

export function useBroadcastChannel() {
  const channelRef = useRef<BroadcastChannel | null>(null);
  const store = useAnalysisStore();
  
  useEffect(() => {
    // Create or get broadcast channel
    const channel = new BroadcastChannel('analysis-sync');
    channelRef.current = channel;
    
    // Listen for messages from other windows
    channel.onmessage = (event: MessageEvent<BroadcastMessage>) => {
      const { type, payload } = event.data;
      
      if (type === 'STATE_UPDATE') {
        // Update local state based on field
        switch (payload.field) {
          case 'losses':
            store.updateLosses(payload.value);
            break;
          case 'hazards':
            store.updateHazards(payload.value);
            break;
          case 'controllers':
            store.updateControllers(payload.value);
            break;
          case 'controlActions':
            store.updateControlActions(payload.value);
            break;
          case 'ucas':
            store.updateUcas(payload.value);
            break;
          case 'scenarios':
            store.updateScenarios(payload.value);
            break;
          case 'systemDescription':
            store.updateSystemDescription(payload.value);
            break;
          case 'enabledAnalyses':
            store.setEnabledAnalyses(payload.value);
            break;
        }
      } else if (type === 'NAVIGATION') {
        // Handle cross-window navigation events
        // This will be implemented based on specific needs
        console.log('Navigation event received:', payload);
      }
    };
    
    // Cleanup
    return () => {
      channel.close();
    };
  }, [store]);
  
  // Function to broadcast state changes
  const broadcast = (field: string, value: any) => {
    if (channelRef.current) {
      channelRef.current.postMessage({
        type: 'STATE_UPDATE',
        payload: { field, value }
      } as BroadcastMessage);
    }
  };
  
  // Function to broadcast navigation events
  const broadcastNavigation = (componentId: string, action: 'focus' | 'highlight', data?: any) => {
    if (channelRef.current) {
      channelRef.current.postMessage({
        type: 'NAVIGATION',
        payload: { componentId, action, data }
      } as BroadcastMessage);
    }
  };
  
  return { broadcast, broadcastNavigation };
}

// Hook to sync specific store updates to broadcast channel
export function useBroadcastSync() {
  const { broadcast } = useBroadcastChannel();
  const store = useAnalysisStore();
  
  // Subscribe to store changes and broadcast them
  useEffect(() => {
    const unsubscribe = useAnalysisStore.subscribe((state, prevState) => {
      // Check which fields changed and broadcast them
      if (state.losses !== prevState.losses) {
        broadcast('losses', state.losses);
      }
      if (state.hazards !== prevState.hazards) {
        broadcast('hazards', state.hazards);
      }
      if (state.controllers !== prevState.controllers) {
        broadcast('controllers', state.controllers);
      }
      if (state.controlActions !== prevState.controlActions) {
        broadcast('controlActions', state.controlActions);
      }
      if (state.ucas !== prevState.ucas) {
        broadcast('ucas', state.ucas);
      }
      if (state.scenarios !== prevState.scenarios) {
        broadcast('scenarios', state.scenarios);
      }
      if (state.systemDescription !== prevState.systemDescription) {
        broadcast('systemDescription', state.systemDescription);
      }
      if (state.enabledAnalyses !== prevState.enabledAnalyses) {
        broadcast('enabledAnalyses', state.enabledAnalyses);
      }
    });
    
    return unsubscribe;
  }, [broadcast]);
}