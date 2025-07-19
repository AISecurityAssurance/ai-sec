import { Link, useLocation } from 'react-router-dom';
import { Shield, Settings, Beaker, MessageSquare } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';
import './AppSwitcher.css';

const apps = [
  { path: '/analysis', label: 'Analysis', icon: Shield },
  { path: '/admin', label: 'Admin', icon: Settings },
  { path: '/arena', label: 'Testing Arena', icon: Beaker },
  { path: '/feedback', label: 'Feedback', icon: MessageSquare },
];

export default function AppSwitcher() {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const currentApp = apps.find(app => location.pathname.startsWith(app.path));

  return (
    <div className="app-switcher">
      <div className="app-switcher-apps">
        {apps.map(app => {
          const Icon = app.icon;
          const isActive = location.pathname.startsWith(app.path);
          
          return (
            <Link
              key={app.path}
              to={app.path}
              className={`app-btn ${isActive ? 'active' : ''}`}
            >
              <Icon size={16} />
              <span>{app.label}</span>
            </Link>
          );
        })}
      </div>
      
      <button
        className="theme-toggle"
        onClick={toggleTheme}
        title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
      >
        {theme === 'dark' ? '☀️' : '🌙'}
      </button>
    </div>
  );
}