import { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, FileText, SlidersHorizontal, Settings, MessageSquare, Menu, Sun, Moon } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';
import './TopNavBar.css';

const apps = [
  { path: '/analysis', label: 'Analysis', icon: Shield },
  { path: '/prompts', label: 'Prompt Settings', icon: FileText },
  { path: '/settings', label: 'Settings', icon: SlidersHorizontal },
  { path: '/admin', label: 'Admin', icon: Settings },
  { path: '/feedback', label: 'Feedback', icon: MessageSquare },
];

export default function TopNavBar() {
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);


  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMenuOpen]);

  const currentApp = apps.find(app => location.pathname.startsWith(app.path));

  return (
    <nav className="top-nav-bar">
      <div className="nav-content">
        <Link to="/" className="nav-logo">
          <Shield size={24} />
          <span className="nav-title">Security Analysis Platform</span>
        </Link>

        <div className="nav-right">
          {isMobile ? (
            <div className="mobile-menu-container" ref={menuRef}>
              <button
                className="hamburger-button"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                aria-label="Toggle menu"
              >
                <Menu size={24} />
              </button>
              
              {isMenuOpen && (
                <div className="mobile-dropdown">
                  {apps.map(app => {
                    const Icon = app.icon;
                    const isActive = location.pathname.startsWith(app.path);
                    
                    return (
                      <Link
                        key={app.path}
                        to={app.path}
                        className={`mobile-nav-item ${isActive ? 'active' : ''}`}
                        onClick={() => setIsMenuOpen(false)}
                      >
                        <Icon size={20} />
                        <span>{app.label}</span>
                      </Link>
                    );
                  })}
                  <button
                    className="mobile-nav-item theme-toggle-mobile"
                    onClick={() => {
                      toggleTheme();
                      setIsMenuOpen(false);
                    }}
                  >
                    {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                    <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="desktop-nav">
              {apps.map(app => {
                const isActive = location.pathname.startsWith(app.path);
                
                return (
                  <Link
                    key={app.path}
                    to={app.path}
                    className={`nav-link ${isActive ? 'active' : ''}`}
                  >
                    {app.label}
                  </Link>
                );
              })}
              <button
                className="theme-toggle"
                onClick={toggleTheme}
                aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}