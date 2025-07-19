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

## 🧪 Testing the UI

1. **Analysis Page**: Upload files, run security analysis, chat with the assistant
2. **Admin Page**: Configure model settings and analysis parameters
3. **Testing Arena**: Compare different analysis approaches
4. **Feedback Page**: Submit feedback with our humorous AI job security quiz

## 📝 Notes

- Frontend runs independently (no backend required for UI demo)
- Mock data is used for all analysis results
- The backend integration is planned for the next phase

## 🤝 Contributing

See [CLAUDE.md](./CLAUDE.md) for AI assistant context and development guidelines.