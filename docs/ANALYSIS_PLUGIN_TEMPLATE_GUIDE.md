# Analysis Plugin Template System Guide

## Overview

The Analysis Plugin Template System provides a standardized way to create analysis components with built-in Edit/Cancel/Save/Export functionality and multi-window support. Each template component can be opened in a new browser window/tab while maintaining state synchronization.

## Core Features

1. **Edit/Cancel/Save Functionality**: Each component has built-in editing capabilities
2. **Export Options**: Smart export format detection based on content type
3. **Multi-Window Support**: Right-click or button to open in new window
4. **State Synchronization**: Real-time sync across all open windows
5. **Hierarchical Editing**: Parent sections make all children editable

## Available Templates

### 1. AnalysisSection
Collapsible sections that can contain other components.

```tsx
import { AnalysisSection } from '@/components/templates';

<AnalysisSection
  id="risk-assessment"
  title="Risk Assessment"
  icon={<AlertTriangle size={16} />}
  level={2}  // h2, h3, h4, etc.
  collapsible
  defaultExpanded={false}
  onSave={(id, data) => console.log('Saved:', data)}
>
  {/* Child components */}
</AnalysisSection>
```

### 2. AnalysisTable
Data tables with sorting, filtering, pagination, and inline editing.

```tsx
import { AnalysisTable } from '@/components/templates';

const columns = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'name', label: 'Name' },
  { key: 'risk', label: 'Risk Level', sortable: true }
];

<AnalysisTable
  id="threat-table"
  title="Threat Analysis"
  data={threatData}
  columns={columns}
  sortable
  filterable
  pageSize={10}
  onSave={(id, data) => console.log('Saved:', data)}
/>
```

### 3. AnalysisText
Editable text content with format support.

```tsx
import { AnalysisText } from '@/components/templates';

<AnalysisText
  id="system-description"
  title="System Description"
  content="Initial content..."
  format="markdown"  // 'plain', 'markdown', 'html'
  maxLength={5000}
  onSave={(id, data) => console.log('Saved:', data)}
/>
```

### 4. AnalysisDiagram
Container for visualizations and diagrams.

```tsx
import { AnalysisDiagram } from '@/components/templates';

<AnalysisDiagram
  id="control-flow"
  title="Control Flow Diagram"
  type="flowchart"  // 'flowchart', 'chart', 'diagram'
  onSave={(id, data) => console.log('Saved:', data)}
>
  {/* Your diagram component */}
</AnalysisDiagram>
```

## Export Formats

Each template automatically detects appropriate export formats:

- **Tables**: CSV, Excel, JSON, PDF
- **Diagrams**: PNG, SVG, PDF
- **Text**: TXT, Word, PDF, HTML
- **Sections**: PDF, HTML, Word

## Creating a Plugin

Here's a complete example of creating an analysis plugin:

```tsx
import { AnalysisSection, AnalysisTable, AnalysisText } from '@/components/templates';

export function MyAnalysisPlugin({ data, onSave }) {
  const handleSave = (id: string, updatedData: any) => {
    // Save to backend
    onSave(id, updatedData);
  };

  return (
    <AnalysisSection
      id="my-analysis"
      title="My Security Analysis"
      onSave={handleSave}
    >
      <AnalysisText
        id="overview"
        title="Overview"
        content={data.overview}
        format="markdown"
        onSave={handleSave}
      />
      
      <AnalysisTable
        id="findings"
        title="Security Findings"
        data={data.findings}
        columns={[
          { key: 'id', label: 'ID', sortable: true },
          { key: 'severity', label: 'Severity', sortable: true },
          { key: 'description', label: 'Description' }
        ]}
        onSave={handleSave}
      />
      
      <AnalysisSection
        id="mitigations"
        title="Mitigations"
        level={3}
        collapsible
        onSave={handleSave}
      >
        {data.mitigations.map(mitigation => (
          <AnalysisText
            key={mitigation.id}
            id={`mitigation-${mitigation.id}`}
            title={mitigation.title}
            content={mitigation.content}
            onSave={handleSave}
          />
        ))}
      </AnalysisSection>
    </AnalysisSection>
  );
}
```

## LLM Integration Instructions

To create a plugin using an LLM, provide this structure:

```
Create an analysis plugin with the following structure:
1. Main section: [Plugin Name]
2. Subsections:
   - Overview (text)
   - Data table with columns: [column1, column2, ...]
   - Nested sections for [categories]
3. Each component should have:
   - Unique ID
   - Title
   - Appropriate data
   - onSave handler
```

## State Management

The template system handles:
- Local edit state (draft changes)
- Cancel/revert functionality
- Multi-window synchronization via BroadcastChannel
- Prop updates from parent components

## Styling

Each template has its own CSS file with customizable CSS variables:
- `--template-spacing`
- `--template-border-color`
- `--template-header-height`
- etc.

## Best Practices

1. **Unique IDs**: Always provide unique IDs for each component
2. **Hierarchical Structure**: Use AnalysisSection for grouping related content
3. **Save Handlers**: Implement proper save handlers for data persistence
4. **Export Formats**: Let the system auto-detect formats unless specific needs
5. **Edit Scope**: Consider if editing should be at component or section level

## Advanced Features

### Custom Export Handlers
```tsx
<AnalysisTable
  onExport={(format, data) => {
    // Custom export logic
    if (format === 'csv') {
      return customCSVExport(data);
    }
  }}
/>
```

### Conditional Editing
```tsx
<AnalysisText
  editable={userHasPermission}
  onSave={handleSave}
/>
```

### Multi-Window Sync
```tsx
// Automatic sync is built-in
// Access sync state with useSyncState hook
const [syncedData, setSyncedData] = useSyncState('my-data-key', initialData);
```

## TypeScript Types

All templates are fully typed. Import types:

```tsx
import type { 
  AnalysisTableProps,
  TableColumn,
  ExportFormat 
} from '@/components/templates';
```

## Example: STPA-Sec Plugin

See `CollapsibleAnalysisContentWithTemplates.tsx` for a complete implementation using real STPA-Sec data with all template types.