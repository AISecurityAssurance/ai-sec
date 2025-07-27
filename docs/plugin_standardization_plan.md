# Plugin Standardization Plan for Testing Arena Integration

## Executive Summary

This document outlines the plan to standardize all security analysis plugins (STPA-Sec, STRIDE, PASTA, STPA-Sec+, etc.) to enable:
1. Integration with the Testing Arena for side-by-side comparison
2. Model-agnostic execution with different LLMs
3. Prompt visibility and modification
4. Consistent plugin architecture across the platform

## Current State Analysis

### Testing Arena Status
- Basic UI structure exists in `/cortex_arena`
- Supports side-by-side comparison of "Production" vs "Experimental" variants
- Currently uses mock data - no real analysis integration
- Has placeholder for plugin management
- Model provider protocol defined but not implemented

### Analysis Plugins Status
- STPA-Sec: Complex implementation with PostgreSQL backend
- STPA-Sec+: Orchestrator plugin with import/synthesis capabilities
- Other plugins: Exist as UI placeholders only
- No standardized plugin interface
- Tightly coupled to platform assumptions

## Architecture Design

### 1. Plugin Interface Standard

```typescript
// Core plugin interface that all analysis plugins must implement
interface IAnalysisPlugin {
  // Metadata
  readonly id: string;
  readonly name: string;
  readonly version: string;
  readonly description: string;
  readonly author: string;
  readonly capabilities: PluginCapabilities;
  
  // Lifecycle
  initialize(context: PluginContext): Promise<void>;
  destroy(): Promise<void>;
  
  // Analysis
  analyze(input: AnalysisInput): Promise<AnalysisOutput>;
  validateInput(input: unknown): ValidationResult;
  
  // Testing Arena Support
  getPrompts(): PromptRegistry;
  getTestCases(): TestCase[];
  getComparisonMetrics(): ComparisonMetric[];
  
  // State Management
  exportState(): PluginState;
  importState(state: PluginState): void;
}

// Plugin capabilities declaration
interface PluginCapabilities {
  supportsStreaming: boolean;
  supportsPartialResults: boolean;
  requiresContext: boolean;
  maxInputSize: number;
  supportedFormats: string[];
  requiredModels: ModelRequirement[];
}

// Context provided by the platform
interface PluginContext {
  modelProvider: IModelProvider;
  storage?: IStorageProvider;
  logger: ILogger;
  config: PluginConfig;
  pluginRegistry?: IPluginRegistry; // For orchestrators like STPA-Sec+
}
```

### 2. Prompt Management System

```typescript
// All prompts must be extractable and modifiable
interface PromptRegistry {
  prompts: Map<string, PromptTemplate>;
  
  getPrompt(id: string): PromptTemplate;
  setPrompt(id: string, template: PromptTemplate): void;
  listPrompts(): PromptInfo[];
  exportPrompts(): PromptExport;
  importPrompts(data: PromptExport): void;
}

interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  variables: PromptVariable[];
  examples?: Example[];
  metadata: {
    tokenEstimate: number;
    lastModified: Date;
    testCoverage: number;
  };
}
```

### 3. Plugin SDK Structure

```
/packages/plugin-sdk/
├── src/
│   ├── core/
│   │   ├── BasePlugin.ts          # Abstract base class
│   │   ├── PluginInterface.ts     # Interface definitions
│   │   └── PluginValidator.ts     # Input/output validation
│   │
│   ├── prompts/
│   │   ├── PromptManager.ts       # Prompt registry implementation
│   │   ├── PromptTemplate.ts      # Template engine
│   │   └── PromptValidator.ts     # Prompt validation
│   │
│   ├── testing/
│   │   ├── TestCaseBuilder.ts     # Test case creation
│   │   ├── MetricsCalculator.ts   # Comparison metrics
│   │   └── ArenaAdapter.ts        # Testing Arena integration
│   │
│   ├── providers/
│   │   ├── ModelProvider.ts       # Model abstraction
│   │   ├── StorageProvider.ts     # Storage abstraction
│   │   └── LogProvider.ts         # Logging abstraction
│   │
│   └── index.ts                   # Public API
│
├── templates/                      # Plugin templates
│   ├── simple-plugin/
│   ├── orchestrator-plugin/
│   └── streaming-plugin/
│
├── docs/
│   ├── getting-started.md
│   ├── api-reference.md
│   └── testing-arena-guide.md
│
└── package.json
```

