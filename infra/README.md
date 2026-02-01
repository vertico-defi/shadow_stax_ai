# Local Infrastructure

This folder contains local-first orchestration for the baseline stack.

- `docker-compose.yml` starts the vLLM service, FastAPI backend, and Next.js frontend for the chatbot vertical.

Run it from the repo root with:

```bash
docker compose -f infra/docker-compose.yml up --build
```
