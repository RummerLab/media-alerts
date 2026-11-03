# RummerLab media alerts

Daily digest of news/media mentions of **Jodie Rummer**, **RummerLab**, **Physioshark**, and **Athletes of the Reef**. Complements Google Alerts and Talkwalker Alerts. It does **not** scrape full article pages.

Each morning it fetches targeted RSS/API sources, dedupes them, and emails new items to `athletesofthereef@gmail.com` in a Google Alerts-style message.

## Talkwalker Alerts (use alongside this)

**Search query**

```
"Jodie Rummer" OR RummerLab OR "Rummer Lab" OR Physioshark OR "Athletes of the Reef"
```

**Result type:** start with **News** only.

That matches Google Alerts and this digest. Add a second Talkwalker alert for **Blogs** if you want Cosmos/Oceanographic-style sites. Skip **Twitter** and **Discussions** unless you want social noise.

## Sources

| Source | Notes |
| --- | --- |
| Google News RSS (AU) | Targeted keyword search |
| Google News RSS (US) | Catches Independent, Popular Mechanics, Forbes, etc. |
| Google News RSS (UK) | Guardian / Independent UK editions |
| Bing News RSS | Second crawler |
| The Conversation author Atom | [Jodie L. Rummer](https://theconversation.com/profiles/jodie-l-rummer-711270/articles.atom) |
| [GDELT](https://www.gdeltproject.org/) DOC 2.0 | Free global article search; no API key |
| Guardian Open Platform | Optional `THE_GUARDIAN_API_KEY` |
| NewsAPI.org | Optional `NEWS_API_ORG_KEY` (free tier: `/v2/top-headlines`) |
| newsapi.ai / Google CSE / etc. | Keys in `.env.example`; sources not wired yet |

Generic outlet firehoses (whole ABC / SMH feeds) from the old Scholar scraper are **not** included. Those created more noise than Google Alerts. This tool only uses search feeds and APIs already scoped to Jodie/the lab.

Own sites (`rummerlab.com`, `jodierummer.com`, `physioshark.org`) are dropped.

## Setup

1. Copy `.env.example` to `.env`.
2. Create a [Gmail App Password](https://myaccount.google.com/apppasswords) for `athletesofthereef@gmail.com` and set `SMTP_PASSWORD`.
3. Optional: register a free [Guardian Open Platform](https://open-platform.theguardian.com/access/) key and/or [NewsAPI](https://newsapi.org/register) key.
4. Run:

```bash
cp .env.example .env
docker compose pull
docker compose up -d --no-build
```

Default schedule: **07:00 Australia/Brisbane**. Set `RUN_ON_START=1` for a first send on container start.

Manual run without waiting:

```bash
docker compose run --rm digest python -m src --once
docker compose run --rm digest python -m src --dry-run
```

Seen URLs are stored in `data/seen.json` so repeats are not emailed again.

The container runs as a non-root user (`APP_UID`/`APP_GID`, default `1000:1000`), and that user must be able to write `./data`. If your host user isn't 1000, set `APP_UID`/`APP_GID` in `.env` to the output of `id -u` / `id -g`. Images up to v0.0.2 ran as root, so an existing `data/` may be root-owned. Fix it once before upgrading:

```bash
sudo chown -R "${APP_UID:-1000}:${APP_GID:-1000}" data
```

## Local tests

```bash
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -r requirements-dev.txt
ruff check . --fix && ruff format .
pytest
```

## Container releases and nightly dependency updates

Production Compose pulls GHCR images with native ARM64 (Odroid) and AMD64 support. After merging this change and publishing the first release, run from the existing deployment directory:

```bash
git pull --ff-only
docker compose pull
docker compose up -d --no-build --remove-orphans
docker compose ps
```

Keep the same Compose project name and existing volumes/bind mounts. Keep your `.env` and credentials; do not delete production data. The existing Watchtower installation can follow `latest` using the containers' `com.centurylinklabs.watchtower.enable=true` labels. If Watchtower filters names or scopes, include these containers in that configuration. No second Watchtower instance is needed. Watchtower applies new images, while future Compose and environment changes still need `git pull` and `docker compose up`. GHCR packages must be public for anonymous pulls; alternatively configure registry authentication in Docker and Watchtower.

Use the Compose tag variable (`SCHOLAR_IMAGE_TAG` for Scholar, `IMAGE_TAG` for the other apps) to pin both services to a published `vMAJOR.MINOR.PATCH` tag for rollback. Local builds use `docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build` (Scholar must first build its base service with the same two files).

`docker-release.yml` publishes stable `v*` tag pushes, manual runs with an existing version tag, and calls from the nightly updater. It checks the exact release commit, validates both native architectures without secrets or upstream services, publishes the GitHub release, then updates the multi-platform `latest` tags. To publish manually, push an unused stable version tag on `main`, or rerun the Docker release workflow with that existing tag. The normal `GITHUB_TOKEN` needs contents/packages write permission; no PAT is required. Tag publication created by `GITHUB_TOKEN` does not trigger other workflows, so nightly calls the reusable release workflow explicitly.

Nightly updates run at 00:37 Australia/Brisbane. Python direct constraints live in `requirements.txt` and `requirements-dev.txt`; their generated `requirements.lock` and `requirements-dev.lock` pin the full graph with hashes. uv excludes versions uploaded in the last **three days** and keeps upgrades within each locked package's major (within its minor for 0.x), without downgrading. The podcast frontend uses pinned pnpm, a frozen lockfile in CI/Docker, and `minimumReleaseAge: 4320` for direct and transitive packages. The age gate reduces exposure to newly compromised releases; it does not guarantee package safety.

Only a changed **production** Python graph or podcast frontend production graph creates a patch version, tag, GitHub release, and image. This includes transitive and platform-specific runtime changes. Developer tooling, frontend devDependencies, and hash-only lock changes are committed after checks but do not release. With no changes, the run does nothing. Tests, lint, and a local production image smoke test run before a production update is committed; the release then checks both architectures. The bot refuses to rebase if `main` changed during validation, and pushes the tested commit/tag atomically. Branch rules must allow this bot to push dependency commits to `main`; failures remain visible in Actions rather than bypassing protections.

To refresh manually, install `uv==0.13.7` (and `pnpm@12.15.0` for the podcast frontend), then run `python scripts/dependency_release.py update`. Do not edit generated lockfiles by hand. Nightly uses existing stable tags when choosing the next patch version, even if project metadata previously lagged behind a release.