### 4. Plugin Package Standard

Each plugin must follow this structure:

```
/packages/plugins/[plugin-name]/
├── src/
│   ├── index.ts                   # Plugin entry point
│   ├── plugin.ts                  # Main plugin class
│   ├── prompts/
│   │   ├── index.ts
│   │   └── [prompt-name].yaml     # YAML prompt definitions
│   ├── analyzers/
│   │   └── [analyzer-name].ts     # Analysis logic
│   ├── validators/
│   │   └── [validator-name].ts    # Input validation
│   └── types.ts                   # Plugin-specific types
│
├── test/
│   ├── plugin.test.ts
│   ├── fixtures/
│   └── test-cases.json            # Testing Arena cases
│
├── dist/                          # Built output
│   ├── plugin.js                  # Bundled plugin
│   ├── plugin.d.ts               # Type definitions
│   └── testing-arena.json        # Arena metadata
│
├── plugin.json                    # Plugin manifest
├── package.json
├── tsconfig.json
└── README.md
```

### 5. Plugin Manifest Schema

```json
{
  "id": "stpa-sec",
  "name": "STPA-Sec Security Analysis",
  "version": "1.0.0",
  "description": "System-Theoretic Process Analysis for Security",
  "author": "Security Platform Team",
  "main": "dist/plugin.js",
  "types": "dist/plugin.d.ts",
  
  "capabilities": {
    "supportsStreaming": true,
    "supportsPartialResults": true,
    "requiresContext": true,
    "maxInputSize": 1048576,
    "supportedFormats": ["json", "yaml", "text"],
    "requiredModels": [
      {
        "capability": "completion",
        "minTokens": 4000,
        "preferredTokens": 8000
      }
    ]
  },
  
  "testingArena": {
    "testCases": "test/test-cases.json",
    "comparisonMetrics": [
      "completeness",
      "accuracy",
      "consistency"
    ],
    "visualizations": [
      "risk-matrix",
      "control-flow"
    ]
  },
  
  "dependencies": {
    "@security-platform/plugin-sdk": "^1.0.0"
  }
}
```

## Implementation Plan

### Phase 1: Plugin SDK Development (Week 1)

1. **Day 1-2: Core SDK**
   - Create base plugin interface
   - Implement prompt management system
   - Build model provider abstraction

2. **Day 3-4: Testing Integration**
   - Create Testing Arena adapter
   - Implement comparison metrics
   - Build test case system

3. **Day 5: Documentation & Templates**
   - Write developer guide
   - Create plugin templates
   - Build example plugin

**Deliverable**: Published `@security-platform/plugin-sdk` package

### Phase 2: Plugin Migration (Week 2-3)

1. **STRIDE Plugin (Simple)**
   - Port to new architecture
   - Extract prompts
   - Add test cases
   - Verify in Testing Arena

2. **PASTA Plugin (Medium)**
   - Implement full analysis
   - Add streaming support
   - Create visualizations

3. **STPA-Sec Plugin (Complex)**
   - Refactor for stateless operation
   - Abstract database access
   - Implement partial results

4. **STPA-Sec+ Plugin (Orchestrator)**
   - Adapt for dual-mode operation
   - Handle plugin dependencies
   - Support import-only mode

**Deliverable**: All plugins working in Testing Arena

### Phase 3: Testing Arena Integration (Week 4)

1. **Plugin Loader**
   ```typescript
   class PluginLoader {
     async loadPlugin(path: string): Promise<IAnalysisPlugin>;
     async loadFromRegistry(id: string): Promise<IAnalysisPlugin>;
     validatePlugin(plugin: unknown): ValidationResult;
   }
   ```

