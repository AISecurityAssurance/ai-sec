import { useEffect, useRef, useState } from 'react';
import type { MouseEvent } from 'react';

interface ContextMenuOptions {
  x: number;
  y: number;
  items: Array<{
    label: string;
    action: () => void;
    icon?: React.ReactNode;
  }>;
}

export function useContextMenu() {
  const [contextMenu, setContextMenu] = useState<ContextMenuOptions | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const handleClickOutside = (e: Event) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setContextMenu(null);
      }
    };
    
    if (contextMenu) {
      document.addEventListener('click', handleClickOutside);
      document.addEventListener('contextmenu', handleClickOutside);
    }
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('contextmenu', handleClickOutside);
    };
  }, [contextMenu]);
  
  const showContextMenu = (e: MouseEvent, items: ContextMenuOptions['items']) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      items
    });
  };
  
  const hideContextMenu = () => {
    setContextMenu(null);
  };
  
  return {
    contextMenu,
    showContextMenu,
    hideContextMenu,
    menuRef
  };
}