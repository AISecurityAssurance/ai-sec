#!/bin/bash
# Run STPA-Sec Step 1 Analysis using Docker

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it using: export OPENAI_API_KEY='your-api-key'"
    exit 1
fi

# Build the CLI container if needed
echo "Building CLI container..."
docker-compose -f docker-compose.cli.yml build cli

# Run the analysis
echo "Running Step 1 analysis with GPT-4 Turbo..."
docker-compose -f docker-compose.cli.yml run --rm \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    cli python3 cli.py analyze --config configs/gpt4-turbo-standard.yaml

echo "Analysis complete!"