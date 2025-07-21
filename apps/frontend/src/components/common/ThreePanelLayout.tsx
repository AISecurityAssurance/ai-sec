import { useState, useRef, useEffect } from 'react';
import type { ReactNode } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { ChevronLeft, ChevronRight, Maximize2, Minimize2 } from 'lucide-react';
import './ThreePanelLayout.css';

interface ThreePanelLayoutProps {
  leftPanel: ReactNode;
  centerPanel: ReactNode;
  rightPanel: ReactNode;
  defaultSizes?: [number, number, number];
  minSizes?: [number, number, number];
  onOpenInNewWindow?: (panel: 'left' | 'center' | 'right') => void;
}

export default function ThreePanelLayout({
  leftPanel,
  centerPanel,
  rightPanel,
  defaultSizes = [20, 50, 30],
  minSizes = [10, 30, 10],
  onOpenInNewWindow
}: ThreePanelLayoutProps) {
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [fullscreenPanel, setFullscreenPanel] = useState<'left' | 'center' | 'right' | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const leftPanelRef = useRef<any>(null);
  const rightPanelRef = useRef<any>(null);

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        setIsFullscreen(false);
        setFullscreenPanel(null);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Handle fullscreen
  const toggleFullscreen = async (panel: 'left' | 'center' | 'right') => {
    if (!document.fullscreenElement) {
      try {
        await containerRef.current?.requestFullscreen();
        setIsFullscreen(true);
        setFullscreenPanel(panel);
      } catch (err) {
        console.error('Error attempting to enable fullscreen:', err);
      }
    } else {
      await document.exitFullscreen();
    }
  };

  const handleLeftCollapse = () => {
    if (leftPanelRef.current) {
      if (leftCollapsed) {
        leftPanelRef.current.expand();
      } else {
        leftPanelRef.current.collapse();
      }
      setLeftCollapsed(!leftCollapsed);
    }
  };

  const handleRightCollapse = () => {
    if (rightPanelRef.current) {
      if (rightCollapsed) {
        rightPanelRef.current.expand();
      } else {
        rightPanelRef.current.collapse();
      }
      setRightCollapsed(!rightCollapsed);
    }
  };

  return (
    <div className="three-panel-layout" ref={containerRef}>
      <PanelGroup direction="horizontal">
        {/* Left Panel */}
        <Panel
          ref={leftPanelRef}
          id="left"
          order={1}
          defaultSize={defaultSizes[0]}
          collapsedSize={0}
          collapsible={true}
          minSize={minSizes[0]}
          maxSize={40}
          onCollapse={() => setLeftCollapsed(true)}
          onExpand={() => setLeftCollapsed(false)}
          style={{ display: isFullscreen && fullscreenPanel !== 'left' ? 'none' : undefined }}
        >
          <div className="panel left-panel">
            <div className="panel-header">
              <a 
                href="/analysis/input-selection" 
                target="_blank"
                rel="noopener noreferrer"
                className="panel-title-link"
              >
                <h3>Selections</h3>
              </a>
              <div className="panel-controls">
                <button
                  className="panel-control-btn"
                  onClick={() => toggleFullscreen('left')}
                  title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
                >
                  {isFullscreen && fullscreenPanel === 'left' ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                </button>
                {!isFullscreen && (
                  <button
                    className="panel-control-btn"
                    onClick={handleLeftCollapse}
                    title={leftCollapsed ? "Expand" : "Collapse"}
                  >
                    {leftCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
                  </button>
                )}
              </div>
            </div>
            <div className="panel-content">
              {leftPanel}
            </div>
          </div>
        </Panel>

        <PanelResizeHandle 
          id="left-resize"
          style={{ display: (isFullscreen || leftCollapsed) ? 'none' : undefined }}
        />

        {/* Center Panel */}
        <Panel
          id="center"
          order={2}
          defaultSize={defaultSizes[1]}
          minSize={minSizes[1]}
          style={{ display: isFullscreen && fullscreenPanel !== 'center' ? 'none' : undefined }}
        >
          <div className="panel center-panel">
            <div className="panel-header">
              <a 
                href="/analysis/canvas" 
                target="_blank"
                rel="noopener noreferrer"
                className="panel-title-link"
              >
                <h3>Analysis Canvas</h3>
              </a>
              <div className="panel-controls">
                <button
                  className="panel-control-btn"
                  onClick={() => toggleFullscreen('center')}
                  title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
                >
                  {isFullscreen && fullscreenPanel === 'center' ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                </button>
              </div>
            </div>
            <div className="panel-content">
              {centerPanel}
            </div>
          </div>
        </Panel>

        <PanelResizeHandle 
          id="right-resize"
          style={{ display: (isFullscreen || rightCollapsed) ? 'none' : undefined }}
        />

        {/* Right Panel */}
        <Panel
          ref={rightPanelRef}
          id="right"
          order={3}
          defaultSize={defaultSizes[2]}
          collapsedSize={0}
          collapsible={true}
          minSize={minSizes[2]}
          maxSize={40}
          onCollapse={() => setRightCollapsed(true)}
          onExpand={() => setRightCollapsed(false)}
          style={{ display: isFullscreen && fullscreenPanel !== 'right' ? 'none' : undefined }}
        >
          <div className="panel right-panel">
            <div className="panel-header">
              <a 
                href="/analysis/agent" 
                target="_blank"
                rel="noopener noreferrer"
                className="panel-title-link"
              >
                <h3>Security Analyst Agent</h3>
              </a>
              <div className="panel-controls">
                <button
                  className="panel-control-btn"
                  onClick={() => toggleFullscreen('right')}
                  title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
                >
                  {isFullscreen && fullscreenPanel === 'right' ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                </button>
                {!isFullscreen && (
                  <button
                    className="panel-control-btn"
                    onClick={handleRightCollapse}
                    title={rightCollapsed ? "Expand" : "Collapse"}
                  >
                    {rightCollapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
                  </button>
                )}
              </div>
            </div>
            <div className="panel-content">
              {rightPanel}
            </div>
          </div>
        </Panel>
      </PanelGroup>

      {/* Collapsed Panel Indicators */}
      {!isFullscreen && (
        <>
          {leftCollapsed && (
            <button 
              className="collapsed-indicator left"
              onClick={handleLeftCollapse}
            >
              <ChevronRight size={20} />
              <span>Input</span>
            </button>
          )}
          
          {rightCollapsed && (
            <button 
              className="collapsed-indicator right"
              onClick={handleRightCollapse}
            >
              <ChevronLeft size={20} />
              <span>Agent</span>
            </button>
          )}
        </>
      )}
    </div>
  );
}