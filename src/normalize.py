from urllib.parse import parse_qs, urlparse, urlunparse

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}


def _is_google_host(host: str) -> bool:
    # Require an exact google.com label (or subdomain). Plain endswith("google.com")
    # would also match attacker hosts like "evilgoogle.com".
    return host == "google.com" or host.endswith(".google.com")


def unwrap_google_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if _is_google_host(host) and parsed.path == "/url":
        target = parse_qs(parsed.query).get("q", [""])[0]
        # Require a real http(s) scheme; startswith("http") accepts "httpevil://…".
        if target.startswith(("http://", "https://")):
            return target
    return url


def strip_tracking(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return urlunparse(parsed._replace(fragment=""))
    kept = []
    for pair in parsed.query.split("&"):
        key = pair.split("=", 1)[0]
        if key.lower() not in TRACKING_PARAMS:
            kept.append(pair)
    query = "&".join(kept)
    return urlunparse(parsed._replace(query=query, fragment=""))


def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    return strip_tracking(unwrap_google_url(url.strip()))


def host_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""
