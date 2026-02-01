# Repo Map (Quick Glance)

This is a high-level index of the repository with the purpose of each file or directory. It emphasizes the tools and skills commonly used by top-tier AI and full-stack teams.

## Root
- `README.md` - Product/platform overview, local run instructions, and baseline scope.
- `.env.example` - Environment template for local dev (FastAPI + Next.js + vLLM).
- `.gitignore` - Standard Python/Node/Docker local ignores.
- `.github/workflows/ci.yml` - GitHub Actions CI for Python linting and TypeScript typecheck (professional CI workflow).

## apps/
### apps/chatbot/
- `backend/` - FastAPI service (Python + Pydantic + Uvicorn). API-first and async-ready.
  - `app/main.py` - FastAPI app entrypoint and middleware wiring.
  - `app/routes/health.py` - Health check endpoint.
  - `app/routes/chat.py` - Chat endpoint wired to service layer.
  - `app/services/chat_service.py` - Legacy stub service (kept for reference).
  - `app/services/llm_client.py` - OpenAI-compatible LLM client (vLLM).
  - `app/services/conversation_store.py` - In-memory conversation store (Redis-ready).
  - `app/services/rate_limit.py` - Sliding window rate limiter.
  - `app/services/safety.py` - Adult-safe policy enforcement (blocks illegal categories).
  - `requirements.txt` - Backend dependencies.
  - `Dockerfile` - Backend container build.
- `frontend/` - Next.js App Router UI (React + TypeScript + Tailwind CSS).
  - `app/layout.tsx` - App Router root layout.
  - `app/page.tsx` - Chat UI page.
  - `lib/api.ts` - API client stub calling backend.
  - `lib/branding.ts` - Centralized product branding config (rebrandable).
  - `styles/globals.css` - Tailwind base + global styles.
  - `package.json` - Frontend scripts and dependencies.
  - `next.config.js` - Next.js config.
  - `tailwind.config.js` - Tailwind config (App Router paths).
  - `postcss.config.js` - Tailwind/PostCSS wiring.
  - `Dockerfile` - Frontend container build.
  - `README.md` - Notes about App Router + pages/ behavior.
  - `pages/` - Intentionally empty; avoids dev watcher ENOENT.

### apps/crypto-trading/
- `research/`, `training/`, `execution/` - Placeholder folders for AI trading workflows (data science, model training, execution services).

### apps/sports-betting/
- `data/`, `models/`, `services/` - Placeholder folders for data pipelines, modeling, and service layer.

## shared/
- `config/settings.py` - Env-based configuration (12-factor style).
- `logging/logger.py` - Structured logging (production-friendly JSON lines).
- `schemas/chat.py` - Shared Pydantic schemas for API contracts.
- `schemas/chat.ts` - Shared TypeScript types for frontend contracts.
- `utils/strings.py` - Small utility helpers.

## infra/
- `docker-compose.yml` - Local stack orchestration (Docker + Compose).
- `README.md` - Infra run instructions.

## docs/
- `vision.md` - Product vision across verticals.
- `architecture.md` - Boundaries between apps and shared layer.
- `compliance.md` - High-level governance notes for adult/financial/gambling domains.
- `repo-map.md` - This quick reference.

## Key professional tools/skills in use
- Next.js App Router, React, TypeScript, Tailwind CSS (modern frontend stack).
- FastAPI, Pydantic, Uvicorn (async API services).
- Docker + Docker Compose (local-first orchestration).
- GitHub Actions (CI automation).
- Structured logging + env-based configuration (production engineering fundamentals).
