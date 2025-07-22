import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export type TokenCalculationMethod = 'chars' | 'bytes' | 'custom';
export type OverflowBehavior = 'warn' | 'block';

interface TokenEstimationSettings {
  calculationMethod: TokenCalculationMethod;
  charsPerToken: number;
  bytesPerToken: number;
  customTokenizer?: string;
  maxTokens: number;
  overflowBehavior: OverflowBehavior;
}

interface PanelSettings {
  leftPanelWidth: number;
  middlePanelWidth: number;
  rightPanelWidth: number;
  leftPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;
}

interface AnalysisSettings {
  defaultAnalysisOrder: string[];
  autoRunAnalysis: boolean;
  preserveLockedSections: boolean;
}

interface GeneralSettings {
  demoMode: boolean;
  theme: 'light' | 'dark' | 'system';
  autoSaveInterval: number; // in seconds
}

export type ModelProvider = 'anthropic' | 'openai' | 'groq' | 'gemini' | 'ollama' | 'custom';
export type AuthMethod = 'api-key' | 'oauth' | 'none';

interface ModelConfig {
  provider: ModelProvider;
  authMethod: AuthMethod;
  apiKey?: string;
  apiEndpoint?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  isEnabled: boolean;
}

interface ModelSettings {
  activeProvider: ModelProvider;
  providers: Record<ModelProvider, ModelConfig>;
  defaultTemperature: number;
  defaultMaxTokens: number;
  streamResponses: boolean;
  enableFallback: boolean;
  fallbackOrder: ModelProvider[];
}

interface SettingsState {
  tokenEstimation: TokenEstimationSettings;
  panels: PanelSettings;
  analysis: AnalysisSettings;
  general: GeneralSettings;
  models: ModelSettings;
  
  // Actions
  updateTokenEstimation: (settings: Partial<TokenEstimationSettings>) => void;
  updatePanelSettings: (settings: Partial<PanelSettings>) => void;
  updateAnalysisSettings: (settings: Partial<AnalysisSettings>) => void;
  updateGeneralSettings: (settings: Partial<GeneralSettings>) => void;
  updateModelSettings: (settings: Partial<ModelSettings>) => void;
  updateProviderConfig: (provider: ModelProvider, config: Partial<ModelConfig>) => void;
  resetToDefaults: () => void;
  exportSettings: () => string;
  importSettings: (settingsJson: string) => boolean;
}

