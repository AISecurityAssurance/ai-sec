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

interface AnalysisState {
  // Project info
  projectId: string | null;
  projectVersion: string;
  
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
  
  // Actions
  setProjectId: (id: string | null) => void;
  setProjectVersion: (version: string) => void;
  updateSystemDescription: (data: Partial<typeof initialSystemDescription>) => void;
  updateLosses: (data: typeof initialLosses) => void;
  updateHazards: (data: typeof initialHazards) => void;
  updateControllers: (data: typeof initialControllers) => void;
  updateControlActions: (data: typeof initialControlActions) => void;
  updateUcas: (data: typeof initialUcas) => void;
  updateScenarios: (data: typeof initialScenarios) => void;
  setEnabledAnalyses: (analyses: Record<string, boolean>) => void;
  setDemoMode: (enabled: boolean) => void;
}

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set) => ({
      // Initial state
      projectId: null,
      projectVersion: '1.0.0',
      systemDescription: initialSystemDescription,
      losses: initialLosses,
      hazards: initialHazards,
      controllers: initialControllers,
      controlActions: initialControlActions,
      ucas: initialUcas,
      scenarios: initialScenarios,
      enabledAnalyses: {
        'stpa-sec': true,
        'stride': true,
        'pasta': true,
        'maestro': false,
        'dread': true,
        'linddun': false,
        'hazop': false,
        'octave': false,
        'cve': false
      },
      demoMode: true,
      
      // Actions
      setProjectId: (id) => set({ projectId: id }),
      setProjectVersion: (version) => set({ projectVersion: version }),
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
      setDemoMode: (enabled) => set({ demoMode: enabled })
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