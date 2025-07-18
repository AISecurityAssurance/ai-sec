// Chat and Conversation Types

export interface ChatMessage {
  id: string;
  sessionId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: MessageMetadata;
  attachments?: Attachment[];
}

export interface MessageMetadata {
  // Analysis context
  analysisId?: string;
  findingIds?: string[];
  
  // Actions taken
  actions?: MessageAction[];
  
  // UI hints
  suggestions?: string[];
  highlightedFindings?: string[];
  
  // Token usage
  tokenUsage?: {
    prompt: number;
    completion: number;
    total: number;
  };
}

export interface MessageAction {
  type: 'refine_finding' | 'explore_impact' | 'generate_mitigation' | 'run_analysis' | 'update_diagram';
  target: string;
  result?: any;
}

export interface Attachment {
  id: string;
  type: 'file' | 'code' | 'diagram' | 'finding';
  name: string;
  content?: string;
  url?: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  id: string;
  projectId: string;
  userId: string;
  startedAt: Date;
  lastMessageAt: Date;
  messages: ChatMessage[];
  context: ChatContext;
}

export interface ChatContext {
  recentMessages: ChatMessage[];
  relevantFindings: any[]; // Analysis findings
  codeReferences: CodeReference[];
  activeAnalysis?: string;
  selectedFindings?: string[];
}

export interface CodeReference {
  file: string;
  line: number;
  content: string;
  relevance: number;
}

// CSAT Types
export interface CSATResponse {
  id: string;
  sessionId: string;
  userId: string;
  timestamp: Date;
  ratings: {
    overall: number; // 1-5
    accuracy: number; // 1-5
    completeness: number; // 1-5
    usability: number; // 1-5
  };
  npsScore?: number; // 0-10
  feedback?: string;
  featureRequests?: string[];
  bugReports?: BugReport[];
}

export interface BugReport {
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  reproducible: boolean;
  steps?: string;
  screenshot?: string; // Base64 encoded
}