import type { ReactNode } from 'react';
import './SimpleLayout.css';

interface SimpleLayoutProps {
  children: ReactNode;
}

export default function SimpleLayout({ children }: SimpleLayoutProps) {
  return (
    <div className="simple-layout">
      {children}
    </div>
  );
}