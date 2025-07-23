#!/bin/bash

echo "🔧 Setting up integration tests..."

cd integration-tests

# Install dependencies
echo "Installing test dependencies..."
npm install

# Install Playwright browsers
echo "Installing Playwright browsers..."
npx playwright install chromium

echo "✅ Integration test setup complete!"
echo ""
echo "To run tests:"
echo "  1. Make sure you have API keys in .env file"
echo "  2. Run: ./integration-tests/run-integration-tests.sh"