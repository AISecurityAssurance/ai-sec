import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  variables: string[];
  analysisType: string;
  version: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface PromptSettings {
  temperature: number;
  maxTokens: number;
  topP: number;
  frequencyPenalty: number;
  presencePenalty: number;
  preferredModels: {
    primary: string;
    fallback: string;
  };
  useGeneratedArtifacts: boolean;
  chainAnalyses: boolean;
}

interface PromptState {
  templates: PromptTemplate[];
  settings: PromptSettings;
  activeTemplateId: string | null;
  
  // Actions
  addTemplate: (template: Omit<PromptTemplate, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateTemplate: (id: string, updates: Partial<PromptTemplate>) => void;
  deleteTemplate: (id: string) => void;
  setActiveTemplate: (id: string) => void;
  updateSettings: (settings: Partial<PromptSettings>) => void;
  duplicateTemplate: (id: string, newName: string) => void;
  importTemplates: (templates: PromptTemplate[]) => void;
  exportTemplates: () => string;
}

const defaultPromptSettings: PromptSettings = {
  temperature: 0.7,
  maxTokens: 4096,
  topP: 0.9,
  frequencyPenalty: 0,
  presencePenalty: 0,
  preferredModels: {
    primary: 'gpt-4',
    fallback: 'gpt-3.5-turbo'
  },
  useGeneratedArtifacts: true,
  chainAnalyses: true
};

// Default prompt templates
const defaultTemplates: PromptTemplate[] = [
  {
    id: 'stpa-sec-default',
    name: 'STPA-Sec Analysis',
    description: 'Default prompt for STPA-Sec security analysis',
    template: `Perform a comprehensive STPA-Sec analysis on the following system:

System: {systemName}
Description: {systemDescription}
Context: {context}

Please identify:
1. Losses (security compromises)
2. System-level security constraints
3. Control structure with security considerations
4. Unsafe/unsecure control actions
5. Loss scenarios

Format the output as structured data.`,
    variables: ['systemName', 'systemDescription', 'context'],
    analysisType: 'stpa-sec',
    version: '1.0.0',
    isActive: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: 'stride-default',
    name: 'STRIDE Analysis',
    description: 'Default prompt for STRIDE threat modeling',
    template: `Perform a STRIDE threat analysis on the following system:

System: {systemName}
Components: {components}
Data Flows: {dataFlows}

For each component and data flow, identify threats in these categories:
- Spoofing
- Tampering
- Repudiation
- Information Disclosure
- Denial of Service
- Elevation of Privilege

Provide mitigations for each identified threat.`,
    variables: ['systemName', 'components', 'dataFlows'],
    analysisType: 'stride',
    version: '1.0.0',
    isActive: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];

export const usePromptStore = create<PromptState>()(
  persist(
    (set, get) => ({
      templates: defaultTemplates,
      settings: defaultPromptSettings,
      activeTemplateId: null,
      
      addTemplate: (template) =>
        set((state) => ({
          templates: [
            ...state.templates,
            {
              ...template,
              id: `template-${Date.now()}`,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString()
            }
          ]
        })),
        
      updateTemplate: (id, updates) =>
        set((state) => ({
          templates: state.templates.map((t) =>
            t.id === id
              ? { ...t, ...updates, updatedAt: new Date().toISOString() }
              : t
          )
        })),
        
      deleteTemplate: (id) =>
        set((state) => ({
          templates: state.templates.filter((t) => t.id !== id),
          activeTemplateId: state.activeTemplateId === id ? null : state.activeTemplateId
        })),
        
      setActiveTemplate: (id) =>
        set({ activeTemplateId: id }),
        
      updateSettings: (settings) =>
        set((state) => ({
          settings: { ...state.settings, ...settings }
        })),
        
      duplicateTemplate: (id, newName) => {
        const state = get();
        const original = state.templates.find((t) => t.id === id);
        if (original) {
          const duplicate = {
            ...original,
            id: `template-${Date.now()}`,
            name: newName,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          };
          set((state) => ({
            templates: [...state.templates, duplicate]
          }));
        }
      },
      
      importTemplates: (templates) =>
        set((state) => ({
          templates: [...state.templates, ...templates]
        })),
        
      exportTemplates: () => {
        const state = get();
        return JSON.stringify({
          templates: state.templates,
          settings: state.settings,
          version: '1.0.0',
          exportDate: new Date().toISOString()
        }, null, 2);
      }
    }),
    {
      name: 'security-platform-prompts',
      partialize: (state) => ({
        templates: state.templates,
        settings: state.settings,
        activeTemplateId: state.activeTemplateId
      })
    }
  )
);

// Helper to get active template
export function getActiveTemplate(state: PromptState): PromptTemplate | null {
  return state.templates.find(t => t.id === state.activeTemplateId) || null;
}

// Helper to get templates by analysis type
export function getTemplatesByType(state: PromptState, analysisType: string): PromptTemplate[] {
  return state.templates.filter(t => t.analysisType === analysisType && t.isActive);
}