import { useEffect, useState, useCallback } from 'react';
import wsClient from '../utils/websocket';
import type { AnalysisUpdate, SectionUpdate } from '../utils/websocket';

interface UseWebSocketOptions {
  onAnalysisUpdate?: (update: AnalysisUpdate) => void;
  onSectionUpdate?: (update: SectionUpdate) => void;
  onNotification?: (data: any) => void;
  onError?: (error: any) => void;
  analysisId?: string;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('disconnected');
  
  useEffect(() => {
    // Set initial connection state
    setConnectionState(wsClient.getConnectionState());
    setIsConnected(wsClient.getConnectionState() === 'connected');
    
    // Event handlers
    const handleConnected = () => {
      setIsConnected(true);
      setConnectionState('connected');
    };
    
    const handleDisconnected = () => {
      setIsConnected(false);
      setConnectionState('disconnected');
    };
    
    const handleAnalysisUpdate = (update: AnalysisUpdate) => {
      options.onAnalysisUpdate?.(update);
    };
    
    const handleSectionUpdate = (update: SectionUpdate) => {
      options.onSectionUpdate?.(update);
    };
    
    const handleNotification = (data: any) => {
      options.onNotification?.(data);
    };
    
    const handleError = (error: any) => {
      options.onError?.(error);
    };
    
    // Subscribe to events
    wsClient.on('connected', handleConnected);
    wsClient.on('disconnected', handleDisconnected);
    wsClient.on('analysis_update', handleAnalysisUpdate);
    wsClient.on('section_update', handleSectionUpdate);
    wsClient.on('notification', handleNotification);
    wsClient.on('error', handleError);
    
    // Subscribe to analysis if ID provided
    if (options.analysisId) {
      wsClient.subscribe(options.analysisId);
    }
    
    // Cleanup
    return () => {
      wsClient.off('connected', handleConnected);
      wsClient.off('disconnected', handleDisconnected);
      wsClient.off('analysis_update', handleAnalysisUpdate);
      wsClient.off('section_update', handleSectionUpdate);
      wsClient.off('notification', handleNotification);
      wsClient.off('error', handleError);
      
      if (options.analysisId) {
        wsClient.unsubscribe(options.analysisId);
      }
    };
  }, [options.analysisId]); // Only re-run if analysisId changes
  
  const subscribe = useCallback((analysisId: string) => {
    wsClient.subscribe(analysisId);
  }, []);
  
  const unsubscribe = useCallback((analysisId: string) => {
    wsClient.unsubscribe(analysisId);
  }, []);
  
  const send = useCallback((data: any) => {
    wsClient.send(data);
  }, []);
  
  return {
    isConnected,
    connectionState,
    subscribe,
    unsubscribe,
    send
  };
}