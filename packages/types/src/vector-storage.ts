// packages/types/src/vector-storage.ts
export interface VectorDocument {
  id: string;
  content: string;
  metadata: {
    source: 'chat' | 'code' | 'analysis' | 'documentation';
    projectId: string;
    timestamp: Date;
    
    // For code
    filePath?: string;
    language?: string;
    functionName?: string;
    className?: string;
    
    // For chat
    userId?: string;
    sessionId?: string;
    role?: 'user' | 'assistant';
    
    // For analysis
    analysisType?: 'stpa-sec' | 'stride' | 'pasta' | 'maestro';
    findingId?: string;
    severity?: string;
  };
  embedding?: number[]; // Vector embedding
}

export interface VectorSearchResult {
  document: VectorDocument;
  score: number;
  highlights?: string[];
}

export interface SearchOptions {
  limit?: number;
  minScore?: number;
  filter?: Partial<VectorDocument['metadata']>;
}

export interface VectorStorageProvider {
  // Core operations
  upsert(documents: VectorDocument[]): Promise<void>;
  search(query: string, options?: SearchOptions): Promise<VectorSearchResult[]>;
  delete(ids: string[]): Promise<void>;
  
  // Specialized searches
  searchSimilarCode(codeSnippet: string, projectId: string): Promise<VectorSearchResult[]>;
  searchChatHistory(query: string, sessionId: string): Promise<VectorSearchResult[]>;
  searchRelatedFindings(finding: string, analysisId: string): Promise<VectorSearchResult[]>;
}