const defaultSettings = {
  tokenEstimation: {
    calculationMethod: 'chars' as TokenCalculationMethod,
    charsPerToken: 4,
    bytesPerToken: 4,
    maxTokens: 250000,
    overflowBehavior: 'warn' as OverflowBehavior,
  },
  panels: {
    leftPanelWidth: 20,
    middlePanelWidth: 50,
    rightPanelWidth: 30,
    leftPanelCollapsed: false,
    rightPanelCollapsed: false,
  },
  analysis: {
    defaultAnalysisOrder: [
      'overview',
      'stpa-sec',
      'stride',
      'pasta',
      'dread',
      'maestro',
      'linddun',
      'hazop',
      'octave'
    ],
    autoRunAnalysis: false,
    preserveLockedSections: true,
  },
  general: {
    demoMode: true,
    theme: 'light' as const,
    autoSaveInterval: 30,
  },
  models: {
    activeProvider: 'anthropic' as ModelProvider,
    providers: {
      anthropic: {
        provider: 'anthropic',
        authMethod: 'api-key',
        apiKey: '',
        model: 'claude-3-opus-20240229',
        temperature: 0.7,
        maxTokens: 4096,
        isEnabled: false,
      },
      openai: {
        provider: 'openai',
        authMethod: 'api-key',
        apiKey: '',
        model: 'gpt-4-turbo-preview',
        temperature: 0.7,
        maxTokens: 4096,
        isEnabled: false,
      },
      groq: {
        provider: 'groq',
        authMethod: 'api-key',
        apiKey: '',
        model: 'llama2-70b-4096',
        temperature: 0.7,
        maxTokens: 4096,
        isEnabled: false,
      },
      gemini: {
        provider: 'gemini',
        authMethod: 'api-key',
        apiKey: '',
        model: 'gemini-pro',
        temperature: 0.7,
        maxTokens: 4096,
        isEnabled: false,
      },
      ollama: {
        provider: 'ollama',
        authMethod: 'none',
        apiEndpoint: 'http://localhost:11434',
        model: 'llama2',
        temperature: 0.7,
        maxTokens: 4096,
        isEnabled: false,
      },
      custom: {
        provider: 'custom',
        authMethod: 'api-key',
        apiKey: '',
        apiEndpoint: '',
        model: '',
        temperature: 0.7,
        maxTokens: 4096,
        isEnabled: false,
      },
    } as Record<ModelProvider, ModelConfig>,
    defaultTemperature: 0.7,
    defaultMaxTokens: 4096,
    streamResponses: true,
    enableFallback: false,
    fallbackOrder: ['anthropic', 'openai', 'groq', 'gemini', 'ollama'] as ModelProvider[],
  }
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      ...defaultSettings,
      
      updateTokenEstimation: (settings) =>
        set((state) => ({
          tokenEstimation: { ...state.tokenEstimation, ...settings }
        })),
        
      updatePanelSettings: (settings) =>
        set((state) => ({
          panels: { ...state.panels, ...settings }
        })),
        
      updateAnalysisSettings: (settings) =>
        set((state) => ({
          analysis: { ...state.analysis, ...settings }
        })),
        
      updateGeneralSettings: (settings) =>
        set((state) => ({
          general: { ...state.general, ...settings }
        })),
        
      updateModelSettings: (settings) =>
        set((state) => ({
          models: { ...state.models, ...settings }
        })),
        
      updateProviderConfig: (provider, config) =>
        set((state) => ({
          models: {
            ...state.models,
            providers: {
              ...state.models.providers,
              [provider]: { ...state.models.providers[provider], ...config }
            }
          }
        })),
        
      resetToDefaults: () => set(defaultSettings),
      
      exportSettings: () => {
        const state = get();
        const exportData = {
          tokenEstimation: state.tokenEstimation,
          panels: state.panels,
          analysis: state.analysis,
          general: state.general,
          models: state.models,
          version: '1.0.0',
          exportDate: new Date().toISOString()
        };
        return JSON.stringify(exportData, null, 2);
      },
      
      importSettings: (settingsJson) => {
        try {
          const imported = JSON.parse(settingsJson);
          if (imported.version && imported.tokenEstimation) {
            set({
              tokenEstimation: imported.tokenEstimation,
              panels: imported.panels,
              analysis: imported.analysis,
              general: imported.general,
              models: imported.models || defaultSettings.models
            });
            return true;
          }
          return false;
        } catch (error) {
          console.error('Failed to import settings:', error);
          return false;
        }
      }
    }),
    {
      name: 'security-platform-settings',
      partialize: (state) => ({
        tokenEstimation: state.tokenEstimation,
        panels: state.panels,
        analysis: state.analysis,
        general: state.general,
        models: state.models
      })
    }
  )
);

// Helper functions for token calculation
export function calculateTokens(content: string, settings: TokenEstimationSettings): number {
  switch (settings.calculationMethod) {
    case 'chars':
      return Math.ceil(content.length / settings.charsPerToken);
    case 'bytes':
      const bytes = new TextEncoder().encode(content).length;
      return Math.ceil(bytes / settings.bytesPerToken);
    case 'custom':
      // Placeholder for custom tokenizer integration
      console.warn('Custom tokenizer not implemented, falling back to chars');
      return Math.ceil(content.length / settings.charsPerToken);
    default:
      return Math.ceil(content.length / settings.charsPerToken);
  }
}

export function getTokenPercentage(usedTokens: number, maxTokens: number): number {
  return Math.min((usedTokens / maxTokens) * 100, 100);
}