import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useTheme } from './hooks/useTheme';
import AnalysisRoutes from './apps/analysis/routes';
import AdminApp from './apps/admin/AdminApp';
import SettingsApp from './apps/settings/SettingsApp';
import PromptsApp from './apps/prompts/PromptsApp';
import CSATApp from './apps/csat/CSATApp';
import TopNavBar from './components/common/TopNavBar';
import ErrorBoundary from './components/common/ErrorBoundary';
import './App.css';

function App() {
  const { theme } = useTheme();

  useEffect(() => {
    // Initialize theme on mount
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <ErrorBoundary>
      <TopNavBar />
      <div className="app-container">
        <Routes>
          <Route path="/analysis/*" element={<AnalysisRoutes />} />
          <Route path="/admin/*" element={<AdminApp />} />
          <Route path="/settings/*" element={<SettingsApp />} />
          <Route path="/prompts/*" element={<PromptsApp />} />
          <Route path="/feedback/*" element={<CSATApp />} />
          <Route path="/" element={<Navigate to="/analysis" replace />} />
        </Routes>
      </div>
    </ErrorBoundary>
  );
}

export default App;