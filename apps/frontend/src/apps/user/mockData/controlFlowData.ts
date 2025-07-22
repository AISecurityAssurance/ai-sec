import type { Node, Edge } from '@xyflow/react';

export const controlFlowNodes: Node[] = [
  // User Layer
  {
    id: 'user',
    type: 'default',
    position: { x: 50, y: 100 },
    data: { label: 'End Users' },
    style: { background: '#e0f2fe', border: '2px solid #0284c7', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'admin',
    type: 'default',
    position: { x: 50, y: 300 },
    data: { label: 'System Administrators' },
    style: { background: '#e0f2fe', border: '2px solid #0284c7', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'support',
    type: 'default',
    position: { x: 50, y: 400 },
    data: { label: 'Support Staff' },
    style: { background: '#e0f2fe', border: '2px solid #0284c7', borderRadius: '8px', padding: '10px' }
  },
  
  // Frontend Layer
  {
    id: 'web-app',
    type: 'default',
    position: { x: 250, y: 50 },
    data: { label: 'Web Application' },
    style: { background: '#dcfce7', border: '2px solid #16a34a', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'mobile-app',
    type: 'default',
    position: { x: 250, y: 150 },
    data: { label: 'Mobile Application' },
    style: { background: '#dcfce7', border: '2px solid #16a34a', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'admin-portal',
    type: 'default',
    position: { x: 250, y: 300 },
    data: { label: 'Admin Portal' },
    style: { background: '#dcfce7', border: '2px solid #16a34a', borderRadius: '8px', padding: '10px' }
  },
  
  // Edge Services Layer
  {
    id: 'load-balancer',
    type: 'default',
    position: { x: 450, y: 100 },
    data: { label: 'Load Balancer' },
    style: { background: '#fef3c7', border: '2px solid #f59e0b', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'waf',
    type: 'default',
    position: { x: 450, y: 200 },
    data: { label: 'Web Application Firewall' },
    style: { background: '#fef3c7', border: '2px solid #f59e0b', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'api-gateway',
    type: 'default',
    position: { x: 450, y: 300 },
    data: { label: 'API Gateway' },
    style: { background: '#fef3c7', border: '2px solid #f59e0b', borderRadius: '8px', padding: '10px' }
  },
  
  // Core Services Layer
  {
    id: 'auth-service',
    type: 'default',
    position: { x: 650, y: 50 },
    data: { label: 'Authentication Service' },
    style: { background: '#e9d5ff', border: '2px solid #9333ea', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'session-manager',
    type: 'default',
    position: { x: 650, y: 150 },
    data: { label: 'Session Manager' },
    style: { background: '#e9d5ff', border: '2px solid #9333ea', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'transaction-processor',
    type: 'default',
    position: { x: 650, y: 250 },
    data: { label: 'Transaction Processor' },
    style: { background: '#e9d5ff', border: '2px solid #9333ea', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'fraud-detection',
    type: 'default',
    position: { x: 650, y: 350 },
    data: { label: 'Fraud Detection System' },
    style: { background: '#e9d5ff', border: '2px solid #9333ea', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'notification-service',
    type: 'default',
    position: { x: 650, y: 450 },
    data: { label: 'Notification Service' },
    style: { background: '#e9d5ff', border: '2px solid #9333ea', borderRadius: '8px', padding: '10px' }
  },
  
  // Data Layer
  {
    id: 'database',
    type: 'default',
    position: { x: 850, y: 100 },
    data: { label: 'Core Database' },
    style: { background: '#fecaca', border: '2px solid #dc2626', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'cache',
    type: 'default',
    position: { x: 850, y: 200 },
    data: { label: 'Redis Cache' },
    style: { background: '#fecaca', border: '2px solid #dc2626', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'audit-log',
    type: 'default',
    position: { x: 850, y: 300 },
    data: { label: 'Audit Log System' },
    style: { background: '#fecaca', border: '2px solid #dc2626', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'file-storage',
    type: 'default',
    position: { x: 850, y: 400 },
    data: { label: 'File Storage' },
    style: { background: '#fecaca', border: '2px solid #dc2626', borderRadius: '8px', padding: '10px' }
  },
  
  // External Services
  {
    id: 'third-party',
    type: 'default',
    position: { x: 450, y: 500 },
    data: { label: 'Third-party APIs' },
    style: { background: '#f3f4f6', border: '2px solid #6b7280', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'payment-gateway',
    type: 'default',
    position: { x: 450, y: 600 },
    data: { label: 'Payment Gateway' },
    style: { background: '#f3f4f6', border: '2px solid #6b7280', borderRadius: '8px', padding: '10px' }
  },
  
  // Monitoring Layer
  {
    id: 'monitoring',
    type: 'default',
    position: { x: 1050, y: 200 },
    data: { label: 'Monitoring & Alerts' },
    style: { background: '#fee2e2', border: '2px solid #ef4444', borderRadius: '8px', padding: '10px' }
  },
  {
    id: 'siem',
    type: 'default',
    position: { x: 1050, y: 300 },
    data: { label: 'SIEM System' },
    style: { background: '#fee2e2', border: '2px solid #ef4444', borderRadius: '8px', padding: '10px' }
  }
];

export const controlFlowEdges: Edge[] = [
  // User interactions
  { id: 'e1', source: 'user', target: 'web-app', label: 'HTTPS', animated: true },
  { id: 'e2', source: 'user', target: 'mobile-app', label: 'API', animated: true },
  { id: 'e3', source: 'admin', target: 'admin-portal', label: 'Admin Access', animated: true },
  { id: 'e4', source: 'support', target: 'admin-portal', label: 'Support Access' },
  
  // Frontend to Edge Services
  { id: 'e5', source: 'web-app', target: 'load-balancer', label: 'HTTP/HTTPS' },
  { id: 'e6', source: 'mobile-app', target: 'load-balancer', label: 'API Calls' },
  { id: 'e7', source: 'admin-portal', target: 'api-gateway', label: 'Admin API' },
  
  // Edge Services routing
  { id: 'e8', source: 'load-balancer', target: 'waf', label: 'Traffic' },
  { id: 'e9', source: 'waf', target: 'api-gateway', label: 'Filtered Traffic' },
  
  // API Gateway to Core Services
  { id: 'e10', source: 'api-gateway', target: 'auth-service', label: 'Auth' },
  { id: 'e11', source: 'api-gateway', target: 'session-manager', label: 'Sessions' },
  { id: 'e12', source: 'api-gateway', target: 'transaction-processor', label: 'Transactions' },
  { id: 'e13', source: 'api-gateway', target: 'notification-service', label: 'Notifications' },
  
  // Core Service interactions
  { id: 'e14', source: 'auth-service', target: 'session-manager', label: 'Session Create' },
  { id: 'e15', source: 'transaction-processor', target: 'fraud-detection', label: 'Risk Check' },
  { id: 'e16', source: 'fraud-detection', target: 'transaction-processor', label: 'Risk Score', type: 'step', style: { strokeDasharray: '5 5' } },
  { id: 'e17', source: 'transaction-processor', target: 'notification-service', label: 'Alerts' },
  
  // Data layer connections
  { id: 'e18', source: 'auth-service', target: 'database', label: 'User Data' },
  { id: 'e19', source: 'auth-service', target: 'cache', label: 'Session Cache' },
  { id: 'e20', source: 'session-manager', target: 'cache', label: 'Session Store' },
  { id: 'e21', source: 'transaction-processor', target: 'database', label: 'Transactions' },
  { id: 'e22', source: 'fraud-detection', target: 'database', label: 'Risk Data' },
  { id: 'e23', source: 'notification-service', target: 'database', label: 'Notifications' },
  
  // Audit logging
  { id: 'e24', source: 'auth-service', target: 'audit-log', label: 'Auth Events' },
  { id: 'e25', source: 'transaction-processor', target: 'audit-log', label: 'Tx Events' },
  { id: 'e26', source: 'api-gateway', target: 'audit-log', label: 'API Logs' },
  { id: 'e27', source: 'waf', target: 'audit-log', label: 'Security Events' },
  
  // External services
  { id: 'e28', source: 'api-gateway', target: 'third-party', label: 'External APIs' },
  { id: 'e29', source: 'transaction-processor', target: 'payment-gateway', label: 'Payments' },
  { id: 'e30', source: 'notification-service', target: 'third-party', label: 'SMS/Email' },
  
  // File storage
  { id: 'e31', source: 'transaction-processor', target: 'file-storage', label: 'Documents' },
  { id: 'e32', source: 'notification-service', target: 'file-storage', label: 'Templates' },
  
  // Monitoring connections
  { id: 'e33', source: 'monitoring', target: 'auth-service', label: 'Metrics', type: 'step', style: { stroke: '#ef4444', strokeDasharray: '5 5' } },
  { id: 'e34', source: 'monitoring', target: 'transaction-processor', label: 'Metrics', type: 'step', style: { stroke: '#ef4444', strokeDasharray: '5 5' } },
  { id: 'e35', source: 'monitoring', target: 'database', label: 'DB Metrics', type: 'step', style: { stroke: '#ef4444', strokeDasharray: '5 5' } },
  { id: 'e36', source: 'monitoring', target: 'api-gateway', label: 'API Metrics', type: 'step', style: { stroke: '#ef4444', strokeDasharray: '5 5' } },
  
  // SIEM connections
  { id: 'e37', source: 'siem', target: 'audit-log', label: 'Log Analysis', type: 'step', style: { stroke: '#ef4444', strokeDasharray: '5 5' } },
  { id: 'e38', source: 'siem', target: 'waf', label: 'Security Rules', type: 'step', style: { stroke: '#ef4444', strokeDasharray: '5 5' } },
  { id: 'e39', source: 'siem', target: 'monitoring', label: 'Alerts', type: 'step', style: { stroke: '#ef4444', strokeDasharray: '5 5' } },
  
  // Response flows (dashed lines)
  { id: 'e40', source: 'api-gateway', target: 'waf', label: 'Response', type: 'smoothstep', style: { stroke: '#94a3b8', strokeDasharray: '5 5' } },
  { id: 'e41', source: 'waf', target: 'load-balancer', label: 'Response', type: 'smoothstep', style: { stroke: '#94a3b8', strokeDasharray: '5 5' } },
  { id: 'e42', source: 'load-balancer', target: 'web-app', label: 'Response', type: 'smoothstep', style: { stroke: '#94a3b8', strokeDasharray: '5 5' } },
  { id: 'e43', source: 'load-balancer', target: 'mobile-app', label: 'Response', type: 'smoothstep', style: { stroke: '#94a3b8', strokeDasharray: '5 5' } }
];