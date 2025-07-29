# Model Configuration Guide

This guide explains how to configure different AI models for STPA-Sec Step 1 analysis.

## Overview

The system supports multiple model providers and can be configured through:
1. Environment variables (highest priority)
2. Configuration files (`.yaml` files)
3. Default settings

## Supported Providers

- **OpenAI** (includes Azure OpenAI)
- **Anthropic** (Claude)
- **Groq**
- **Google Gemini**
- **Ollama** (local models)

## Configuration Priority

The system checks for models in this order:
1. **Azure OpenAI** (if Azure environment variables are set)
2. **Config file settings** (if specified in the YAML)
3. **Standard environment variables** (e.g., OPENAI_API_KEY)
4. **Default settings**

## Azure OpenAI Configuration

Azure OpenAI takes priority when these environment variables are set:

```bash
export AZURE_OPENAI_API_KEY="your-azure-api-key"
export AZURE_OPENAI_API_BASE="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_MODEL="your-deployment-name"
```

When these are set, the system automatically:
- Uses Azure OpenAI endpoints
- Displays "Using Azure OpenAI" in the console
- Shows the Azure model in the analysis report

### Using Azure OpenAI with the CLI

The `ai-sec` script automatically passes Azure environment variables to the Docker container:

```bash
# Set Azure credentials
export AZURE_OPENAI_API_KEY="your-azure-api-key"
export AZURE_OPENAI_API_BASE="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_MODEL="your-deployment-name"

# Run analysis
./ai-sec analyze --config configs/azure-gpt4-turbo-standard.yaml
```

### Example Azure Config File

```yaml
# azure-gpt4-turbo-standard.yaml
analysis:
  name: "Analysis with Azure OpenAI"
  output_dir: "./analyses/azure-analysis/"

model:
  provider: "openai"  # Azure uses the OpenAI provider
  # No API key needed - uses Azure env vars

execution:
  mode: "standard"
```

## Standard OpenAI Configuration

For standard OpenAI (not Azure):

```bash
export OPENAI_API_KEY="sk-..."
```

### Example OpenAI Config File

```yaml
# gpt4-turbo-standard.yaml
analysis:
  name: "Analysis with OpenAI"
  output_dir: "./analyses/openai-analysis/"

model:
  provider: "openai"
  name: "gpt-4-turbo-preview"
  api_key_env: "OPENAI_API_KEY"

execution:
  mode: "standard"
```

## Ollama (Local Models) Configuration

For local models using Ollama:

```bash
# Start Ollama server first
ollama serve

# Pull a model
ollama pull llama2
```

### Example Ollama Config File

```yaml
# ollama-llama2-standard.yaml
analysis:
  name: "Analysis with Local Llama 2"
  output_dir: "./analyses/ollama-analysis/"

model:
  provider: "ollama"
  name: "llama2"
  api_endpoint: "http://localhost:11434"  # Default Ollama endpoint

execution:
  mode: "standard"
```

## How Configuration Works

### 1. Environment Variables Processing

The system checks environment variables in `settings.py`:

```python
# Azure OpenAI (highest priority)
if AZURE_OPENAI_API_KEY and AZURE_OPENAI_API_BASE:
    # Use Azure configuration
    
# Standard providers
elif OPENAI_API_KEY:
    # Use standard OpenAI
elif ANTHROPIC_API_KEY:
    # Use Anthropic
# ... etc
```

### 2. CLI Configuration Override

The CLI (`cli.py`) can override settings based on the config file:

```python
def _setup_api_keys(self, config: dict):
    # Check for Azure first
    if os.getenv('AZURE_OPENAI_API_KEY'):
        # Configure Azure
    # Then check config file
    elif config['model']['api_key_env']:
        # Use specified environment variable
```

### 3. Model Information Display

The analysis report shows which model was used:

```
Model Information:
  • Provider: openai
  • Model: gpt-4-turbo
  • Execution Mode: standard
```

## Adding New Model Providers

To add a new provider:

1. Add to `ModelProvider` enum in `settings.py`
2. Create client class in `llm_client.py`
3. Add environment variable loading in `settings.py`
4. Update CLI configuration in `cli.py`

## Troubleshooting

### Azure OpenAI Not Detected
- Ensure all three Azure environment variables are set
- Check that `AZURE_OPENAI_API_BASE` includes the trailing slash
- Verify the deployment name matches your Azure resource

### Model Not Found
- Check environment variable names match exactly
- Ensure API keys are valid
- For Ollama, verify the server is running

### Wrong Model Used
- Azure takes priority over standard OpenAI
- Check environment variables aren't conflicting
- Use `unset VARIABLE_NAME` to clear unwanted variables