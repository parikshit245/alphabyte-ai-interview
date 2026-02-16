# AI Interview Intelligence Platform

Enterprise-grade AI Interview Intelligence Platform built with modern monorepo architecture.

> 📖 **[View Complete Setup Guide](./SETUP.md)** - Detailed instructions for running the full platform or individual components

## Tech Stack

- **Monorepo**: Turborepo with pnpm workspaces
- **Runtime**: Node.js 20+
- **Frontend**: Next.js 15 (App Router), React 19, TypeScript
- **Styling**: Tailwind CSS v3.4.x, shadcn/ui, Tremor
- **Database**: CockroachDB with Prisma ORM
- **Authentication**: JWT with bcrypt, role-based access control
- **Containerization**: Docker Compose

## ✨ Features

### Authentication System
- ✅ **User Registration** - Create accounts for Candidates, Recruiters, and Admins
- ✅ **Secure Login/Logout** - JWT-based authentication with token expiration
- ✅ **Role-Based Access Control** - Separate portals for each user type
- ✅ **Protected Routes** - Automatic redirect to login for unauthorized access
- ✅ **Session Management** - Persistent login state with token refresh

### Platform Portals
- ✅ **Candidate Portal** - For job seekers taking AI interviews
- ✅ **Recruiter Portal** - For hiring managers managing candidates and jobs
- ✅ **Admin Portal** - For platform administrators managing users and companies

### Infrastructure
- ✅ **Containerized Deployment** - Full Docker Compose setup
- ✅ **Database Management** - CockroachDB with Prisma migrations
- ✅ **API Backend** - RESTful API with Next.js API routes
- ✅ **CORS Configured** - Cross-origin requests enabled for all portals
- ✅ **Health Checks** - Service monitoring and status endpoints

## Project Structure

```
ai-interview-platform/
├── apps/
│   ├── candidate-portal/    # Candidate-facing Next.js app
│   ├── recruiter-portal/    # Recruiter dashboard Next.js app
│   ├── admin-portal/        # Admin panel Next.js app
│   └── backend/             # API backend (Next.js API routes)
├── packages/
│   ├── shared-types/        # Shared TypeScript types
│   ├── database/            # Prisma schema and client
│   ├── ui/                  # Shared UI components
│   └── config/              # Shared configs (ESLint, TypeScript)
└── docker-compose.yml       # Local development environment
```

## Getting Started

### Quick Start (Docker - Recommended)

```bash
# Start all services
docker compose up -d

# Seed test accounts
.\scripts\seed-users.ps1
```

**That's it!** All services are now running:
- **Candidate Portal**: http://localhost:3000
- **Recruiter Portal**: http://localhost:3001
- **Admin Portal**: http://localhost:3002
- **Backend API**: http://localhost:3003

### Login Credentials

- **Candidate**: `candidate@test.com` / `password123`
- **Recruiter**: `recruiter@test.com` / `password123`
- **Admin**: `admin@test.com` / `password123`

### 📖 Detailed Setup Instructions

For detailed setup, local development, troubleshooting, and more:

👉 **[Read the Complete Setup Guide](./SETUP.md)**

Includes:
- Running individual apps for testing
- Local development without Docker
- Database management
- Troubleshooting common issues
- Testing registration & login flows

---

## Application URLs

- **Candidate Portal**: http://localhost:3000
- **Recruiter Portal**: http://localhost:3001
- **Admin Portal**: http://localhost:3002
- **Backend API**: http://localhost:3003
- **CockroachDB Admin**: http://localhost:8080
- **Prisma Studio**: Run `cd packages/database && npx prisma studio`

## Development

### Useful Docker Commands

```bash
# View all running containers
docker compose ps

# View logs for all services
docker compose logs -f

# View logs for specific service
docker compose logs -f backend

# Restart a service
docker compose restart backend

# Stop all services
docker compose down

# Rebuild and restart
docker compose up -d --build
```

### Available Scripts

- `pnpm dev` - Start all apps in development mode
- `pnpm build` - Build all apps for production
- `pnpm lint` - Lint all packages
- `pnpm type-check` - Run TypeScript type checking
- `pnpm format` - Format code with Prettier
- `pnpm db:generate` - Generate Prisma client
- `pnpm db:push` - Push schema to database
- `pnpm check` - Run type-check, lint, and build

### Adding Dependencies

Add to specific workspace:
```bash
pnpm add <package> --filter <workspace-name>
```

Add to root:
```bash
pnpm add -w <package>
```

## Architecture

### Authentication Flow

- Manual JWT implementation (no NextAuth)
- Access tokens: 15 minutes
- Refresh tokens: 7 days (httpOnly cookie)
- bcrypt for password hashing

### Database

- CockroachDB as PostgreSQL-compatible distributed SQL
- Prisma ORM with `cockroachdb` provider
- UUID-based primary keys
- Soft delete support

### AI JSON-RPC API

Endpoint: `POST /api/ai/jsonrpc`

Methods:
- `parseResume`
- `generateQuestions`
- `evaluateAnswer`
- `calculateMatchScore`
- `behavioralAnalysis`
- `integrityScoring`

## 🎯 Hackathon Demo Setup

Quick 5-minute setup for demonstrations:

```bash
# 1. Start all services
docker compose up -d

# 2. Wait for services to be ready (30 seconds)
docker compose ps

# 3. Seed test accounts
.\scripts\seed-users.ps1

# 4. Open all portals
start http://localhost:3000  # Candidate
start http://localhost:3001  # Recruiter
start http://localhost:3002  # Admin
```

### Demo Credentials
- **Candidate**: `candidate@test.com` / `password123`
- **Recruiter**: `recruiter@test.com` / `password123`
- **Admin**: `admin@test.com` / `password123`

### Demo Flow
1. **Register** a new account at `/register`
2. **Login** with test credentials
3. **Navigate** the dashboard
4. **Logout** and login again
5. **Test** role-based access by visiting different portals

## License

Proprietary - All Rights Reserved
