import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

QUERY = '"Jodie Rummer" OR RummerLab OR "Rummer Lab" OR Physioshark OR "Athletes of the Reef"'
ENCODED_QUERY = quote_plus(QUERY)

GOOGLE_NEWS_AU = (
    "https://news.google.com/rss/search"
    f"?q={ENCODED_QUERY}&hl=en-AU&gl=AU&ceid=AU:en"
)
GOOGLE_NEWS_US = (
    "https://news.google.com/rss/search"
    f"?q={ENCODED_QUERY}&hl=en&gl=US&ceid=US:en"
)
GOOGLE_NEWS_GB = (
    "https://news.google.com/rss/search"
    f"?q={ENCODED_QUERY}&hl=en-GB&gl=GB&ceid=GB:en"
)
BING_NEWS = (
    "https://www.bing.com/news/search"
    f"?q={ENCODED_QUERY}&format=rss"
)
CONVERSATION_ATOM = (
    "https://theconversation.com/profiles/jodie-l-rummer-711270/articles.atom"
)

RSS_FEEDS: list[dict[str, str | bool]] = [
    {"name": "Google News AU", "url": GOOGLE_NEWS_AU},
    {"name": "Google News US", "url": GOOGLE_NEWS_US},
    {"name": "Google News UK", "url": GOOGLE_NEWS_GB},
    {"name": "Bing News", "url": BING_NEWS},
    {
        "name": "The Conversation",
        "url": CONVERSATION_ATOM,
        "trusted": True,
    },
]

RELEVANCE_PHRASES = (
    "jodie rummer",
    "jodie l. rummer",
    "dr rummer",
    "professor rummer",
    "rummerlab",
    "rummer lab",
    "physioshark",
    "athletes of the reef",
    "physiologyfish",
)

EXCLUDED_HOST_SUFFIXES = (
    "rummerlab.com",
    "jodierummer.com",
    "physioshark.org",
)

DATA_DIR = os.environ.get("DATA_DIR", "data")
SEEN_PATH = os.path.join(DATA_DIR, "seen.json")

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER)
MAIL_TO = [
    address.strip()
    for address in os.environ.get("MAIL_TO", "athletesofthereef@gmail.com").split(",")
    if address.strip()
]
MAIL_CC = [
    address.strip()
    for address in os.environ.get("MAIL_CC", "").split(",")
    if address.strip()
]

GUARDIAN_API_KEY = os.environ.get("THE_GUARDIAN_API_KEY", "").strip()
NEWS_API_ORG_KEY = os.environ.get("NEWS_API_ORG_KEY", "").strip()

DIGEST_HOUR = int(os.environ.get("DIGEST_HOUR", "7"))
DIGEST_MINUTE = int(os.environ.get("DIGEST_MINUTE", "0"))
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "7"))
RUN_ON_START = os.environ.get("RUN_ON_START", "0").lower() in {"1", "true", "yes"}
USER_AGENT = "RummerLabMediaAlerts/1.0 (+https://rummerlab.com)"