2. **Comparison Engine**
   ```typescript
   class ComparisonEngine {
     async runComparison(
       pluginA: IAnalysisPlugin,
       pluginB: IAnalysisPlugin,
       input: AnalysisInput,
       config: ComparisonConfig
     ): Promise<ComparisonResult>;
   }
   ```

3. **Results Visualization**
   - Unified result format
   - Diff visualization
   - Metric dashboards

**Deliverable**: Fully integrated Testing Arena

## Quick Win Implementation

### Minimal STRIDE Plugin (Day 1 Deliverable)

```typescript
// packages/plugins/stride-minimal/src/index.ts
import { BasePlugin, PromptRegistry } from '@security-platform/plugin-sdk';

export class STRIDEPlugin extends BasePlugin {
  id = 'stride-minimal';
  name = 'STRIDE Threat Modeling';
  version = '0.1.0';
  
  prompts = new PromptRegistry([
    {
      id: 'analyze-threats',
      name: 'STRIDE Analysis',
      template: `Analyze the following system for STRIDE threats:
      
System Description:
{{systemDescription}}

Identify threats in these categories:
- Spoofing
- Tampering  
- Repudiation
- Information Disclosure
- Denial of Service
- Elevation of Privilege

Format as JSON with structure:
{
  "threats": [
    {
      "id": "T001",
      "category": "Spoofing",
      "component": "...",
      "description": "...",
      "severity": "high|medium|low"
    }
  ]
}`,
      variables: ['systemDescription']
    }
  ]);
  
  async analyze(input: AnalysisInput): Promise<AnalysisOutput> {
    const prompt = this.prompts.getPrompt('analyze-threats');
    const rendered = prompt.render({
      systemDescription: input.data.system
    });
    
    const response = await this.context.modelProvider.complete({
      prompt: rendered,
      format: 'json'
    });
    
    return {
      success: true,
      results: response.data,
      metadata: {
        promptTokens: response.usage.promptTokens,
        completionTokens: response.usage.completionTokens,
        modelId: this.context.modelProvider.getModelId()
      }
    };
  }
  
  getTestCases(): TestCase[] {
    return [
      {
        id: 'banking-api',
        name: 'Banking API Test',
        input: {
          system: 'RESTful banking API with OAuth2 authentication...'
        },
        expectedMetrics: {
          threatCount: { min: 10, max: 20 },
          severityDistribution: {
            high: { min: 2, max: 5 },
            medium: { min: 3, max: 8 },
            low: { min: 5, max: 10 }
          }
        }
      }
    ];
  }
}
```

### Testing Arena Quick Integration

```typescript
// cortex_arena/src/plugins/PluginRunner.tsx
import { IAnalysisPlugin } from '@security-platform/plugin-sdk';

export function PluginRunner({ 
  plugin: IAnalysisPlugin,
  modelProvider: IModelProvider,
  input: any 
}) {
  const [results, setResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  
  const runAnalysis = async () => {
    setIsRunning(true);
    
    // Initialize plugin with context
    await plugin.initialize({
      modelProvider,
      logger: console,
      config: {}
    });
    
    // Run analysis
    const output = await plugin.analyze(input);
    setResults(output);
    
    setIsRunning(false);
  };
  
  return (
    <div>
      <button onClick={runAnalysis} disabled={isRunning}>
        Run {plugin.name}
      </button>
      {results && <ResultsView results={results} />}
    </div>
  );
}
```

## Success Metrics

1. **Week 1**: Basic STRIDE plugin running in Testing Arena
2. **Week 2**: All plugins converted to new architecture  
3. **Week 3**: Side-by-side comparison working with real models
4. **Week 4**: Full Testing Arena integration with metrics

## Next Steps

1. Review and approve this plan
2. Create plugin-sdk package structure
3. Implement minimal STRIDE plugin
4. Test in cortex_arena
5. Iterate based on feedback

This plan provides a clear path to standardize all plugins while delivering quick wins for the Testing Arena integration.