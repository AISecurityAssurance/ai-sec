#!/bin/bash
# Run backend tests

echo "Running Security Analyst Backend Tests"
echo "====================================="

# Set test environment
export ENVIRONMENT=test
export DATABASE_URL=sqlite+aiosqlite:///:memory:
export SECRET_KEY=test-secret-key
export OPENAI_API_KEY=test-key
export ANTHROPIC_API_KEY=test-key

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest tests/ \
    -v \
    --cov=core \
    --cov=api \
    --cov-report=html \
    --cov-report=term-missing \
    --asyncio-mode=auto

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi