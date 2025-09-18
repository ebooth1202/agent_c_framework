# Multi-stage Dockerfile for Agent C Realtime Client SDK Demo App

# Stage 1: Base dependencies
FROM node:20-alpine AS base
RUN apk add --no-cache libc6-compat git
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm@9

# Stage 2: Install dependencies
FROM base AS deps
WORKDIR /app

# Copy workspace configuration files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY lerna.json ./

# Copy all package.json files for workspace packages
COPY packages/core/package.json ./packages/core/
COPY packages/react/package.json ./packages/react/
COPY packages/ui/package.json ./packages/ui/
COPY packages/demo/package.json ./packages/demo/

# Install dependencies using frozen lockfile
RUN pnpm install

# Stage 3: Build all packages from source
FROM base AS builder
WORKDIR /app

# copy self signed cert
COPY localhost_self_signed-key.pem ./
COPY localhost_self_signed.pem ./

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages/core/node_modules ./packages/core/node_modules
COPY --from=deps /app/packages/react/node_modules ./packages/react/node_modules
COPY --from=deps /app/packages/ui/node_modules ./packages/ui/node_modules
COPY --from=deps /app/packages/demo/node_modules ./packages/demo/node_modules

# Copy workspace configuration
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY lerna.json tsconfig.json ./
COPY eslint.config.mts ./

# Copy source code for all packages
COPY packages/core ./packages/core
COPY packages/react ./packages/react
COPY packages/ui ./packages/ui
COPY packages/demo ./packages/demo

# Build packages in dependency order
# 1. Build core package first (no internal dependencies)
RUN cd packages/core && pnpm build

# 2. Build react package (depends on core)
RUN cd packages/react && pnpm build

# 3. Build ui package (depends on core and react)
RUN cd packages/ui && pnpm build

# 4. Build demo app (depends on all workspace packages)
RUN cd packages/demo && pnpm build

# Stage 4: Production runner
FROM node:20-alpine AS runner
WORKDIR /app

# Install git which pnpm needs
RUN apk add --no-cache git

# Add non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Set NODE_ENV to production
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Install pnpm in runner for package resolution
RUN npm install -g pnpm@9

# Copy necessary files from builder
# Copy package files
COPY --from=builder /app/package.json ./
COPY --from=builder /app/pnpm-lock.yaml ./
COPY --from=builder /app/pnpm-workspace.yaml ./
COPY --from=builder /app/lerna.json ./

# Copy built packages
COPY --from=builder --chown=nextjs:nodejs /app/packages/core/package.json ./packages/core/
COPY --from=builder --chown=nextjs:nodejs /app/packages/core/dist ./packages/core/dist

COPY --from=builder --chown=nextjs:nodejs /app/packages/react/package.json ./packages/react/
COPY --from=builder --chown=nextjs:nodejs /app/packages/react/dist ./packages/react/dist

COPY --from=builder --chown=nextjs:nodejs /app/packages/ui/package.json ./packages/ui/
COPY --from=builder --chown=nextjs:nodejs /app/packages/ui/dist ./packages/ui/dist
# UI package also needs source for transpilation
COPY --from=builder --chown=nextjs:nodejs /app/packages/ui/src ./packages/ui/src

# Copy demo app
COPY --from=builder --chown=nextjs:nodejs /app/packages/demo/package.json ./packages/demo/
COPY --from=builder --chown=nextjs:nodejs /app/packages/demo/.next ./packages/demo/.next
COPY --from=builder --chown=nextjs:nodejs /app/packages/demo/next.config.js ./packages/demo/
COPY --from=builder --chown=nextjs:nodejs /app/packages/demo/public ./packages/demo/public

# Install production dependencies only
RUN pnpm install --frozen-lockfile --prod --ignore-scripts

# Switch to non-root user
USER nextjs

# Expose the port Next.js runs on
EXPOSE 3000

# Change to demo directory and start the application
WORKDIR /app/packages/demo

# Use Next.js production server
CMD ["pnpm", "start", "--experimental-https-key localhost_self_signed-key.pem", "--experimental-https-cert localhost_self_signed.pem"]