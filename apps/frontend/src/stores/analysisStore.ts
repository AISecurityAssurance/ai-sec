import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';
import { useVersionStore } from './versionStore';
import { stpaSecApiService } from '../services/stpaSecApiService';
import type { 
  Loss, 
  Hazard, 
  Controller, 
  ControlAction, 
  UCA, 
  CausalScenario 
} from '@security-platform/types';

interface AnalysisStatus {
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  message?: string;
}

interface AnalysisSection {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  content?: any;
  error?: string;
}

interface AnalysisResult {
  framework: string;
  sections: AnalysisSection[];
  status: AnalysisStatus;
  startedAt?: string;
  completedAt?: string;
}

interface SystemDescription {
  name: string;
  description: string;
  fullDescription?: string;
  boundaries: {
    included: string[];
    excluded: string[];
  };
  assumptions: string[];
  missionStatement: {
    purpose: string;
    method: string;
    goals: string[];
    constraints: string[];
  };
  context?: string;
}

interface AnalysisState {
  // Project info
  projectId: string | null;
  projectVersion: string;
  
  // Analysis info
  currentAnalysisId: string | null;
  analysisStatus: AnalysisStatus;
  analysisResults: Record<string, AnalysisResult>;
  
  // System data
  systemDescription: SystemDescription;
  
  // STPA-Sec data
  losses: Loss[];
  hazards: Hazard[];
  controllers: Controller[];
  controlActions: ControlAction[];
  ucas: UCA[];
  scenarios: CausalScenario[];
  
  // UI state
  enabledAnalyses: Record<string, boolean>;
  demoMode: boolean;
  hasUnsavedChanges: boolean;
  isLoadingData: boolean;
  dataLoadError: string | null;
  
  // Actions
  setProjectId: (id: string | null) => void;
  setProjectVersion: (version: string) => void;
  setCurrentAnalysisId: (id: string | null) => void;
  updateAnalysisStatus: (status: AnalysisStatus) => void;
  updateAnalysisResult: (framework: string, result: AnalysisResult) => void;
  updateSectionResult: (framework: string, sectionId: string, section: Partial<AnalysisSection>) => void;
  updateSystemDescription: (data: Partial<SystemDescription>) => void;
  updateLosses: (data: Loss[]) => void;
  updateHazards: (data: Hazard[]) => void;
  updateControllers: (data: Controller[]) => void;
  updateControlActions: (data: ControlAction[]) => void;
  updateUcas: (data: UCA[]) => void;
  updateScenarios: (data: CausalScenario[]) => void;
  setEnabledAnalyses: (analyses: Record<string, boolean>) => void;
  setDemoMode: (enabled: boolean) => void;
  setHasUnsavedChanges: (hasChanges: boolean) => void;
  clearAnalysisResults: () => void;
  resetToDemoData: () => void;
  loadVersionData: (versionId: string) => void;
  loadDataFromApi: () => Promise<void>;
}

