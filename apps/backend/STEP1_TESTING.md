# Step 1 Analysis Testing Guide

## Prerequisites

1. **Install Python dependencies**:
   ```bash
   pip install asyncpg httpx pyyaml rich
   ```

2. **PostgreSQL Setup**:
   - Ensure PostgreSQL is running (via Docker Compose in the project)
   - Database should be accessible at: `localhost:5432`
   - Credentials: `sa_user` / `sa_password`

3. **Model Provider Setup**:
   
   For OpenAI (GPT-4):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   For Ollama (local):
   ```bash
   # Install Ollama from https://ollama.ai
   ollama serve  # Start server
   ollama pull mixtral:instruct  # Download model
   ```

## Running Tests

### 1. Test Setup Verification
```bash
cd apps/backend
python3 test_step1_setup.py
```

This will verify:
- Database connectivity
- Model provider access
- Required files exist
- Python imports work

### 2. Load Demo Analysis
```bash
python3 cli.py demo
```

This loads the pre-packaged banking demo analysis without any LLM calls.

### 3. Run Standard Analysis with GPT-4
```bash
python3 cli.py analyze --config configs/test-gpt4-standard.yaml
```

### 4. Run Standard Analysis with Ollama
```bash
python3 cli.py analyze --config configs/test-ollama-standard.yaml
```

### 5. Run Enhanced ASI-ARCH Analysis
```bash
# Create enhanced config first
python3 cli.py analyze --config configs/enhanced-analysis.yaml
```

## Expected Outputs

Each analysis creates:
1. New PostgreSQL database (`stpa_analysis_YYYYMMDD_HHMMSS`)
2. Output directory with:
   - `analysis-config.yaml` - Configuration used
   - `analysis-results.json` - Complete results

## Completeness Check

The system automatically verifies:
- All 5 Step 1 artifacts are generated
- Required fields are present
- Minimum counts are met (3+ losses, hazards, stakeholders)
- Cross-artifact consistency

## Troubleshooting

1. **Database Connection Failed**:
   - Check Docker Compose is running: `docker-compose up -d`
   - Verify PostgreSQL container: `docker ps | grep postgres`

2. **Ollama Connection Failed**:
   - Ensure Ollama is running: `ollama serve`
   - Check model is downloaded: `ollama list`

3. **OpenAI API Failed**:
   - Verify API key is set: `echo $OPENAI_API_KEY`
   - Check API key is valid

4. **Import Errors**:
   - Install missing packages: `pip install <package>`
   - Ensure you're in `apps/backend` directory

## Configuration Options

### Model Selection
- `provider`: "openai" or "ollama"
- `name`: Model name (e.g., "gpt-4-turbo-preview", "mixtral:instruct")
- `temperature`: 0.0-1.0 (higher = more creative)

### Execution Modes
- `standard`: Single agent per task
- `enhanced`: Dual perspective (Intuitive + Technical)
- `dream_team`: All 4 cognitive styles (future)

### Validation Settings
- `check_completeness`: Enable completeness checking
- `min_losses`: Minimum required losses
- `min_hazards`: Minimum required hazards
- `min_stakeholders`: Minimum required stakeholders