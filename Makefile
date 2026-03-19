.PHONY: check lint lint-docker lint-compose lint-deps test coverage-diff fmt fix

# ── Full quality gate ──
check: lint test

# ── Lint: check only — safe for AI, CI, pre-commit. Never modifies files. ──
lint:
	@uv run ruff format --check src/ tests/ || (echo "Formatting issues found. Run 'make fix' to auto-fix." && exit 1)
	@uv run ruff check src/ tests/ || (echo "Lint issues found. Fixable ones can be resolved with 'make fix'." && exit 1)
	@uv run ty check src/
	@git ls-files '*.yml' '*.yaml' | xargs uv run yamllint -s
	@hadolint Dockerfile gateway/Dockerfile
	@IMAGE_TAG=lint TRANSMISSION_USER=x TRANSMISSION_PASS=x JACKETT_API_KEY=x WEBDAV_URL=x WEBDAV_USER=x WEBDAV_PASS=x \
		AUTH0_DOMAIN=x AUTH0_CLIENT_ID=x AUTH0_CLIENT_SECRET=x AUTH0_AUDIENCE=x \
		docker compose -f docker-compose.prod.yml config --quiet
	@docker compose -f docker-compose.yml config --quiet
	@uv run pip-audit

# ── Fix: auto-fix formatting and import sorting, then verify with lint. ──
fix:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/
	$(MAKE) lint

# ── Tests (with 90% coverage gate, skip-covered output) ──
test:
	uv run python -m pytest

# ── Diff coverage: coverage of changed lines vs main. Fails below 95%. ──
coverage-diff:
	uv run diff-cover coverage.xml --compare-branch=origin/main --fail-under=95

# ── Aliases ──
fmt: fix
