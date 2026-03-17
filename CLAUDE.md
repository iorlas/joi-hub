# Reelm — AI Agent Context

Your personal media agent — AI-native alternative to Sonarr/Radarr.

## Build & Test

- `make check` — full quality gate (lint + test), run before every commit
- `make lint` — all linters (ruff, ty, yamllint, hadolint, compose validation, pip-audit)
- `make test` — pytest with 95% coverage gate (shows only files below threshold)
- `make fmt` — auto-fix Python formatting

## Architecture

```
Internet → Agentgateway (Rust, OAuth 2.1, tool federation)
               ├→ reelm-transmission (MCP server, Transmission RPC)
               ├→ reelm-jackett (MCP server, torrent search)
               ├→ reelm-storage (MCP server, WebDAV file ops)
               └→ future services (Jellyfin, mem0, etc.)
```

- **Each MCP server is standalone** — no auth, no shared state, independently deployable
- **Agentgateway** handles auth (OAuth 2.1) and federation (virtual MCP, tool prefixing)
- **Source layout**: `src/mcps/servers/` — one file per MCP server, `src/mcps/shared/` — pagination, query, schema utils

## Conventions

- All MCP tool functions go in `src/mcps/servers/<service>.py`
- Shared utilities (pagination, filtering, projection) in `src/mcps/shared/`
- Config via `pydantic-settings` in `src/mcps/config.py` — env vars, no hardcoded values
- Tests: `@pytest.mark.unit` for unit tests, `@pytest.mark.contract` for VCR replay tests
- Cassettes in `tests/cassettes/`, golden snapshots in `tests/snapshots/`

## Deployment

- **Model B**: GitHub Actions builds images → pushes to GHCR → updates Dokploy via API → deploys
- **Compose**: `docker-compose.prod.yml` is the source of truth, pushed to Dokploy atomically
- **Images**: SHA-pinned tags (`main-<sha>`), never `:latest` for our images
- **Dokploy API only** — never SSH for routine operations
- See `~/Documents/Knowledge/Researches/036-deployment-platform/guidelines/` for full deployment platform docs

## Never

- Never add auth code to MCP servers — agentgateway handles all auth
- Never use SSH for deployment debugging — escalation: API → UI → Swagger → SSH (last resort)
- Never use `:latest` tag for reelm images — always SHA-pinned
- Never manually create/start/stop Dokploy-managed containers with docker commands
- Never commit secrets or `.env` files

## Ask First

- Before adding a new MCP server or external dependency
- Before changing the gateway config or auth flow
- Before modifying docker-compose.prod.yml structure (networks, volumes, labels)
- Before changing the CI/CD pipeline
