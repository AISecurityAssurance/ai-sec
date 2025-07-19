import React from 'react';
import { ExternalLink, Copy } from 'lucide-react';
import './ContextMenu.css';

interface ContextMenuItem {
  label: string;
  action: () => void;
  icon?: React.ReactNode;
}

interface ContextMenuProps {
  x: number;
  y: number;
  items: ContextMenuItem[];
  menuRef: React.RefObject<HTMLDivElement>;
}

export default function ContextMenu({ x, y, items, menuRef }: ContextMenuProps) {
  return (
    <div
      ref={menuRef}
      className="context-menu"
      style={{
        position: 'fixed',
        left: `${x}px`,
        top: `${y}px`,
      }}
    >
      {items.map((item, index) => (
        <button
          key={index}
          className="context-menu-item"
          onClick={(e) => {
            e.stopPropagation();
            item.action();
          }}
        >
          {item.icon && <span className="context-menu-icon">{item.icon}</span>}
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  );
}