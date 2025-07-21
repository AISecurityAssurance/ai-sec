import type { Node, Edge } from '@xyflow/react';

export const controlFlowNodes: Node[] = [
  {
    id: 'user',
    type: 'default',
    position: { x: 100, y: 50 },
    data: { label: 'End Users' }
  },
  {
    id: 'web-app',
    type: 'default',
    position: { x: 350, y: 50 },
    data: { label: 'Web Application' }
  },
  {
    id: 'mobile-app',
    type: 'default',
    position: { x: 350, y: 150 },
    data: { label: 'Mobile Application' }
  },
  {
    id: 'api-gateway',
    type: 'default',
    position: { x: 600, y: 100 },
    data: { label: 'API Gateway' }
  },
  {
    id: 'auth-service',
    type: 'default',
    position: { x: 850, y: 50 },
    data: { label: 'Authentication Service' }
  },
  {
    id: 'transaction-processor',
    type: 'default',
    position: { x: 850, y: 150 },
    data: { label: 'Transaction Processor' }
  },
  {
    id: 'fraud-detection',
    type: 'default',
    position: { x: 850, y: 250 },
    data: { label: 'Fraud Detection System' }
  },
  {
    id: 'database',
    type: 'default',
    position: { x: 1100, y: 100 },
    data: { label: 'Core Database' }
  },
  {
    id: 'audit-log',
    type: 'default',
    position: { x: 1100, y: 200 },
    data: { label: 'Audit Log System' }
  },
  {
    id: 'third-party',
    type: 'default',
    position: { x: 600, y: 350 },
    data: { label: 'Third-party Services' }
  },
  {
    id: 'admin',
    type: 'default',
    position: { x: 100, y: 250 },
    data: { label: 'System Administrators' }
  },
  {
    id: 'admin-portal',
    type: 'default',
    position: { x: 350, y: 250 },
    data: { label: 'Admin Portal' }
  },
  {
    id: 'monitoring',
    type: 'default',
    position: { x: 600, y: 450 },
    data: { label: 'Monitoring & Alerts' }
  }
];

export const controlFlowEdges: Edge[] = [
  // User interactions
  { id: 'e1', source: 'user', target: 'web-app', label: 'HTTPS Requests' },
  { id: 'e2', source: 'user', target: 'mobile-app', label: 'API Calls' },
  
  // Frontend to backend
  { id: 'e3', source: 'web-app', target: 'api-gateway', label: 'REST API' },
  { id: 'e4', source: 'mobile-app', target: 'api-gateway', label: 'REST API' },
  
  // API Gateway routing
  { id: 'e5', source: 'api-gateway', target: 'auth-service', label: 'Auth Requests' },
  { id: 'e6', source: 'api-gateway', target: 'transaction-processor', label: 'Transaction Requests' },
  { id: 'e7', source: 'api-gateway', target: 'third-party', label: 'External API Calls' },
  
  // Service interactions
  { id: 'e8', source: 'auth-service', target: 'database', label: 'User Queries' },
  { id: 'e9', source: 'transaction-processor', target: 'database', label: 'Transaction Data' },
  { id: 'e10', source: 'transaction-processor', target: 'fraud-detection', label: 'Risk Assessment' },
  { id: 'e11', source: 'fraud-detection', target: 'transaction-processor', label: 'Risk Score', type: 'step' },
  
  // Audit logging
  { id: 'e12', source: 'auth-service', target: 'audit-log', label: 'Auth Events' },
  { id: 'e13', source: 'transaction-processor', target: 'audit-log', label: 'Transaction Events' },
  { id: 'e14', source: 'api-gateway', target: 'audit-log', label: 'API Access Logs' },
  
  // Admin interactions
  { id: 'e15', source: 'admin', target: 'admin-portal', label: 'Admin Access' },
  { id: 'e16', source: 'admin-portal', target: 'api-gateway', label: 'Admin API' },
  { id: 'e17', source: 'admin-portal', target: 'monitoring', label: 'Monitor Access' },
  
  // Monitoring connections
  { id: 'e18', source: 'monitoring', target: 'auth-service', label: 'Service Health', type: 'step' },
  { id: 'e19', source: 'monitoring', target: 'transaction-processor', label: 'Service Health', type: 'step' },
  { id: 'e20', source: 'monitoring', target: 'database', label: 'DB Metrics', type: 'step' },
  
  // Response flows (dashed lines)
  { id: 'e21', source: 'api-gateway', target: 'web-app', label: 'Responses', type: 'step' },
  { id: 'e22', source: 'api-gateway', target: 'mobile-app', label: 'Responses', type: 'step' }
];