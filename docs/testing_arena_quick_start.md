# Testing Arena Quick Start Guide

## For Immediate Integration

This guide helps you quickly integrate analysis plugins into the Testing Arena while we build the full plugin SDK.

## Minimal Plugin Interface (Use Today)

```typescript
// Add to cortex_arena/src/types/plugin.ts
export interface ITestablePlugin {
  id: string;
  name: string;
  
  // Simple analysis function
  analyze(
    input: string,
    modelProvider: {
      complete: (prompt: string) => Promise<{ text: string; usage: any }>
    }
  ): Promise<{
    success: boolean;
    results: any;
    error?: string;
  }>;
  
  // Get the prompt template
  getPrompt(): string;
  
  // Get test cases
  getTestCase(): {
    input: string;
    expectedResultCount?: number;
  };
}
```

## Quick STRIDE Plugin Example

```typescript
// cortex_arena/src/plugins/stride/index.ts
export class STRIDEPlugin implements ITestablePlugin {
  id = 'stride';
  name = 'STRIDE Analysis';
  
  getPrompt(): string {
    return `Analyze this system for STRIDE threats:

{{INPUT}}

Return a JSON array of threats with: id, category (S/T/R/I/D/E), description, severity`;
  }
  
  async analyze(input: string, modelProvider: any) {
    const prompt = this.getPrompt().replace('{{INPUT}}', input);
    
    try {
      const response = await modelProvider.complete(prompt);
      const threats = JSON.parse(response.text);
      
      return {
        success: true,
        results: {
          threats,
          summary: {
            total: threats.length,
            high: threats.filter(t => t.severity === 'high').length,
            medium: threats.filter(t => t.severity === 'medium').length,
            low: threats.filter(t => t.severity === 'low').length
          }
        }
      };
    } catch (error) {
      return {
        success: false,
        results: null,
        error: error.message
      };
    }
  }
  
  getTestCase() {
    return {
      input: "Banking API with OAuth2 authentication, handles financial transactions",
      expectedResultCount: 10
    };
  }
}
```

## Integration in Testing Arena

```typescript
// cortex_arena/src/components/PluginTestColumn.tsx
import { STRIDEPlugin } from '../plugins/stride';

export function PluginTestColumn({ 
  variant,
  modelConfig 
}: { 
  variant: 'production' | 'experimental',
  modelConfig: ModelConfig 
}) {
  const [plugin] = useState(new STRIDEPlugin());
  const [results, setResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  
  // Simple model provider wrapper
  const modelProvider = {
    complete: async (prompt: string) => {
      // Use your existing model integration
      const response = await callModel(modelConfig, prompt);
      return {
        text: response,
        usage: { tokens: response.length / 4 } // Rough estimate
      };
    }
  };
  
  const runTest = async () => {
    setIsRunning(true);
    const testCase = plugin.getTestCase();
    const result = await plugin.analyze(testCase.input, modelProvider);
    setResults(result);
    setIsRunning(false);
  };
  
  return (
    <div className="test-column">
      <h3>{variant} - {plugin.name}</h3>
      <div className="model-info">
        Model: {modelConfig.provider} / {modelConfig.model}
      </div>
      
      <button onClick={runTest} disabled={isRunning}>
        Run Analysis
      </button>
      
      {results && (
        <div className="results">
          {results.success ? (
            <>
              <div className="summary">
                Total Threats: {results.results.summary.total}
                High: {results.results.summary.high}
                Medium: {results.results.summary.medium}
                Low: {results.results.summary.low}
              </div>
              <div className="threats">
                {results.results.threats.map(threat => (
                  <div key={threat.id} className={`threat ${threat.severity}`}>
                    <strong>{threat.category}</strong>: {threat.description}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="error">Error: {results.error}</div>
          )}
        </div>
      )}
      
      <details>
        <summary>View Prompt</summary>
        <pre>{plugin.getPrompt()}</pre>
      </details>
    </div>
  );
}
```

## Side-by-Side Comparison

