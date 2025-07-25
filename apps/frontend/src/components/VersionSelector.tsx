import React from 'react';
import { GitBranch, Plus, Check } from 'lucide-react';
import { useVersionStore } from '../stores/versionStore';

export function VersionSelector() {
  const { 
    activeVersionId, 
    versions, 
    switchVersion, 
    createVersion 
  } = useVersionStore();
  
  const activeVersion = versions.find(v => v.id === activeVersionId);
  const [showDropdown, setShowDropdown] = React.useState(false);
  const [showCreateDialog, setShowCreateDialog] = React.useState(false);
  const [newVersionName, setNewVersionName] = React.useState('');
  const [newVersionDescription, setNewVersionDescription] = React.useState('');
  
  const handleCreateVersion = () => {
    if (newVersionName.trim()) {
      const newId = createVersion(
        newVersionName,
        newVersionDescription || 'No description',
        activeVersionId
      );
      switchVersion(newId);
      setShowCreateDialog(false);
      setNewVersionName('');
      setNewVersionDescription('');
      setShowDropdown(false);
    }
  };
  
  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 16px',
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          cursor: 'pointer',
          fontSize: 'var(--font-size-sm)',
          color: 'var(--color-text)'
        }}
      >
        <GitBranch size={16} />
        <span>{activeVersion?.name || 'Select Version'}</span>
        {activeVersion?.isDemo && (
          <span style={{ 
            fontSize: '11px', 
            background: 'var(--color-primary-light)', 
            padding: '2px 6px', 
            borderRadius: '3px' 
          }}>
            DEMO
          </span>
        )}
      </button>
      
      {showDropdown && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            marginTop: '4px',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            minWidth: '250px',
            zIndex: 1000
          }}
        >
          <div style={{ padding: '8px 0' }}>
            {versions.map(version => (
              <button
                key={version.id}
                onClick={() => {
                  switchVersion(version.id);
                  setShowDropdown(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  width: '100%',
                  padding: '8px 16px',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: 'var(--font-size-sm)',
                  color: 'var(--color-text)',
                  textAlign: 'left' as const
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--color-surface-secondary)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <div>
                  <div style={{ fontWeight: 'var(--font-weight-medium)' }}>
                    {version.name}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                    {version.description}
                  </div>
                </div>
                {version.id === activeVersionId && <Check size={16} />}
              </button>
            ))}
          </div>
          
          <div style={{ borderTop: '1px solid var(--color-border)', padding: '8px' }}>
            <button
              onClick={() => setShowCreateDialog(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                width: '100%',
                padding: '8px',
                background: 'transparent',
                border: '1px dashed var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-primary)'
              }}
            >
              <Plus size={16} />
              Create New Version
            </button>
          </div>
        </div>
      )}
      
      {showCreateDialog && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000
          }}
          onClick={() => setShowCreateDialog(false)}
        >
          <div
            style={{
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              minWidth: '400px',
              boxShadow: '0 8px 24px rgba(0,0,0,0.15)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <h3 style={{ margin: '0 0 16px 0' }}>Create New Version</h3>
            
            <div style={{ marginBottom: '16px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '4px', 
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-secondary)'
              }}>
                Version Name
              </label>
              <input
                type="text"
                value={newVersionName}
                onChange={e => setNewVersionName(e.target.value)}
                placeholder="e.g., Analysis v2"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--font-size-sm)'
                }}
              />
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '4px', 
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-secondary)'
              }}>
                Description
              </label>
              <textarea
                value={newVersionDescription}
                onChange={e => setNewVersionDescription(e.target.value)}
                placeholder="Optional description..."
                rows={3}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--font-size-sm)',
                  resize: 'vertical'
                }}
              />
            </div>
            
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowCreateDialog(false)}
                style={{
                  padding: '8px 16px',
                  background: 'transparent',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  fontSize: 'var(--font-size-sm)'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateVersion}
                disabled={!newVersionName.trim()}
                style={{
                  padding: '8px 16px',
                  background: newVersionName.trim() ? 'var(--color-primary)' : 'var(--color-surface-secondary)',
                  color: newVersionName.trim() ? 'white' : 'var(--color-text-secondary)',
                  border: 'none',
                  borderRadius: 'var(--radius-sm)',
                  cursor: newVersionName.trim() ? 'pointer' : 'not-allowed',
                  fontSize: 'var(--font-size-sm)'
                }}
              >
                Create Version
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}