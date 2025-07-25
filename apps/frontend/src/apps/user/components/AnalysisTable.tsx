// Legacy placeholder - redirects to template version
// TODO: Remove all components that depend on this legacy table

import React from 'react';
import { AnalysisTable as TemplateAnalysisTable } from '../../../components/templates/AnalysisTable';
import type { AnalysisTableProps, TableColumn } from './legacyTypes';

export type { TableColumn, TableRow } from './legacyTypes';

// Adapter to convert legacy props to template props
export default function AnalysisTable(props: AnalysisTableProps) {
  const columns = props.columns.map(col => ({
    key: col.key,
    label: col.label,
    sortable: true
  }));

  return (
    <TemplateAnalysisTable
      id={`legacy-${props.title?.toLowerCase().replace(/\s+/g, '-') || 'table'}`}
      title={props.title}
      data={props.data}
      columns={columns}
      sortable={true}
      filterable={true}
      editable={false}
      onRowClick={props.onRowSelect}
      clickableRows={!!props.onRowSelect}
    />
  );
}