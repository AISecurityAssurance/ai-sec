import { useState } from 'react';
import { Plus, Edit2, Copy, Trash2, Save, FileText } from 'lucide-react';
import SimpleLayout from '../../components/common/SimpleLayout';
import { usePromptStore, getTemplatesByType } from '../../stores/promptStore';
import './PromptsApp.css';

export default function PromptsApp() {
  const { templates, settings, activeTemplateId, setActiveTemplate, updateTemplate } = usePromptStore();
  const [selectedAnalysisType, setSelectedAnalysisType] = useState<string>('all');
  const [editingTemplate, setEditingTemplate] = useState<string | null>(null);
  const [templateContent, setTemplateContent] = useState<string>('');

  const analysisTypes = [
    'all',
    'stpa-sec',
    'stride',
    'pasta',
    'dread',
    'maestro',
    'linddun',
    'hazop',
    'octave'
  ];

  const filteredTemplates = selectedAnalysisType === 'all' 
    ? templates 
    : templates.filter(t => t.analysisType === selectedAnalysisType);

  const handleEditTemplate = (template: any) => {
    setEditingTemplate(template.id);
    setTemplateContent(template.template);
  };

  const handleSaveTemplate = () => {
    if (editingTemplate) {
      updateTemplate(editingTemplate, { template: templateContent });
      setEditingTemplate(null);
      setTemplateContent('');
    }
  };

  return (
    <SimpleLayout>
      <div className="prompts-page">
        <div className="prompts-page-header">
          <h1>Prompt Settings</h1>
          <button className="add-template-button">
            <Plus size={20} />
            New Template
          </button>
        </div>
        <div className="prompts-container">
        <div className="prompts-sidebar">
          <div className="analysis-type-filter">
            <h3>Analysis Type</h3>
            {analysisTypes.map(type => (
              <button
                key={type}
                className={`filter-button ${selectedAnalysisType === type ? 'active' : ''}`}
                onClick={() => setSelectedAnalysisType(type)}
              >
                {type === 'all' ? 'All Templates' : type.toUpperCase()}
              </button>
            ))}
          </div>

          <div className="prompt-settings-section">
            <h3>Model Settings</h3>
            <div className="setting-item">
              <label>Temperature</label>
              <input
                type="number"
                value={settings.temperature}
                onChange={(e) => usePromptStore.getState().updateSettings({ temperature: parseFloat(e.target.value) })}
                min="0"
                max="1"
                step="0.1"
              />
            </div>
            <div className="setting-item">
              <label>Max Tokens</label>
              <input
                type="number"
                value={settings.maxTokens}
                onChange={(e) => usePromptStore.getState().updateSettings({ maxTokens: parseInt(e.target.value) })}
                min="100"
                max="8192"
                step="100"
              />
            </div>
          </div>
        </div>

        <div className="prompts-content">
          <div className="templates-grid">
            {filteredTemplates.map(template => (
              <div
                key={template.id}
                className={`template-card ${activeTemplateId === template.id ? 'active' : ''} ${editingTemplate === template.id ? 'editing' : ''}`}
              >
                <div className="template-header">
                  <div className="template-info">
                    <h3>{template.name}</h3>
                    <p>{template.description}</p>
                    <div className="template-meta">
                      <span className="analysis-type-badge">{template.analysisType}</span>
                      <span className="version">v{template.version}</span>
                    </div>
                  </div>
                  <div className="template-actions">
                    <button
                      onClick={() => setActiveTemplate(template.id)}
                      className="icon-button"
                      title="Set as active"
                    >
                      <FileText size={16} />
                    </button>
                    <button
                      onClick={() => handleEditTemplate(template)}
                      className="icon-button"
                      title="Edit"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() => usePromptStore.getState().duplicateTemplate(template.id, `${template.name} (Copy)`)}
                      className="icon-button"
                      title="Duplicate"
                    >
                      <Copy size={16} />
                    </button>
                    <button
                      onClick={() => usePromptStore.getState().deleteTemplate(template.id)}
                      className="icon-button danger"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>

                {editingTemplate === template.id ? (
                  <div className="template-editor">
                    <textarea
                      value={templateContent}
                      onChange={(e) => setTemplateContent(e.target.value)}
                      className="template-textarea"
                      rows={10}
                    />
                    <div className="editor-actions">
                      <button onClick={handleSaveTemplate} className="save-button">
                        <Save size={16} />
                        Save
                      </button>
                      <button
                        onClick={() => {
                          setEditingTemplate(null);
                          setTemplateContent('');
                        }}
                        className="cancel-button"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="template-preview">
                    <pre>{template.template}</pre>
                    <div className="template-variables">
                      <strong>Variables:</strong> {template.variables.join(', ')}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
      </div>
    </SimpleLayout>
  );
}