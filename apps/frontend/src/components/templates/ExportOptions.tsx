import React from 'react';
import { ExportOptionsProps, ExportFormat } from './types';
import './ExportOptions.css';

/**
 * Export options dialog component
 * Auto-detects appropriate formats based on component type
 */
export const ExportOptions: React.FC<ExportOptionsProps> = ({
  isOpen,
  onClose,
  onExport,
  availableFormats,
  componentType
}) => {
  if (!isOpen) return null;

  // Get default formats based on component type
  const getDefaultFormats = (): ExportFormat[] => {
    switch (componentType) {
      case 'table':
        return ['csv', 'xlsx', 'json', 'pdf'];
      case 'diagram':
        return ['png', 'svg', 'pdf'];
      case 'text':
        return ['docx', 'pdf', 'html', 'txt'];
      case 'section':
        return ['pdf', 'html', 'docx'];
      case 'container':
      default:
        return ['pdf', 'html', 'json'];
    }
  };

  // Use provided formats or defaults
  const formats = availableFormats.length > 0 ? availableFormats : getDefaultFormats();

  // Format labels
  const formatLabels: Record<ExportFormat, string> = {
    pdf: 'PDF Document',
    csv: 'CSV File',
    json: 'JSON Data',
    png: 'PNG Image',
    svg: 'SVG Vector',
    html: 'HTML Page',
    docx: 'Word Document',
    xlsx: 'Excel Spreadsheet',
    txt: 'Plain Text'
  };

  // Format icons (using Unicode/emoji for simplicity)
  const formatIcons: Record<ExportFormat, string> = {
    pdf: '📄',
    csv: '📊',
    json: '{ }',
    png: '🖼️',
    svg: '🎨',
    html: '🌐',
    docx: '📝',
    xlsx: '📈',
    txt: '📃'
  };

  return (
    <>
      <div className="export-backdrop" onClick={onClose} />
      <div className="export-dialog">
        <div className="export-header">
          <h3>Export Options</h3>
          <button className="export-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="export-content">
          <p className="export-description">
            Choose a format to export this {componentType}:
          </p>
          <div className="export-formats">
            {formats.map(format => (
              <button
                key={format}
                className="export-format-btn"
                onClick={() => onExport(format)}
              >
                <span className="format-icon">{formatIcons[format]}</span>
                <span className="format-label">{formatLabels[format]}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};