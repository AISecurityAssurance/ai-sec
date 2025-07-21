# Analysis Template System

A flexible and reusable template system for analysis components with built-in editing, export, and multi-window synchronization capabilities.

## Overview

The Analysis Template System provides a set of components that wrap different types of analysis content with consistent functionality:

- **Edit/Cancel/Save toolbar** - Edit content inline with save/cancel functionality
- **Export capabilities** - Auto-detected export formats based on content type
- **Multi-window sync** - Changes synchronize across browser windows/tabs
- **Standalone mode** - Components can be opened in new windows
- **Hierarchical editing** - Edit mode propagates to all child components

## Components

### AnalysisContainer
Base wrapper component that provides toolbar functionality for all templates.

```tsx
<AnalysisContainer
  id="unique-id"
  title="Container Title"
  onSave={(data) => console.log('Saved:', data)}
  onExport={(format) => console.log('Export:', format)}
  exportFormats={['pdf', 'html', 'json']}
>
  {/* Your content here */}
</AnalysisContainer>
```

### AnalysisSection
Collapsible sections with nested content support.

```tsx
<AnalysisSection
  id="section-1"
  title="Risk Assessment"
  level={1}
  collapsible={true}
  defaultCollapsed={false}
>
  {/* Nested content and sections */}
</AnalysisSection>
```

### AnalysisTable
Data tables with sorting, filtering, pagination, and inline editing.

```tsx
<AnalysisTable
  id="data-table"
  title="Risk Matrix"
  data={tableData}
  columns={[
    { id: 'name', header: 'Name', accessor: 'name', editable: true },
    { id: 'risk', header: 'Risk', accessor: 'risk', type: 'select' }
  ]}
  enableSorting={true}
  enableFiltering={true}
  enablePagination={true}
/>
```

### AnalysisText
Editable text content with support for plain text, markdown, and HTML.

```tsx
<AnalysisText
  id="summary"
  title="Executive Summary"
  content="Initial content..."
  format="plain"
  maxLength={1000}
  placeholder="Enter summary..."
/>
```

### AnalysisDiagram
Container for diagrams, charts, and visualizations.

```tsx
<AnalysisDiagram
  id="architecture"
  title="System Architecture"
  type="flowchart"
  data={diagramData}
  width="100%"
  height={400}
  interactive={true}
>
  {/* Custom diagram content */}
</AnalysisDiagram>
```

## Features

### 1. Edit Mode
- Click Edit button to make content editable
- Changes are tracked with visual indicators
- Save commits changes, Cancel reverts to original

### 2. Export Formats
Auto-detected based on content type:
- **Tables**: CSV, Excel, JSON, PDF
- **Diagrams**: PNG, SVG, PDF
- **Text**: TXT, Word, PDF, HTML
- **Sections**: PDF, HTML, Word

### 3. Multi-Window Synchronization
- Uses BroadcastChannel API for real-time sync
- Edit states synchronize across windows
- Changes appear immediately in all open instances

### 4. Standalone Mode
- Right-click or use Open button to open in new window
- Components work independently
- Full functionality retained in standalone mode

### 5. Hierarchical Editing
- When a section enters edit mode, all children become editable
- Useful for editing complex nested structures
- Edit state propagates down the component tree

## Usage Example

```tsx
import { AnalysisSection, AnalysisTable, AnalysisText } from './components/templates';

function MyAnalysis() {
  return (
    <AnalysisSection
      id="main-analysis"
      title="Security Analysis"
      level={1}
    >
      <AnalysisText
        id="overview"
        title="Overview"
        content="System security analysis..."
      />
      
      <AnalysisTable
        id="vulnerabilities"
        title="Vulnerability Matrix"
        data={vulnData}
        columns={columns}
      />
    </AnalysisSection>
  );
}
```

## Customization

### Custom Export Handlers
```tsx
<AnalysisContainer
  onExport={(format) => {
    switch(format) {
      case 'custom':
        handleCustomExport();
        break;
      default:
        handleDefaultExport(format);
    }
  }}
  exportFormats={['pdf', 'custom']}
/>
```

### Custom Toolbar Actions
```tsx
<AnalysisContainer
  customActions={[
    {
      id: 'refresh',
      label: 'Refresh',
      onClick: () => refreshData()
    }
  ]}
/>
```

## State Management

The template system uses custom hooks for state synchronization:

- `useSyncState` - Synchronizes state across windows
- `useSyncEditState` - Manages edit states with sync

## Styling

Each component has its own CSS file with customizable classes:
- `.analysis-container` - Base container styles
- `.analysis-toolbar` - Toolbar styles
- `.editing` - Edit mode styles

## Browser Support

- Modern browsers with BroadcastChannel API support
- Fallback to local state for older browsers
- Responsive design for mobile devices