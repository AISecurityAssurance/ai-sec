import { Routes, Route, Navigate } from 'react-router-dom';
import UserApp from './UserApp';
import StandaloneComponent from './components/StandaloneComponent';
import StandaloneAnalysisView from './components/StandaloneAnalysisView';
import StandaloneTemplateView from './components/StandaloneTemplateView';
import FocusedItemView from './components/FocusedItemView';

// Component types that can be opened in standalone windows
export const STANDALONE_COMPONENTS = {
  'control-diagram': 'Process Control Diagram',
  'losses': 'Losses',
  'hazards': 'Hazards/Vulnerabilities', 
  'controllers': 'Controllers',
  'control-actions': 'Control Actions',
  'ucas': 'Unsafe/Unsecure Control Actions',
  'scenarios': 'Causal Scenarios',
  'wargaming': 'Wargaming',
  'stride': 'STRIDE Analysis',
  'pasta': 'PASTA Analysis',
  'dread': 'DREAD Analysis',
  'overview': 'Analysis Overview'
} as const;

export type StandaloneComponentType = keyof typeof STANDALONE_COMPONENTS;

export default function UserRoutes() {
  return (
    <Routes>
      {/* Main application route */}
      <Route path="/" element={<UserApp />} />
      
      {/* Full analysis view routes */}
      <Route path="/view/:analysisType" element={<StandaloneAnalysisView />} />
      
      {/* Template-based analysis view routes */}
      <Route path="/template/:analysisType" element={<StandaloneTemplateView />} />
      <Route path="/template/:analysisType/:sectionId" element={<StandaloneTemplateView />} />
      
      {/* Standalone component routes */}
      <Route path="/component/:componentType" element={<StandaloneComponent />} />
      
      {/* Focused item view routes */}
      <Route path="/item/:itemType/:itemId" element={<FocusedItemView />} />
      
      {/* Redirect any unknown paths to main */}
      <Route path="*" element={<Navigate to="/analysis" replace />} />
    </Routes>
  );
}