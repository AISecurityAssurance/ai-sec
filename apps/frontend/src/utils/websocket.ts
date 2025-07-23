/**
 * WebSocket client for real-time updates
 * Handles connection, reconnection, and message routing
 */

// Simple EventEmitter implementation for browser
class EventEmitter {
  private events: Map<string, Array<(...args: any[]) => void>> = new Map();

  on(event: string, listener: (...args: any[]) => void): void {
    if (!this.events.has(event)) {
      this.events.set(event, []);
    }
    this.events.get(event)!.push(listener);
  }

  off(event: string, listener: (...args: any[]) => void): void {
    const listeners = this.events.get(event);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    }
  }

  emit(event: string, ...args: any[]): void {
    const listeners = this.events.get(event);
    if (listeners) {
      listeners.forEach(listener => listener(...args));
    }
  }

  removeAllListeners(event?: string): void {
    if (event) {
      this.events.delete(event);
    } else {
      this.events.clear();
    }
  }
}

export interface WSMessage {
  type: 'connection' | 'analysis_update' | 'section_update' | 'error' | 'notification' | 'pong';
  timestamp: string;
  data: Record<string, any>;
}

export interface AnalysisUpdate {
  analysis_id: string;
  status: string;
  progress: number;
  message?: string;
}

export interface SectionUpdate {
  analysis_id: string;
  framework: string;
  section_id: string;
  status: string;
  content?: any;
  error?: string;
}

class WebSocketClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private userId: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private heartbeatInterval: number | null = null;
  private subscriptions = new Set<string>();
  
  constructor() {
    super();
    // Get user ID from session or generate one
    this.userId = localStorage.getItem('userId') || this.generateUserId();
    localStorage.setItem('userId', this.userId);
    
    // Construct WebSocket URL
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    this.url = `${wsUrl}/ws/${this.userId}`;
  }
  
  private generateUserId(): string {
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }
    
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.startHeartbeat();
        
        // Re-subscribe to previous subscriptions
        this.subscriptions.forEach(analysisId => {
          this.subscribe(analysisId);
        });
        
        this.emit('connected');
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.stopHeartbeat();
        this.emit('disconnected');
        this.attemptReconnect();
      };
      
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }
  
  private handleMessage(message: WSMessage): void {
    switch (message.type) {
      case 'connection':
        this.emit('connection', message.data);
        break;
        
      case 'analysis_update':
        this.emit('analysis_update', message.data as AnalysisUpdate);
        break;
        
      case 'section_update':
        this.emit('section_update', message.data as SectionUpdate);
        break;
        
      case 'notification':
        this.emit('notification', message.data);
        break;
        
      case 'error':
        this.emit('error', message.data);
        break;
        
      case 'pong':
        // Heartbeat response received
        break;
        
      default:
        console.warn('Unknown message type:', message.type);
    }
  }
  
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('reconnect_failed');
      return;
    }
    
    this.reconnectAttempts++;
    console.log(`Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, this.reconnectDelay);
    
    // Exponential backoff
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000); // Max 30 seconds
  }
  
  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, 30000); // Ping every 30 seconds
  }
  
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      window.clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
  
  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, queuing message');
      // Could implement a message queue here
    }
  }
  
  subscribe(analysisId: string): void {
    this.subscriptions.add(analysisId);
    this.send({
      type: 'subscribe',
      analysis_id: analysisId
    });
  }
  
  unsubscribe(analysisId: string): void {
    this.subscriptions.delete(analysisId);
    this.send({
      type: 'unsubscribe',
      analysis_id: analysisId
    });
  }
  
  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
  
  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }
}

// Create singleton instance
const wsClient = new WebSocketClient();

// Auto-connect on import
if (typeof window !== 'undefined') {
  wsClient.connect();
}

export default wsClient;