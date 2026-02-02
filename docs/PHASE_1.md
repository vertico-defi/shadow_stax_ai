# Phase 1 — Persona + Memory Scaffolding

## Summary
- Adds persona JSON + schema validation at startup.
- Adds SQLite-backed memory scaffolding (summary, memories, relationship state).
- Adds deterministic prompt builder layering.
- Keeps chat working end-to-end with minimal behavioral changes.

## SQLite location
- Default: `apps/chatbot/backend/data/memory.db`
- Override with `MEMORY_DB_PATH` in `.env`.

## Tests
Run backend tests:

```bash
docker compose -f infra/docker-compose.yml exec backend pytest
```

## Notes
- Memory extraction is rule-based and only stores explicit statements.
- Vector retrieval and embeddings are deferred to Phase 2.
