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
docker compose up -d --build
```

Default schedule: **07:00 Australia/Brisbane**. Set `RUN_ON_START=1` for a first send on container start.

Manual run without waiting:

```bash
docker compose run --rm digest python -m src --once
docker compose run --rm digest python -m src --dry-run
```

Seen URLs are stored in `data/seen.json` so repeats are not emailed again.

## Local tests

```bash
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -r requirements-dev.txt
ruff check . --fix && ruff format .
pytest
```
