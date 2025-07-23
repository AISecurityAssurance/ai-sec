# Security Analyst Platform - Integration Tests

This directory contains end-to-end integration tests for the Security Analyst Platform.

## Overview

The integration tests verify that:
- Frontend and backend services work together correctly
- WebSocket real-time updates function properly
- All 8 security frameworks produce expected results
- Chat functionality integrates with analysis context
- Error handling works across the system
- Cross-tab synchronization maintains state

## Prerequisites

1. Docker and Docker Compose installed
2. Node.js 18+ installed
3. Environment variables set in root `.env` file:
   ```
   OPENAI_API_KEY=your-key
   ANTHROPIC_API_KEY=your-key
   GROQ_API_KEY=your-key (optional)
   GOOGLE_API_KEY=your-key (optional)
   ```

## Setup

First time setup:
```bash
./integration-tests/setup-tests.sh
```

## Running Tests

To run all integration tests:
```bash
./integration-tests/run-integration-tests.sh
```

This script will:
1. Start all services using Docker Compose
2. Wait for services to be ready
3. Run the Playwright test suite
4. Clean up services after tests complete

## Running Individual Tests

To run tests manually:

1. Start services:
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

2. Run specific test:
   ```bash
   cd integration-tests
   npm test tests/01-health-check.spec.ts
   ```

3. Run tests with UI mode:
   ```bash
   npm run test:ui
   ```

4. Debug tests:
   ```bash
   npm run test:debug
   ```

## Test Structure

- `01-health-check.spec.ts` - Basic connectivity tests
- `02-create-analysis.spec.ts` - Analysis creation and progress
- `03-framework-analysis.spec.ts` - Framework-specific result tests
- `04-websocket-updates.spec.ts` - Real-time update tests
- `05-chat-integration.spec.ts` - Chat functionality tests
- `06-error-handling.spec.ts` - Error scenarios
- `07-all-frameworks.spec.ts` - Comprehensive framework tests

## Troubleshooting

### Services won't start
- Check Docker logs: `docker-compose -f docker-compose.test.yml logs`
- Ensure ports 3000, 8000, 5433, and 6380 are available

### Tests timeout
- Increase timeout in `playwright.config.ts`
- Check if services are responding: `curl http://localhost:8000/api/health`

### WebSocket tests fail
- Verify WebSocket endpoint: `wscat -c ws://localhost:8000/ws`
- Check browser console for connection errors

### Database errors
- Reset test database: `docker-compose -f docker-compose.test.yml down -v`
- Check migrations: `docker-compose -f docker-compose.test.yml logs backend`

## CI/CD Integration

For CI/CD pipelines, use:
```bash
# Run tests in CI mode
CI=true ./integration-tests/run-integration-tests.sh
```

This enables:
- Test retries on failure
- Headless browser mode
- Stricter error checking