# Development Dockerfile with hot reloading
FROM node:18-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 5173

# Start dev server with hot reloading
CMD ["pnpm", "dev", "--host", "0.0.0.0"]