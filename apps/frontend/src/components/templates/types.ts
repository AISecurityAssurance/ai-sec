import { ReactNode } from 'react';

/**
 * Base props for all analysis template components
 */
export interface BaseAnalysisTemplateProps {
  id: string;
  title?: string;
  children: ReactNode | ((props: { isEditing: boolean }) => ReactNode);
  className?: string;
  onEdit?: () => void;
  onSave?: (data: any) => void;
  onCancel?: () => void;
  onExport?: (format: ExportFormat) => void;
  isStandalone?: boolean;
  defaultEditable?: boolean;
}

/**
 * Export format options
 */
export type ExportFormat = 'pdf' | 'csv' | 'json' | 'png' | 'svg' | 'html' | 'docx' | 'xlsx' | 'txt';

/**
 * Props for the AnalysisContainer component
 */
export interface AnalysisContainerProps extends BaseAnalysisTemplateProps {
  showToolbar?: boolean;
  toolbarPosition?: 'top' | 'bottom';
  exportFormats?: ExportFormat[];
  customActions?: ToolbarAction[];
}

/**
 * Custom toolbar action
 */
export interface ToolbarAction {
  id: string;
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  disabled?: boolean;
}

/**
 * Props for the AnalysisSection component
 */
export interface AnalysisSectionProps extends BaseAnalysisTemplateProps {
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
  level?: 1 | 2 | 3 | 4;
}

/**
 * Props for the AnalysisTable component
 */
export interface AnalysisTableProps extends BaseAnalysisTemplateProps {
  data: any[];
  columns: TableColumn[];
  enableSorting?: boolean;
  enableFiltering?: boolean;
  enablePagination?: boolean;
  pageSize?: number;
}

/**
 * Table column definition
 */
export interface TableColumn {
  id: string;
  header: string;
  accessor: string | ((row: any) => any);
  width?: number | string;
  sortable?: boolean;
  filterable?: boolean;
  editable?: boolean;
  type?: 'text' | 'number' | 'date' | 'boolean' | 'select';
  options?: { value: any; label: string }[];
}

/**
 * Props for the AnalysisDiagram component
 */
export interface AnalysisDiagramProps extends BaseAnalysisTemplateProps {
  type: 'flowchart' | 'graph' | 'chart' | 'custom';
  data: any;
  width?: number | string;
  height?: number | string;
  interactive?: boolean;
}

/**
 * Props for the AnalysisText component
 */
export interface AnalysisTextProps extends BaseAnalysisTemplateProps {
  content: string;
  format?: 'plain' | 'markdown' | 'html';
  maxLength?: number;
  placeholder?: string;
}

/**
 * Edit state management
 */
export interface EditState<T = any> {
  isEditing: boolean;
  originalData: T;
  currentData: T;
  hasChanges: boolean;
}

/**
 * Export options dialog props
 */
export interface ExportOptionsProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: (format: ExportFormat) => void;
  availableFormats: ExportFormat[];
  componentType: 'container' | 'section' | 'table' | 'diagram' | 'text';
}