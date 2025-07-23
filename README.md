# Security Analysis Platform

An AI-powered security analysis platform that automates STPA-Sec and STRIDE analysis for complex systems.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- pnpm (install with `npm install -g pnpm`)

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

#### Prerequisites for Integration Tests

1. **Docker and Docker Compose** installed
2. **Environment variables** - Create a `.env` file in the root directory:
   ```bash
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   GROQ_API_KEY=your-groq-api-key  # Optional
   GOOGLE_API_KEY=your-google-api-key  # Optional
   ```

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