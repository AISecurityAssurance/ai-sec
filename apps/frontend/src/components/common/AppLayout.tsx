import type { ReactNode } from 'react';
import AppSwitcher from './AppSwitcher';
import './AppLayout.css';

interface AppLayoutProps {
  children: ReactNode;
  header: ReactNode;
}

export default function AppLayout({ children, header }: AppLayoutProps) {
  return (
    <div className="app-layout">
      <div className="app-header-wrapper">
        {header}
        <div className="app-navigation">
          <AppSwitcher />
        </div>
      </div>
      <div className="app-body">
        {children}
      </div>
    </div>
  );
}