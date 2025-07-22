import { useState, useEffect, useCallback } from 'react';

/**
 * Hook for synchronizing state across multiple browser windows/tabs
 * Uses BroadcastChannel API for real-time sync
 */
export function useSyncState<T>(
  channelName: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [state, setState] = useState<T>(initialValue);
  const [channel] = useState(() => {
    if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
      return new BroadcastChannel(channelName);
    }
    return null;
  });

  // Handle incoming messages
  useEffect(() => {
    if (!channel) return;

    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'STATE_UPDATE') {
        setState(event.data.value);
      }
    };

    channel.addEventListener('message', handleMessage);

    return () => {
      channel.removeEventListener('message', handleMessage);
    };
  }, [channel]);

  // Cleanup channel on unmount
  useEffect(() => {
    return () => {
      channel?.close();
    };
  }, [channel]);

  // Custom setState that broadcasts changes
  const setSyncState = useCallback((value: T | ((prev: T) => T)) => {
    setState(prev => {
      const newValue = typeof value === 'function' 
        ? (value as (prev: T) => T)(prev) 
        : value;

      // Broadcast the change
      if (channel) {
        channel.postMessage({
          type: 'STATE_UPDATE',
          value: newValue,
          timestamp: Date.now()
        });
      }

      return newValue;
    });
  }, [channel]);

  return [state, setSyncState];
}

/**
 * Hook for syncing complex edit states across windows
 */
export function useSyncEditState<T>(componentId: string, initialData: T) {
  const channelName = `analysis-edit-${componentId}`;
  
  const [editState, setEditState] = useSyncState(channelName, {
    isEditing: false,
    originalData: initialData,
    currentData: initialData,
    hasChanges: false,
    lastModified: Date.now()
  });

  const startEdit = useCallback(() => {
    setEditState(prev => ({
      ...prev,
      isEditing: true,
      originalData: prev.currentData,
      lastModified: Date.now()
    }));
  }, [setEditState]);

  const updateData = useCallback((data: T) => {
    setEditState(prev => ({
      ...prev,
      currentData: data,
      hasChanges: JSON.stringify(data) !== JSON.stringify(prev.originalData),
      lastModified: Date.now()
    }));
  }, [setEditState]);

  const saveChanges = useCallback(() => {
    setEditState(prev => ({
      ...prev,
      isEditing: false,
      originalData: prev.currentData,
      hasChanges: false,
      lastModified: Date.now()
    }));
  }, [setEditState]);

  const cancelChanges = useCallback(() => {
    setEditState(prev => ({
      ...prev,
      isEditing: false,
      currentData: prev.originalData,
      hasChanges: false,
      lastModified: Date.now()
    }));
  }, [setEditState]);

  return {
    editState,
    startEdit,
    updateData,
    saveChanges,
    cancelChanges
  };
}