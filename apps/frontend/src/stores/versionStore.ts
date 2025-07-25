import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Version {
  id: string;
  name: string;
  description: string;
  baseVersion?: string; // ID of the version this was forked from
  createdAt: Date;
  lastModified: Date;
  isDemo: boolean;
  isActive: boolean;
}

interface VersionedData {
  versionId: string;
  data: any; // This will hold the actual analysis data
}

interface VersionStore {
  // Current active version
  activeVersionId: string;
  
  // All versions
  versions: Version[];
  
  // Versioned data storage
  versionedData: Record<string, VersionedData>;
  
  // Actions
  createVersion: (name: string, description: string, baseVersionId?: string) => string;
  switchVersion: (versionId: string) => void;
  updateVersionData: (versionId: string, data: any) => void;
  getVersionData: (versionId: string) => any;
  deleteVersion: (versionId: string) => void;
  getActiveVersionData: () => any;
}

// Demo version ID is constant
const DEMO_VERSION_ID = 'demo-v1';

export const useVersionStore = create<VersionStore>()(
  persist(
    (set, get) => ({
      activeVersionId: DEMO_VERSION_ID,
      
      versions: [
        {
          id: DEMO_VERSION_ID,
          name: 'Demo Data',
          description: 'Original demonstration data',
          createdAt: new Date('2024-01-01'),
          lastModified: new Date('2024-01-01'),
          isDemo: true,
          isActive: true
        }
      ],
      
      versionedData: {},
      
      createVersion: (name, description, baseVersionId) => {
        const newVersionId = `v-${Date.now()}`;
        const baseVersion = baseVersionId || get().activeVersionId;
        const baseData = get().getVersionData(baseVersion);
        
        const newVersion: Version = {
          id: newVersionId,
          name,
          description,
          baseVersion,
          createdAt: new Date(),
          lastModified: new Date(),
          isDemo: false,
          isActive: false
        };
        
        set(state => ({
          versions: [...state.versions, newVersion],
          versionedData: {
            ...state.versionedData,
            [newVersionId]: {
              versionId: newVersionId,
              data: structuredClone(baseData || {})
            }
          }
        }));
        
        return newVersionId;
      },
      
      switchVersion: (versionId) => {
        const version = get().versions.find(v => v.id === versionId);
        if (!version) return;
        
        set(state => ({
          activeVersionId: versionId,
          versions: state.versions.map(v => ({
            ...v,
            isActive: v.id === versionId
          }))
        }));
      },
      
      updateVersionData: (versionId, data) => {
        // Don't allow updating demo data
        if (versionId === DEMO_VERSION_ID) {
          console.warn('Cannot modify demo data. Create a new version first.');
          return;
        }
        
        set(state => ({
          versionedData: {
            ...state.versionedData,
            [versionId]: {
              versionId,
              data
            }
          },
          versions: state.versions.map(v => 
            v.id === versionId 
              ? { ...v, lastModified: new Date() }
              : v
          )
        }));
      },
      
      getVersionData: (versionId) => {
        const state = get();
        
        // For demo version, return null to signal that demo data should be used
        if (versionId === DEMO_VERSION_ID) {
          return null;
        }
        
        return state.versionedData[versionId]?.data || null;
      },
      
      deleteVersion: (versionId) => {
        // Don't allow deleting demo version
        if (versionId === DEMO_VERSION_ID) return;
        
        set(state => {
          const newVersionedData = { ...state.versionedData };
          delete newVersionedData[versionId];
          
          return {
            versions: state.versions.filter(v => v.id !== versionId),
            versionedData: newVersionedData,
            // If we're deleting the active version, switch to demo
            activeVersionId: state.activeVersionId === versionId 
              ? DEMO_VERSION_ID 
              : state.activeVersionId
          };
        });
      },
      
      getActiveVersionData: () => {
        const state = get();
        return state.getVersionData(state.activeVersionId);
      }
    }),
    {
      name: 'version-store'
    }
  )
);