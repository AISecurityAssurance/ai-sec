# PromptSaver Integration Guide

## Overview
The PromptSaver system allows saving all LLM prompts and responses during analysis for debugging and auditing purposes.

## Implementation Steps

### 1. CLI Integration (cli.py)

Add the `--save-prompts` flag:

```python
# In cli.py argument parser
parser.add_argument(
    '--save-prompts',
    action='store_true',
    help='Save all LLM prompts and responses to output_dir/prompts/'
)

# In analyze() method, after creating output_dir:
if args.save_prompts:
    from core.utils.prompt_saver import init_prompt_saver
    init_prompt_saver(output_dir, enabled=True)
```

### 2. Step 1 Base Agent Integration

Modify `BaseStep1Agent.query_llm()` method:

```python
# In core/agents/step1_agents/base_step1.py
async def query_llm(self, system_prompt: str, prompt: str, temperature: float = 0.7) -> str:
    """Query the LLM with the given prompts."""
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
        
    messages.append({"role": "user", "content": prompt})
    
    # Get model client and generate response
    try:
        client = get_model_client()
        response = await client.generate(messages, temperature=temperature)
        
        # Save prompt and response if enabled
        from core.utils.prompt_saver import get_prompt_saver
        prompt_saver = get_prompt_saver()
        if prompt_saver:
            await prompt_saver.save_prompt_response(
                agent_name=self.get_agent_type(),
                cognitive_style=self.cognitive_style.value,
                prompt=prompt,
                response=response.content,
                step=1,
                metadata={
                    'system_prompt': system_prompt,
                    'temperature': temperature,
                    'analysis_id': self.analysis_id
                }
            )
        
        return response.content
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {str(e)}") from e
```

### 3. Step 2 Base Agent Integration

Modify `BaseStep2Agent.query_llm_with_retry()`:

```python
# In core/agents/step2_agents/base_step2.py
async def query_llm_with_retry(self, messages: List[Dict[str, str]], 
                               max_retries: int = 3, 
                               temperature: float = 0.7,
                               max_tokens: int = 4000) -> str:
    """Query LLM with retry logic for better JSON parsing."""
    from core.utils.json_parser import parse_llm_json
    from core.utils.prompt_saver import get_prompt_saver
    
    prompt = messages[-1]["content"] if messages else ""
    prompt_saver = get_prompt_saver()
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            # Make LLM call
            response = await self.model_provider.generate(
                messages, 
                temperature=temperature, 
                max_tokens=max_tokens
            )
            response_text = response.content
            
            # Save raw response for debugging
            self.save_raw_response(prompt, response_text, attempt)
            
            # Save to prompt saver if enabled
            if prompt_saver:
                await prompt_saver.save_prompt_response(
                    agent_name=self.__class__.__name__,
                    cognitive_style=self.cognitive_style.value,
                    prompt=prompt,
                    response=response_text,
                    step=2,
                    metadata={
                        'attempt': attempt,
                        'temperature': temperature,
                        'max_tokens': max_tokens,
                        'messages_count': len(messages)
                    }
                )
            
            # Try to parse JSON...
            # (rest of the method remains the same)
```

### 4. Step 2 Coordinator Integration

Pass the output directory and ensure prompt saver is initialized:

```python
# In cli.py _run_step2_analysis():
# After creating output_dir
if args.save_prompts:
    from core.utils.prompt_saver import init_prompt_saver
    init_prompt_saver(output_dir, enabled=True)

# Create Step 2 coordinator with output directory
coordinator = Step2Coordinator(model_provider, db_conn, output_dir=output_dir)
```

### 5. Create Index at End of Analysis

In both Step 1 and Step 2 completion:

```python
# After analysis completes successfully
from core.utils.prompt_saver import get_prompt_saver
prompt_saver = get_prompt_saver()
if prompt_saver:
    index_file = prompt_saver.create_index()
    if index_file:
        self.console.print(f"[dim]Prompt index created: {index_file}[/dim]")
```

## Output Structure

When `--save-prompts` is enabled, the following structure is created:

```
analyses/sd-wan/20250801_120000/
├── analysis-config.yaml
├── analysis-results.json
├── analysis-report.md
└── prompts/
    ├── step1_loss_identification_intuitive_001_prompt.txt
    ├── step1_loss_identification_intuitive_001_response.txt
    ├── step1_loss_identification_intuitive_001_metadata.json
    ├── step1_hazard_identification_systematic_001_prompt.txt
    ├── step1_hazard_identification_systematic_001_response.txt
    ├── step1_hazard_identification_systematic_001_metadata.json
    ├── step2_control_structure_analyst_balanced_001_prompt.txt
    ├── step2_control_structure_analyst_balanced_001_response.txt
    ├── step2_control_structure_analyst_balanced_001_metadata.json
    └── index.json
```

## Benefits

1. **Debugging**: See exact prompts and responses for troubleshooting
2. **Auditing**: Track what the LLM was asked and how it responded
3. **Prompt Engineering**: Analyze prompts to improve them
4. **Reproducibility**: Understand how results were generated
5. **No Performance Impact**: Only saves when explicitly enabled

## Usage

```bash
# Run analysis with prompt saving
./ai-sec analyze --config configs/standard-analysis.yaml --save-prompts

# The prompts will be saved in the output directory
# e.g., analyses/sd-wan/20250801_120000/prompts/
```