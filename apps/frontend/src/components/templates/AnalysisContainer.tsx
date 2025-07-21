import React, { useState, useCallback, useRef, useEffect } from 'react';
import { AnalysisContainerProps, EditState, ExportFormat } from './types';
import { ExportOptions } from './ExportOptions';
import './AnalysisContainer.css';

/**
 * Base container component that wraps analysis content with a toolbar
 * Provides edit/save/cancel/export functionality
 */
export const AnalysisContainer: React.FC<AnalysisContainerProps> = ({
  id,
  title,
  children,
  className = '',
  onEdit,
  onSave,
  onCancel,
  onExport,
  isStandalone = false,
  defaultEditable = false,
  showToolbar = true,
  toolbarPosition = 'top',
  exportFormats = ['pdf', 'html', 'json'],
  customActions = []
}) => {
  const [editState, setEditState] = useState<EditState>({
    isEditing: defaultEditable,
    originalData: null,
    currentData: null,
    hasChanges: false
  });
  const [showExportOptions, setShowExportOptions] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle edit mode toggle
  const handleEdit = useCallback(() => {
    setEditState(prev => ({
      ...prev,
      isEditing: true,
      originalData: prev.currentData || null
    }));
    onEdit?.();
  }, [onEdit]);

  // Handle save
  const handleSave = useCallback(() => {
    setEditState(prev => ({
      ...prev,
      isEditing: false,
      originalData: prev.currentData,
      hasChanges: false
    }));
    onSave?.(editState.currentData);
  }, [onSave, editState.currentData]);

  // Handle cancel
  const handleCancel = useCallback(() => {
    setEditState(prev => ({
      ...prev,
      isEditing: false,
      currentData: prev.originalData,
      hasChanges: false
    }));
    onCancel?.();
  }, [onCancel]);

  // Handle export
  const handleExport = useCallback((format: ExportFormat) => {
    setShowExportOptions(false);
    onExport?.(format);
  }, [onExport]);

  // Handle open in new window
  const handleOpenInNewWindow = useCallback(() => {
    const baseUrl = window.location.origin;
    const componentPath = `/analysis/standalone/${id}`;
    const url = `${baseUrl}${componentPath}`;
    
    // Open in new tab/window
    window.open(url, '_blank', 'noopener,noreferrer');
  }, [id]);

  // Handle context menu for right-click
  const handleContextMenu = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    handleOpenInNewWindow();
  }, [handleOpenInNewWindow]);

  // Render toolbar
  const renderToolbar = () => {
    if (!showToolbar) return null;

    return (
      <div className="analysis-toolbar">
        <div className="toolbar-left">
          {title && <h3 className="toolbar-title">{title}</h3>}
        </div>
        <div className="toolbar-right">
          {!editState.isEditing ? (
            <>
              <button 
                className="toolbar-btn toolbar-btn-edit"
                onClick={handleEdit}
                title="Edit"
              >
                Edit
              </button>
              <button 
                className="toolbar-btn toolbar-btn-export"
                onClick={() => setShowExportOptions(true)}
                title="Export"
              >
                Export
              </button>
              <button 
                className="toolbar-btn toolbar-btn-open"
                onClick={handleOpenInNewWindow}
                title="Open in new window"
              >
                Open
              </button>
              {customActions.map(action => (
                <button
                  key={action.id}
                  className={`toolbar-btn toolbar-btn-custom toolbar-btn-${action.id}`}
                  onClick={action.onClick}
                  disabled={action.disabled}
                  title={action.label}
                >
                  {action.icon || action.label}
                </button>
              ))}
            </>
          ) : (
            <>
              <button 
                className="toolbar-btn toolbar-btn-save"
                onClick={handleSave}
                title="Save changes"
                disabled={!editState.hasChanges}
              >
                Save
              </button>
              <button 
                className="toolbar-btn toolbar-btn-cancel"
                onClick={handleCancel}
                title="Cancel changes"
              >
                Cancel
              </button>
            </>
          )}
        </div>
      </div>
    );
  };

  // Provide edit state to children via context or props
  const renderChildren = () => {
    // If children is a function, call it with edit state
    if (typeof children === 'function') {
      return children({ isEditing: editState.isEditing });
    }
    
    // Otherwise, clone children with edit state
    return React.Children.map(children, child => {
      if (React.isValidElement(child)) {
        return React.cloneElement(child as React.ReactElement<any>, {
          isEditing: editState.isEditing,
          onDataChange: (data: any) => {
            setEditState(prev => ({
              ...prev,
              currentData: data,
              hasChanges: true
            }));
          }
        });
      }
      return child;
    });
  };

  return (
    <div 
      ref={containerRef}
      className={`analysis-container ${className} ${isStandalone ? 'standalone' : ''} ${editState.isEditing ? 'editing' : ''}`}
      onContextMenu={handleContextMenu}
      data-analysis-id={id}
    >
      {toolbarPosition === 'top' && renderToolbar()}
      
      <div className="analysis-content">
        {renderChildren()}
      </div>
      
      {toolbarPosition === 'bottom' && renderToolbar()}
      
      <ExportOptions
        isOpen={showExportOptions}
        onClose={() => setShowExportOptions(false)}
        onExport={handleExport}
        availableFormats={exportFormats}
        componentType="container"
      />
    </div>
  );
};