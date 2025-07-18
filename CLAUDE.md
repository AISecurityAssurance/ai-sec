# Security Platform Prototype - CLAUDE.md

## Project Overview
Building a rapid prototype of a systems engineering security and threat modeling design and analysis application.

## Key Technologies
- Frontend: React TypeScript
- Backend: FastAPI
- Design Principles: SOLID principles, model-agnostic approach using Protocols

## Architecture Requirements
1. **Model Agnostic Approach**: Use Protocols to define interfaces for:
   - Model integration (separate responses, token stats, input formatting, client setup)
   - Storage abstraction (in-house storage, cloud storage, credential management)

2. **Frontend Requirements**:
   - Convert template.html to React TypeScript components
   - Follow React best practices (functional components, hooks, proper state management)
   - Component-based architecture with small, focused components
   - Performance optimization (memoization, code splitting)

3. **Backend Requirements**:
   - FastAPI with modular structure
   - Dependency injection
   - Pydantic for data validation
   - ASGI server for production deployment

## Coding Standards
- Always apply SOLID design principles
- Create reusable, testable components
- Maintain clear separation of concerns
- Use TypeScript for type safety
- Follow DRY principle

## Commands
- Dev: `pnpm dev` (from apps/frontend)
- Build: `pnpm build`
- Lint: `pnpm lint`
- Test: `pnpm test`
- Generate types: `pnpm generate-types` (from root)

## Project Structure
```
/apps
  /frontend         # React TypeScript app (✓ implemented)
    /src
      /apps         # 4 main applications
      /components   # Shared components
      /hooks        # Custom React hooks
      /stores       # Zustand stores (pending)
      /services     # API services (pending)
      /mocks        # Mock providers
      /styles       # Global CSS
  /backend          # FastAPI app (pending)
/packages
  /types            # Shared TypeScript types (✓ implemented)
```

## Progress
- ✅ Monorepo setup with Turborepo
- ✅ Frontend React app with Vite
- ✅ Global CSS with theme system
- ✅ React Router with 4 apps
- ✅ All 4 app interfaces (User, Admin, Arena, CSAT)
- ✅ Chat functionality UI
- ✅ Shared types package
- ⏳ Zustand state management
- ⏳ Model provider implementations
- ⏳ FastAPI backend
- ⏳ File upload functionality
- ⏳ Vector search integration

## Notes
- Prefer Protocols over class hierarchies for models and storage (as per security-platform-architecture.md)
- Focus on security and threat modeling capabilities
- This is a rapid prototype focused on demonstrating key concepts