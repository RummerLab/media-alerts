from dataclasses import dataclass, field


@dataclass(slots=True)
class Article:
    title: str
    url: str
    source: str
    snippet: str = ""
    published: str = ""
    feed: str = ""
    trusted: bool = False
    extra_urls: list[str] = field(default_factory=list)
