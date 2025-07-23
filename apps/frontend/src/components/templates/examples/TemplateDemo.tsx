import React from 'react';
import { AnalysisSection, AnalysisTable, AnalysisText, AnalysisDiagram, TableColumn } from '../index';

/**
 * Demo component showcasing the template system
 */
export const TemplateDemo: React.FC = () => {
  // Sample data for the table
  const sampleData = [
    { id: 1, name: 'System A', risk: 'High', status: 'Active', score: 85 },
    { id: 2, name: 'System B', risk: 'Medium', status: 'Inactive', score: 62 },
    { id: 3, name: 'System C', risk: 'Low', status: 'Active', score: 94 },
    { id: 4, name: 'System D', risk: 'High', status: 'Pending', score: 71 },
    { id: 5, name: 'System E', risk: 'Medium', status: 'Active', score: 88 }
  ];

  // Table columns configuration
  const columns: TableColumn[] = [
    { 
      id: 'name', 
      header: 'System Name', 
      accessor: 'name',
      editable: true,
      width: '30%'
    },
    { 
      id: 'risk', 
      header: 'Risk Level', 
      accessor: 'risk',
      editable: true,
      type: 'select',
      options: [
        { value: 'Low', label: 'Low' },
        { value: 'Medium', label: 'Medium' },
        { value: 'High', label: 'High' }
      ]
    },
    { 
      id: 'status', 
      header: 'Status', 
      accessor: 'status',
      editable: true,
      type: 'select',
      options: [
        { value: 'Active', label: 'Active' },
        { value: 'Inactive', label: 'Inactive' },
        { value: 'Pending', label: 'Pending' }
      ]
    },
    { 
      id: 'score', 
      header: 'Score', 
      accessor: 'score',
      editable: true,
      type: 'number'
    }
  ];

  const handleTableSave = (id: string, data: any) => {
    console.log('Table data saved:', id, data);
  };

  const handleSectionSave = () => {
    console.log('Section saved');
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Analysis Template System Demo</h1>
      
      <AnalysisSection
        id="main-section"
        title="Risk Assessment Overview"
        level={1}
        collapsible={true}
        defaultCollapsed={false}
        onSave={handleSectionSave}
      >
        <p style={{ marginBottom: '16px' }}>
          This section demonstrates the collapsible section template with nested content.
          Click the Edit button in the toolbar to make all content in this section editable.
        </p>

        <AnalysisSection
          id="sub-section-1"
          title="System Analysis"
          level={2}
          collapsible={true}
        >
          <p>
            When the parent section is in edit mode, all nested sections become editable.
            This allows for comprehensive editing of hierarchical content.
          </p>
        </AnalysisSection>

        <AnalysisSection
          id="sub-section-2"
          title="Risk Matrix"
          level={2}
          collapsible={true}
        >
          <AnalysisTable
            id="risk-table"
            title="System Risk Assessment"
            data={sampleData}
            columns={columns}
            enableSorting={true}
            enableFiltering={true}
            enablePagination={true}
            pageSize={10}
            onSave={handleTableSave}
          />
        </AnalysisSection>

        <AnalysisSection
          id="sub-section-3"
          title="Analysis Summary"
          level={2}
          collapsible={true}
        >
          <AnalysisText
            id="summary-text"
            title="Executive Summary"
            content="This is an example of the AnalysisText component. It supports plain text, markdown, and HTML formats. When in edit mode, you can modify this content directly."
            format="plain"
            maxLength={1000}
          />
        </AnalysisSection>

        <AnalysisSection
          id="sub-section-4"
          title="System Architecture"
          level={2}
          collapsible={true}
        >
          <AnalysisDiagram
            id="architecture-diagram"
            title="System Architecture Diagram"
            type="flowchart"
          >
            <div style={{ height: 400, border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <p>Diagram content goes here</p>
            </div>
          </AnalysisDiagram>
        </AnalysisSection>
      </AnalysisSection>

      <div style={{ marginTop: '40px' }}>
        <h2>Features Demonstrated:</h2>
        <ul>
          <li>✓ Edit/Cancel/Save/Export buttons in toolbar</li>
          <li>✓ Collapsible sections with nested content</li>
          <li>✓ Editable table with sorting, filtering, and pagination</li>
          <li>✓ Right-click to open in new window (or use Open button)</li>
          <li>✓ Auto-detected export formats based on content type</li>
          <li>✓ State synchronization across multiple windows</li>
          <li>✓ When editing a section, all children become editable</li>
        </ul>
      </div>
    </div>
  );
};