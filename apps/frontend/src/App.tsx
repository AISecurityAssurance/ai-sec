import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useTheme } from './hooks/useTheme';
import UserApp from './apps/user/UserApp';
import AdminApp from './apps/admin/AdminApp';
import ArenaApp from './apps/arena/ArenaApp';
import CSATApp from './apps/csat/CSATApp';
import AppSwitcher from './components/common/AppSwitcher';
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
      <div className="app-container">
        <Routes>
          <Route path="/analysis/*" element={<UserApp />} />
          <Route path="/admin/*" element={<AdminApp />} />
          <Route path="/arena/*" element={<ArenaApp />} />
          <Route path="/feedback/*" element={<CSATApp />} />
          <Route path="/" element={<Navigate to="/analysis" replace />} />
        </Routes>
      </div>
    </ErrorBoundary>
  );
}

export default App;