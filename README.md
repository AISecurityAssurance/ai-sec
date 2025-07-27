# Security Analyst Platform

A comprehensive AI-powered security threat modeling and analysis platform supporting multiple frameworks including STPA-SEC, STRIDE, PASTA, DREAD, MAESTRO, LINDDUN, HAZOP, and OCTAVE.

## 🆕 Step 1 Analysis CLI (New!)

```bash
# Quick demo - no API keys needed
./ai-sec demo

# Run analysis with your own system
./ai-sec analyze --config configs/standard-analysis.yaml
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## 🚀 Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose
- Git
- At least one LLM API key (OpenAI or Anthropic)

### One-Command Setup

```bash
git clone https://github.com/AISecurityAssurance/prototype1.git
cd prototype1
./setup.sh
```

The setup script will guide you through:
1. Checking dependencies
2. Creating `.env` file for API keys
3. Building and starting all services
4. Verifying everything is running

### Access the Application
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

## 🚀 Manual Setup (Development)

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+
- PostgreSQL 15+
- Redis (optional)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/AISecurityAssurance/prototype1.git
   cd prototype1
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Start the development server**
   ```bash
   pnpm dev
   ```

4. **Open in browser**
   Navigate to http://localhost:5173

That's it! The app should be running locally.

## 📁 Project Structure

```
prototype1/
├── apps/
│   ├── frontend/         # React TypeScript UI
│   └── backend/          # FastAPI backend (includes security prompts)
├── packages/
│   └── types/            # Shared TypeScript types
└── documentation/        # Project documentation
```

## 🎯 Features

- **Security Analysis**: Automated STPA-Sec and STRIDE analysis
- **Admin Panel**: Configure models, prompts, and analysis parameters
- **Testing Arena**: Compare analysis variants side-by-side
- **Feedback System**: Collect user feedback with humor
- **Security Analyst Chat**: AI assistant for security queries

## 🛠️ Available Commands

```bash
# Development
pnpm dev              # Start frontend dev server
pnpm build            # Build all packages
pnpm lint             # Run linting

# Type generation (when backend is ready)
pnpm generate-types   # Generate TypeScript types from Python models
```

## 🎨 UI Features

- **Resizable chat panel**: Drag the left edge of the Security Analyst panel
- **Collapsible sidebars**: Click the menu icon to hide/show sidebars
- **Dark/Light theme**: Toggle in the top-right corner
- **Scrollable results**: Long analysis results scroll independently

## 🧪 Testing

### Testing the UI

1. **Analysis Page**: Upload files, run security analysis, chat with the assistant
2. **Admin Page**: Configure model settings and analysis parameters
3. **Testing Arena**: Compare different analysis approaches
4. **Feedback Page**: Submit feedback with our humorous AI job security quiz

### Integration Testing

The platform includes comprehensive integration tests that verify all components work together correctly.

#### Option 1: Testing WITHOUT Docker (Recommended for Quick Testing)

**Prerequisites:**
- Python 3.8+
- Node.js 18+

**Running Tests Locally:**

1. **Start the backend** (in one terminal):
   ```bash
   # With Ollama (recommended)
   export OLLAMA_ENDPOINT=http://localhost:11434
   ./run-backend-local.sh
   
   # Or without any LLM (uses mock responses)
   ./run-backend-local.sh
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd apps/web
   npm run dev
   ```

3. **Run the tests**:
   ```bash
   # Simple Python tests (no Node.js required)
   python test_backend.py
   
   # Or full integration tests with Playwright
   ./run-tests-local.sh
   ```

**Configuring Models:**
- You can configure models through the Settings UI (no .env required)
- Or set environment variables before starting the backend:
  ```bash
  export ANTHROPIC_API_KEY=your-key  # Optional
  export OPENAI_API_KEY=your-key     # Optional
  export OLLAMA_ENDPOINT=http://localhost:11434  # For local models
  ```

#### Option 2: Testing WITH Docker (Full Integration)

**Prerequisites:**
- Docker and Docker Compose installed
- API keys in `.env` file (optional with new settings system)

#### Running Integration Tests

1. **One-time setup** (installs test dependencies):
   ```bash
   ./integration-tests/setup-tests.sh
   ```

2. **Run all integration tests**:
   ```bash
   ./integration-tests/run-integration-tests.sh
   ```

   This will:
   - Start all services (PostgreSQL, Redis, Backend, Frontend)
   - Wait for services to be ready
   - Run the complete test suite
   - Clean up after tests complete

3. **Run tests manually** (for debugging):
   ```bash
   # Start services
   docker-compose -f docker-compose.test.yml up -d
   
   # Run tests
   cd integration-tests
   npm test
   
   # Run specific test file
   npm test tests/01-health-check.spec.ts
   
   # Run with UI mode (interactive)
   npm run test:ui
   
   # Stop services
   docker-compose -f docker-compose.test.yml down
   ```

#### What the Integration Tests Cover

- ✅ All 8 security frameworks (STPA-SEC, STRIDE, PASTA, DREAD, MAESTRO, LINDDUN, HAZOP, OCTAVE)
- ✅ WebSocket real-time updates and cross-tab synchronization
- ✅ Chat functionality with LlamaIndex context management
- ✅ Error handling and recovery scenarios
- ✅ State persistence across page refreshes
- ✅ Frontend-backend API communication

#### Troubleshooting Integration Tests

- **Port conflicts**: Ensure ports 3000, 8000, 5433, and 6380 are available
- **API key errors**: Verify your `.env` file has valid API keys
- **Docker issues**: Try `docker-compose -f docker-compose.test.yml down -v` to reset
- **Test failures**: Check logs with `docker-compose -f docker-compose.test.yml logs`

## 📝 Notes

- Frontend can run independently with mock data (no backend required for UI demo)
- Full platform requires backend services for real analysis
- Integration tests require Docker and valid LLM API keys
- All 8 security frameworks are fully implemented and tested

## 🤝 Contributing

See [CLAUDE.md](./CLAUDE.md) for AI assistant context and development guidelines.