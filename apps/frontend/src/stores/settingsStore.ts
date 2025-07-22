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

interface SettingsState {
  tokenEstimation: TokenEstimationSettings;
  panels: PanelSettings;
  analysis: AnalysisSettings;
  general: GeneralSettings;
  
  // Actions
  updateTokenEstimation: (settings: Partial<TokenEstimationSettings>) => void;
  updatePanelSettings: (settings: Partial<PanelSettings>) => void;
  updateAnalysisSettings: (settings: Partial<AnalysisSettings>) => void;
  updateGeneralSettings: (settings: Partial<GeneralSettings>) => void;
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
        
      resetToDefaults: () => set(defaultSettings),
      
      exportSettings: () => {
        const state = get();
        const exportData = {
          tokenEstimation: state.tokenEstimation,
          panels: state.panels,
          analysis: state.analysis,
          general: state.general,
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
              general: imported.general
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
        general: state.general
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