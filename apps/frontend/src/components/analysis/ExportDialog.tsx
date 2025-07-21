import { useState } from 'react';
import { X, Download, FileJson, FileText, FileImage } from 'lucide-react';
import './ExportDialog.css';

interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: (format: 'json' | 'pdf' | 'html') => void;
}

export default function ExportDialog({ isOpen, onClose, onExport }: ExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState<'json' | 'pdf' | 'html'>('pdf');

  if (!isOpen) return null;

  const handleExport = () => {
    onExport(selectedFormat);
    onClose();
  };

  return (
    <div className="export-dialog-overlay" onClick={onClose}>
      <div className="export-dialog" onClick={e => e.stopPropagation()}>
        <div className="export-dialog-header">
          <h3>Export Analysis Results</h3>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="export-dialog-content">
          <p className="export-description">
            Choose the format for exporting your analysis results:
          </p>
          
          <div className="export-options">
            <label className={`export-option ${selectedFormat === 'json' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="exportFormat"
                value="json"
                checked={selectedFormat === 'json'}
                onChange={(e) => setSelectedFormat(e.target.value as 'json')}
              />
              <FileJson size={24} />
              <div className="export-option-info">
                <strong>JSON</strong>
                <span>Machine-readable format for integration</span>
              </div>
            </label>
            
            <label className={`export-option ${selectedFormat === 'pdf' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="exportFormat"
                value="pdf"
                checked={selectedFormat === 'pdf'}
                onChange={(e) => setSelectedFormat(e.target.value as 'pdf')}
              />
              <FileText size={24} />
              <div className="export-option-info">
                <strong>PDF</strong>
                <span>Formatted document for sharing</span>
              </div>
            </label>
            
            <label className={`export-option ${selectedFormat === 'html' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="exportFormat"
                value="html"
                checked={selectedFormat === 'html'}
                onChange={(e) => setSelectedFormat(e.target.value as 'html')}
              />
              <FileImage size={24} />
              <div className="export-option-info">
                <strong>HTML</strong>
                <span>Interactive web format</span>
              </div>
            </label>
          </div>
        </div>
        
        <div className="export-dialog-footer">
          <button className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" onClick={handleExport}>
            <Download size={16} />
            Export
          </button>
        </div>
      </div>
    </div>
  );
}