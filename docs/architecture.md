# Architecture Overview

This monorepo separates product apps from shared platform primitives.

- `apps/` contains the three vertical product surfaces. Each app owns its APIs, UIs, and domain logic.
- `shared/` is the internal platform layer with configuration, logging, schemas, and utilities that can be reused across apps without coupling them to a specific vertical.
- `infra/` provides local-first orchestration to run the baseline stack for development.

Boundaries are intentionally strict at this stage: apps may import from `shared/`, but `shared/` must remain agnostic of any single product. This keeps the platform layer lean while still enabling common patterns for observability and request/response contracts.