export const useAnalysisStore = create<AnalysisState>()(
  subscribeWithSelector(
    persist<AnalysisState>(
    (set) => ({
      // Initial state - empty until loaded from database
      projectId: null,
      projectVersion: '1.0.0',
      currentAnalysisId: null,
      analysisStatus: { status: 'pending', progress: 0 },
      analysisResults: {},
      systemDescription: {
        name: '',
        description: '',
        boundaries: {
          included: [],
          excluded: []
        },
        assumptions: [],
        missionStatement: {
          purpose: '',
          method: '',
          goals: [],
          constraints: []
        }
      },
      losses: [],
      hazards: [],
      controllers: [],
      controlActions: [],
      ucas: [],
      scenarios: [],
      enabledAnalyses: {},
      demoMode: false,
      hasUnsavedChanges: false,
      isLoadingData: true,  // Start loading immediately
      dataLoadError: null,
      
      // Actions
      setProjectId: (id) => set({ projectId: id }),
      setProjectVersion: (version) => set({ projectVersion: version }),
      setCurrentAnalysisId: (id) => set({ currentAnalysisId: id }),
      updateAnalysisStatus: (status) => set({ analysisStatus: status }),
      
      updateAnalysisResult: (framework, result) => set((state) => ({
        analysisResults: {
          ...state.analysisResults,
          [framework]: result
        }
      })),
      
      updateSectionResult: (framework, sectionId, section) => set((state) => {
        const result = state.analysisResults[framework];
        if (!result) return state;
        
        const updatedSections = result.sections.map(s => 
          s.id === sectionId ? { ...s, ...section } : s
        );
        
        return {
          analysisResults: {
            ...state.analysisResults,
            [framework]: {
              ...result,
              sections: updatedSections
            }
          }
        };
      }),
      
      updateSystemDescription: (data) => set((state) => ({
        systemDescription: { ...state.systemDescription, ...data },
        hasUnsavedChanges: true
      })),
      
      updateLosses: (data) => set({ losses: data }),
      updateHazards: (data) => set({ hazards: data }),
      updateControllers: (data) => set({ controllers: data }),
      updateControlActions: (data) => set({ controlActions: data }),
      updateUcas: (data) => set({ ucas: data }),
      updateScenarios: (data) => set({ scenarios: data }),
      setEnabledAnalyses: (analyses) => set({ enabledAnalyses: analyses }),
      setDemoMode: (enabled) => set({ demoMode: enabled }),
      setHasUnsavedChanges: (hasChanges) => set({ hasUnsavedChanges: hasChanges }),
      clearAnalysisResults: () => set({ 
        analysisResults: {}, 
        analysisStatus: { status: 'pending', progress: 0 },
        currentAnalysisId: null,
        hasUnsavedChanges: false 
      }),
      
      resetToDemoData: () => {
        // This function should now load from database, not use mock data
        const state = useAnalysisStore.getState();
        state.loadDataFromApi();
      },
      
      loadDataFromApi: async () => {
        set({ isLoadingData: true, dataLoadError: null });
        
        try {
          const data = await stpaSecApiService.loadAnalysisData();
          
          // Only use data from API, no fallback to mock data
          set({
            losses: data.losses || [],
            hazards: data.hazards || [],
            controllers: data.controllers || [],
            controlActions: data.controlActions || [],
            ucas: data.ucas || [],
            scenarios: data.causalScenarios || [],
            isLoadingData: false,
            dataLoadError: null
          });
        } catch (error) {
          console.error('Failed to load data from API:', error);
          set({ 
            isLoadingData: false, 
            dataLoadError: 'Failed to connect to database. Please ensure the backend is running.' 
          });
          // DO NOT fall back to mock data - let the system show the error
          // Clear any existing data to make it obvious something is wrong
          set({
            losses: [],
            hazards: [],
            controllers: [],
            controlActions: [],
            ucas: [],
            scenarios: []
          });
        }
      },
      
      loadVersionData: (versionId) => {
        const versionStore = useVersionStore.getState();
        const versionData = versionStore.getVersionData(versionId);
        
        // For demo version, load from database
        if (versionId === 'demo-v1') {
          // Load from database API
          const state = useAnalysisStore.getState();
          state.loadDataFromApi();
        } else if (versionData) {
          // Load the versioned data (for non-demo versions)
          // This would be data from previous analyses stored locally
          set({
            systemDescription: versionData.systemDescription || {},
            losses: versionData.losses || [],
            hazards: versionData.hazards || [],
            controllers: versionData.controllers || [],
            controlActions: versionData.controlActions || [],
            ucas: versionData.ucas || [],
            scenarios: versionData.scenarios || [],
            hasUnsavedChanges: false
          });
        } else {
          // No data available - clear everything
          set({
            systemDescription: {
              name: '',
              description: '',
              boundaries: {
                included: [],
                excluded: []
              },
              assumptions: [],
              missionStatement: {
                purpose: '',
                method: '',
                goals: [],
                constraints: []
              }
            },
            losses: [],
            hazards: [],
            controllers: [],
            controlActions: [],
            ucas: [],
            scenarios: [],
            hasUnsavedChanges: false,
            analysisResults: {},
            analysisStatus: { status: 'pending', progress: 0 },
            currentAnalysisId: null
          });
        }
      }
    }),
    {
      name: 'analysis-storage',
      partialize: (state) => {
        // Don't persist demo data to prevent modifications from carrying over
        const versionStore = useVersionStore.getState();
        if (versionStore.activeVersionId === 'demo-v1' || state.demoMode) {
          // Only persist non-data settings for demo mode
          return {
            projectId: state.projectId,
            projectVersion: state.projectVersion,
            enabledAnalyses: state.enabledAnalyses,
            demoMode: state.demoMode
          };
        }
        
        // For non-demo versions, persist everything
        return {
          projectId: state.projectId,
          projectVersion: state.projectVersion,
          systemDescription: state.systemDescription,
          losses: state.losses,
          hazards: state.hazards,
          controllers: state.controllers,
          controlActions: state.controlActions,
          ucas: state.ucas,
          scenarios: state.scenarios,
          enabledAnalyses: state.enabledAnalyses,
          demoMode: state.demoMode
        };
      }
    }
  )
  )
);

// Subscribe to version changes
useVersionStore.subscribe(
  (state) => state.activeVersionId,
  (activeVersionId) => {
    const analysisStore = useAnalysisStore.getState();
    analysisStore.loadVersionData(activeVersionId);
  }
);