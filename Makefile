.PHONY: check lint lint-python lint-types lint-yaml lint-docker lint-compose lint-deps test fmt

# ── Full quality gate ──
check: lint test

# ── All linters ──
lint: lint-python lint-types lint-yaml lint-docker lint-compose lint-deps

# ── Python: ruff check + format ──
lint-python:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

# ── Type checking: ty ──
lint-types:
	uv run ty check src/

# ── YAML: docker-compose, gateway config ──
lint-yaml:
	uv run yamllint -s docker-compose.yml docker-compose.prod.yml gateway/config.yaml .yamllint.yml .github/workflows/*.yml

# ── Dockerfiles ──
lint-docker:
	hadolint Dockerfile gateway/Dockerfile

# ── Compose syntax validation ──
lint-compose:
	IMAGE_TAG=lint TRANSMISSION_USER=x TRANSMISSION_PASS=x JACKETT_API_KEY=x WEBDAV_URL=x WEBDAV_USER=x WEBDAV_PASS=x \
		AUTH0_DOMAIN=x AUTH0_CLIENT_ID=x AUTH0_CLIENT_SECRET=x AUTH0_AUDIENCE=x \
		docker compose -f docker-compose.prod.yml config --quiet
	docker compose -f docker-compose.yml config --quiet

# ── Dependency vulnerabilities ──
lint-deps:
	uv run pip-audit

# ── Tests (with 95% coverage, shows only files below threshold) ──
test:
	uv run python -m pytest

# ── Auto-fix what can be fixed ──
fmt:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/
