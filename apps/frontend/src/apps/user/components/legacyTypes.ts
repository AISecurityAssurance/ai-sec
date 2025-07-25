// Legacy types to support old components that are not being used in the main app
// These components use the old AnalysisTable which has been deleted
// TODO: Remove these components entirely in a future cleanup

export interface TableColumn {
  key: string;
  label: string;
  width?: string;
}

export interface TableRow {
  [key: string]: any;
}

export interface AnalysisTableProps {
  columns: TableColumn[];
  data: TableRow[];
  onRowSelect?: (row: TableRow) => void;
  selectedRowId?: string | null;
  title?: string;
  getRowClassName?: (row: TableRow) => string;
}