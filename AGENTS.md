# AGENTS.md

Agent-focused guidance for this repository ([AGENTS.md format](https://agents.md/)). Human-facing docs live in `README.md`.

## Project overview

Daily media digest for **Jodie Rummer / RummerLab / Physioshark / Athletes of the Reef**. Fetches scoped RSS + optional news APIs, dedupes, and emails new items. It does **not** scrape full article pages.

Runtime deps: `requirements.txt`. Lint/test deps: `requirements-dev.txt` (includes runtime via `-r requirements.txt`).

## Setup commands

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix:    source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # ruff + pytest
```

Secrets: copy `.env.example` → `.env`. Never commit `.env` (gitignored).

```bash
docker compose up -d --build
docker compose run --rm digest python -m src --once
docker compose run --rm digest python -m src --dry-run
```

## Lint and format (mandatory)

After every edit to Python files, before considering a task complete:

```bash
ruff check . --fix && ruff format .
```

Or: `python -m ruff check . --fix && python -m ruff format .`

- `ruff check .` — lint (`--fix` where possible)
- `ruff format .` — format
- Fix any remaining Ruff issues before finishing

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

Add or update tests for code you change. Fix failures before finishing.

## Code quality

- Prefer small, focused modules; clear names; type hints where helpful
- DRY: extract shared helpers when the same block appears 2+ times
- Error handling: catch explicitly; log and skip/return empty rather than crash a digest run
- Comments explain *why*, not *what*
- Python: PEP 8 (Ruff), `snake_case` / `PascalCase`, prefer `pathlib` where practical
- Optional API sources must no-op cleanly when their env key is blank

## Sources and env

- Core sources are RSS (Google News AU/US/UK, Bing, The Conversation Atom) plus GDELT DOC 2.0 (no key)
- Optional APIs: Guardian (`THE_GUARDIAN_API_KEY`), NewsAPI.org (`NEWS_API_ORG_KEY`)
- GDELT failures must log and return `[]` — the API can be flaky; never fail the whole digest
- Reserved optional keys in `.env.example` (not wired yet unless implemented): `NEWSAPI_AI_KEY`, `NEWSAPI_COM_KEY`, `GOOGLE_API_KEY`, `GOOGLE_CX_ID`, `SCRAPER_API_KEY`
- Do **not** add full-page article scraping; ScraperAPI is only for exceptional fetch helpers (e.g. redirect resolution), never as a content source
- Own sites (`rummerlab.com`, `jodierummer.com`, `physioshark.org`) stay excluded
- Seen URLs live in `data/seen.json` — do not wipe production state casually

## README and docs

`README.md` is the primary human documentation. Keep it accurate when you change:

- Features, setup, env vars (also `.env.example`), sources, Docker/run commands, dependencies

## Security

- Do not commit secrets, SMTP app passwords, or API keys
- Prefer rotating credentials if they may have been exposed
- CI must not require live SMTP or paid API keys

## Maintaining this file

Treat `AGENTS.md` as living agent docs:

- Add guidance when recurring patterns, tooling, or pitfalls emerge
- Update when standards change; remove redundant or conflicting text
- Keep sections focused and actionable; prefer concrete commands over vague advice


## Pull requests

Before merging any pull request:

1. **Read all comments** on the PR — conversation comments, review comments (including those on specific lines), and bot comments. Address or acknowledge them. Do not merge while review feedback is unresolved.
2. **Wait for CI to complete successfully.** GitHub Actions (and other required checks) on the PR must finish and pass. Do not merge while checks are pending, failed, cancelled, or skipped when they are required. If CI fails, fix the cause and wait for a green run before merging.
