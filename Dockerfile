# Multi-stage Dockerfile for Turborepo monorepo Next.js apps
FROM node:20-alpine AS base
RUN apk add --no-cache libc6-compat openssl
WORKDIR /app

# Install dependencies
FROM base AS deps
# Copy all package files for workspace resolution
COPY package.json package-lock.json* ./
COPY packages/database/package.json ./packages/database/
COPY packages/shared-types/package.json ./packages/shared-types/
COPY packages/ui/package.json ./packages/ui/
COPY packages/config/eslint-config/package.json ./packages/config/eslint-config/
COPY packages/config/typescript-config/package.json ./packages/config/typescript-config/
COPY apps/backend/package.json ./apps/backend/
COPY apps/candidate-portal/package.json ./apps/candidate-portal/
COPY apps/recruiter-portal/package.json ./apps/recruiter-portal/
COPY apps/admin-portal/package.json ./apps/admin-portal/

# Copy Prisma schema
COPY packages/database/prisma ./packages/database/prisma

# Install all dependencies
RUN npm ci

# Build stage
FROM base AS builder

ARG APP_NAME
ENV APP_NAME=${APP_NAME}

# Copy node_modules from deps
COPY --from=deps /app/node_modules ./node_modules

# Copy all source code
COPY . .

# Generate Prisma Client
RUN npx prisma generate --schema=./packages/database/prisma/schema.prisma

# Build the specific app (cd into app directory and run next build)
RUN cd apps/${APP_NAME} && npm run build

# Production stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

ARG APP_NAME
ENV APP_NAME=${APP_NAME}

# Copy necessary files for Next.js
COPY --from=builder /app/apps/${APP_NAME}/next.config.js ./
COPY --from=builder /app/apps/${APP_NAME}/package.json ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/${APP_NAME}/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/${APP_NAME}/.next/static ./apps/${APP_NAME}/.next/static

# Copy Prisma for runtime with binaries (entire prisma bin folder)
COPY --from=builder /app/node_modules/prisma ./node_modules/prisma
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder /app/node_modules/@prisma ./node_modules/@prisma
COPY --from=builder /app/packages/database ./packages/database
COPY --from=builder /app/node_modules/.bin ./node_modules/.bin

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Use conditional entrypoint
ENTRYPOINT ["/bin/sh", "-c", "if [ \"$APP_NAME\" = \"backend\" ]; then /usr/local/bin/docker-entrypoint.sh; else node apps/${APP_NAME}/server.js; fi"]
