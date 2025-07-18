// Model Provider Protocol
export interface ModelProvider {
  name: string;
  
  // Core completion method
  complete(
    prompt: string,
    options?: ModelCompletionOptions
  ): Promise<ModelResponse>;
  
  // Capability checks
  supportsVision(): boolean;
  supportsTools(): boolean;
  supportsStreaming(): boolean;
  getContextWindow(): number;
  
  // Configuration
  configure(config: ModelConfig): void;
}

export interface ModelCompletionOptions {
  system?: string;
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  stopSequences?: string[];
  stream?: boolean;
  tools?: ToolDefinition[];
  images?: string[]; // Base64 encoded images for vision models
}

export interface ModelResponse {
  content: string;
  tokenUsage?: {
    prompt: number;
    completion: number;
    total: number;
  };
  finishReason?: 'stop' | 'length' | 'tool_calls' | 'error';
  toolCalls?: ToolCall[];
}

export interface ModelConfig {
  apiKey?: string;
  baseUrl?: string;
  model?: string;
  organization?: string;
  headers?: Record<string, string>;
}

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: any;
}

// Supported model providers
export type ModelProviderType = 'openai' | 'anthropic' | 'google' | 'ollama' | 'grok';

export interface ModelProviderFactory {
  create(type: ModelProviderType, config: ModelConfig): ModelProvider;
}