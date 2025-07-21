import type { ReactNode } from 'react';
import './StandaloneWrapper.css';

interface StandaloneWrapperProps {
  title: string;
  children: ReactNode;
}

export default function StandaloneWrapper({ title, children }: StandaloneWrapperProps) {
  return (
    <div className="standalone-wrapper">
      <div className="standalone-header">
        <h1>{title}</h1>
      </div>
      <div className="standalone-content">
        {children}
      </div>
    </div>
  );
}