# Security Analysis Platform - Frontend

## Overview

This is the React TypeScript frontend for the Security Analysis Platform. It includes four main applications:

1. **Analysis App** (`/analysis`) - Main user interface for security analysis
2. **Admin Panel** (`/admin`) - Configuration and tuning interface
3. **Testing Arena** (`/arena`) - A/B testing and comparison tools
4. **Feedback/CSAT** (`/feedback`) - Customer satisfaction and feedback collection

## Getting Started

### Development

```bash
# From the frontend directory
pnpm install
pnpm dev
```

The app will be available at http://localhost:5173

### Build

```bash
pnpm build
```

### Testing

```bash
pnpm test        # Run tests
pnpm test:ui     # Run tests with UI
pnpm coverage    # Generate coverage report
```

## Features

- **Dark/Light Theme**: Toggle between themes using the sun/moon icon
- **App Switching**: Navigate between apps using the top-right switcher
- **Responsive Design**: Works on desktop and tablet devices
- **Global Styles**: Consistent styling using CSS variables

## Architecture

- **State Management**: Zustand (to be implemented)
- **Routing**: React Router v6
- **Styling**: CSS with CSS Variables for theming
- **Type Safety**: TypeScript with gradual adoption
- **Component Library**: Custom components

## Project Structure

```
src/
├── apps/           # Main applications
│   ├── user/       # Analysis interface
│   ├── admin/      # Admin panel
│   ├── arena/      # Testing arena
│   └── csat/       # Feedback interface
├── components/     # Shared components
├── hooks/          # Custom React hooks
├── services/       # API and service layers
├── stores/         # Zustand stores
├── mocks/          # Mock data and providers
└── styles/         # Global styles
```

## Next Steps

1. Implement Zustand stores for state management
2. Create model provider implementations
3. Add file upload functionality
4. Implement vector search integration
5. Add real-time collaboration features