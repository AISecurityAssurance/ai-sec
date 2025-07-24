import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  losses as initialLosses,
  hazards as initialHazards,
  controllers as initialControllers,
  controlActions as initialControlActions,
  ucas as initialUcas,
  causalScenarios as initialScenarios
} from '../apps/user/mockData/stpaSecData';
import { systemDescription as initialSystemDescription } from '../apps/user/mockData/systemData';

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

interface AnalysisState {
  // Project info
  projectId: string | null;
  projectVersion: string;
  
  // Analysis info
  currentAnalysisId: string | null;
  analysisStatus: AnalysisStatus;
  analysisResults: Record<string, AnalysisResult>;
  
  // System data
  systemDescription: typeof initialSystemDescription;
  
  // STPA-Sec data
  losses: typeof initialLosses;
  hazards: typeof initialHazards;
  controllers: typeof initialControllers;
  controlActions: typeof initialControlActions;
  ucas: typeof initialUcas;
  scenarios: typeof initialScenarios;
  
  // UI state
  enabledAnalyses: Record<string, boolean>;
  demoMode: boolean;
  hasUnsavedChanges: boolean;
  
  // Actions
  setProjectId: (id: string | null) => void;
  setProjectVersion: (version: string) => void;
  setCurrentAnalysisId: (id: string | null) => void;
  updateAnalysisStatus: (status: AnalysisStatus) => void;
  updateAnalysisResult: (framework: string, result: AnalysisResult) => void;
  updateSectionResult: (framework: string, sectionId: string, section: Partial<AnalysisSection>) => void;
  updateSystemDescription: (data: Partial<typeof initialSystemDescription>) => void;
  updateLosses: (data: typeof initialLosses) => void;
  updateHazards: (data: typeof initialHazards) => void;
  updateControllers: (data: typeof initialControllers) => void;
  updateControlActions: (data: typeof initialControlActions) => void;
  updateUcas: (data: typeof initialUcas) => void;
  updateScenarios: (data: typeof initialScenarios) => void;
  setEnabledAnalyses: (analyses: Record<string, boolean>) => void;
  setDemoMode: (enabled: boolean) => void;
  setHasUnsavedChanges: (hasChanges: boolean) => void;
  clearAnalysisResults: () => void;
}

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set) => ({
      // Initial state
      projectId: null,
      projectVersion: '1.0.0',
      currentAnalysisId: null,
      analysisStatus: { status: 'pending', progress: 0 },
      analysisResults: {},
      systemDescription: initialSystemDescription,
      losses: initialLosses,
      hazards: initialHazards,
      controllers: initialControllers,
      controlActions: initialControlActions,
      ucas: initialUcas,
      scenarios: initialScenarios,
      enabledAnalyses: {
        'stpa-sec': false,
        'stride': false,
        'pasta': false,
        'maestro': false,
        'dread': false,
        'linddun': false,
        'hazop': false,
        'octave': false,
        'cve': false
      },
      demoMode: false,
      hasUnsavedChanges: false,
      
      // Actions
      setProjectId: (id) => set({ projectId: id }),
      setProjectVersion: (version) => set({ projectVersion: version }),
      setCurrentAnalysisId: (id) => set({ currentAnalysisId: id }),
      updateAnalysisStatus: (status) => set({ analysisStatus: status }),
      updateAnalysisResult: (framework, result) => set((state) => ({
        analysisResults: {
          ...state.analysisResults,
          [framework]: result
        },
        hasUnsavedChanges: true
      })),
      updateSectionResult: (framework, sectionId, section) => set((state) => {
        const frameworkResult = state.analysisResults[framework];
        if (!frameworkResult) return state;
        
        const updatedSections = frameworkResult.sections.map(s => 
          s.id === sectionId ? { ...s, ...section } : s
        );
        
        return {
          analysisResults: {
            ...state.analysisResults,
            [framework]: {
              ...frameworkResult,
              sections: updatedSections
            }
          },
          hasUnsavedChanges: true
        };
      }),
      updateSystemDescription: (data) => set((state) => ({
        systemDescription: { ...state.systemDescription, ...data }
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
      })
    }),
    {
      name: 'analysis-storage',
      partialize: (state) => ({
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
      })
    }
  )
);