```typescript
// cortex_arena/src/components/ComparisonView.tsx
export function ComparisonView() {
  const productionModel = { provider: 'anthropic', model: 'claude-3-opus' };
  const experimentalModel = { provider: 'openai', model: 'gpt-4' };
  
  return (
    <div className="comparison-view">
      <PluginTestColumn 
        variant="production" 
        modelConfig={productionModel} 
      />
      <PluginTestColumn 
        variant="experimental" 
        modelConfig={experimentalModel} 
      />
    </div>
  );
}
```

## Adding More Plugins

### 1. PASTA Plugin (Process for Attack Simulation)
```typescript
export class PASTAPlugin implements ITestablePlugin {
  id = 'pasta';
  name = 'PASTA Analysis';
  
  getPrompt(): string {
    return `Perform PASTA analysis with these steps:
1. Define business objectives
2. Define technical scope  
3. Decompose application
4. Analyze threats
5. Identify vulnerabilities
6. Model attacks
7. Analyze risk/impact

System: {{INPUT}}

Return JSON with all 7 stages.`;
  }
  // ... rest of implementation
}
```

### 2. Simple STPA-Sec Wrapper
```typescript
export class STPASecPlugin implements ITestablePlugin {
  id = 'stpa-sec';
  name = 'STPA-Sec Analysis';
  
  getPrompt(): string {
    return `Perform STPA-Sec analysis:
1. Identify losses
2. Identify hazards
3. Model control structure
4. Identify unsafe control actions
5. Identify loss scenarios

System: {{INPUT}}

Return structured JSON results.`;
  }
  // ... rest of implementation
}
```

## Model Provider Integration

```typescript
// cortex_arena/src/services/modelProvider.ts
import { Anthropic } from '@anthropic-ai/sdk';
import OpenAI from 'openai';

export async function callModel(config: ModelConfig, prompt: string) {
  switch (config.provider) {
    case 'anthropic':
      const anthropic = new Anthropic({ apiKey: config.apiKey });
      const response = await anthropic.messages.create({
        model: config.model,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: config.maxTokens || 4000
      });
      return response.content[0].text;
      
    case 'openai':
      const openai = new OpenAI({ apiKey: config.apiKey });
      const response = await openai.chat.completions.create({
        model: config.model,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: config.maxTokens || 4000
      });
      return response.choices[0].message.content;
      
    default:
      throw new Error(`Unknown provider: ${config.provider}`);
  }
}
```

## Metrics Comparison

```typescript
// cortex_arena/src/components/MetricsComparison.tsx
export function MetricsComparison({ resultA, resultB }) {
  const calculateDifference = (a: number, b: number) => {
    return ((b - a) / a * 100).toFixed(1);
  };
  
  return (
    <div className="metrics-comparison">
      <h3>Comparison Metrics</h3>
      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Production</th>
            <th>Experimental</th>
            <th>Difference</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Total Threats</td>
            <td>{resultA.summary.total}</td>
            <td>{resultB.summary.total}</td>
            <td>{calculateDifference(resultA.summary.total, resultB.summary.total)}%</td>
          </tr>
          <tr>
            <td>High Severity</td>
            <td>{resultA.summary.high}</td>
            <td>{resultB.summary.high}</td>
            <td>{calculateDifference(resultA.summary.high, resultB.summary.high)}%</td>
          </tr>
          {/* Add more metrics */}
        </tbody>
      </table>
    </div>
  );
}
```

## Next Steps for Your Colleague

1. **Today**: Copy the minimal plugin interface and STRIDE example
2. **Tomorrow**: Integrate into existing Testing Arena UI
3. **This Week**: Add 2-3 more plugins using the same pattern
4. **Next Week**: We'll provide the full plugin SDK to replace this

## Questions Your Colleague Might Have

**Q: How do I handle streaming responses?**
A: For now, use complete responses. Streaming support coming in full SDK.

**Q: How do I modify prompts in real-time?**
A: Add a prompt editor component that updates the plugin's prompt before running.

**Q: How do I save/load test results?**
A: Store results in local state for now. Persistence coming with full platform integration.

**Q: Can I test STPA-Sec+ this way?**
A: STPA-Sec+ is complex. Start with simpler plugins. We'll provide STPA-Sec+ wrapper next week.

## Contact

- For immediate help: [Your contact]
- SDK updates: Check `/docs/plugin_standardization_plan.md`
- Example code: `/packages/plugins/examples/`

This should get the Testing Arena running with real plugins within a day!