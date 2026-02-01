# Shadow Stax AI

Shadow Stax AI is a multi-vertical platform scaffold for applied AI products spanning adult-content chat experiences, crypto trading systems, and sports betting prediction services. This repository establishes a clean local development foundation with consistent structure, shared platform primitives, and a minimal chatbot flow for end-to-end validation.

## Architecture overview

- Product apps live under `apps/` and own their domain-specific APIs and UIs.
- Shared platform primitives (config, logging, schemas, utilities) live in `shared/` and are consumed by apps.
- Local-first orchestration lives in `infra/` to run the baseline stack.

## Run locally

1. Copy the environment template:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose -f infra/docker-compose.yml up --build
```

The chatbot backend will be available at `http://localhost:8000/health`, and the frontend at `http://localhost:3000`.

### LLM-backed chat (Ollama default, vLLM optional)

By default the stack uses Ollama at `http://ollama:11434` (CPU-friendly). You can switch to vLLM if you have an NVIDIA GPU.

**Initial startup**

```bash
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml logs -f backend
```

**If only editing backend Python code**

Uvicorn runs with `--reload`, so saving the file auto-reloads the backend (no container restart needed).

**If editing docker-compose or LLM config**

```bash
docker compose -f infra/docker-compose.yml down
docker compose -f infra/docker-compose.yml up -d --build
```

**Quick backend test (no frontend)**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages":[{"role":"user","content":"Hello"}],
    "stream": false
  }'
```

**Streaming test**

```bash
curl -N http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages":[{"role":"user","content":"Hello"}],
    "stream": true
  }'
```

### vLLM (optional GPU path)

Run vLLM via a Compose profile (requires NVIDIA GPU + drivers + CUDA):

```bash
docker compose -f infra/docker-compose.yml --profile vllm up -d --build
```

Then set `LLM_BASE_URL=http://llm:8001/v1` and `LLM_MODEL=<hf-model-name>` in `.env`, and restart the stack.

## Directory responsibilities

- `apps/`: Product verticals (chatbot, crypto trading, sports betting).
- `shared/`: Reusable config, logging, schemas, and utilities.
- `infra/`: Local Docker orchestration.
- `docs/`: Vision, architecture boundaries, and compliance notes.

## Deferred at baseline

- Model loading or inference
- Exchange integrations or live trading
- Betting execution or data scraping
- Authentication and authorization
- Databases and persistence
- Kubernetes or cloud deployment
- UI polish beyond minimal scaffolding

This is a foundation scaffold, not an MVP.
