"""Fetches news articles from RSS feeds."""

from dataclasses import dataclass, field
from typing import List, Optional
import feedparser


@dataclass
class Article:
    """Represents a single news article."""

    title: str
    summary: str
    link: str
    published: str = ""
    source: str = ""
    tags: List[str] = field(default_factory=list)


# Default RSS feeds covering a range of topics
DEFAULT_FEEDS = {
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "NPR": "https://feeds.npr.org/1001/rss.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
}


class NewsFetcher:
    """Fetches articles from one or more RSS feeds."""

    def __init__(self, feeds: Optional[dict] = None, max_articles: int = 10):
        """
        Initialize the fetcher.

        Args:
            feeds: Mapping of feed name to URL. Defaults to DEFAULT_FEEDS.
            max_articles: Maximum number of articles to fetch per feed.
        """
        self.feeds = feeds if feeds is not None else DEFAULT_FEEDS
        self.max_articles = max_articles

    def fetch_feed(self, name: str, url: str) -> List[Article]:
        """Fetch and parse a single RSS feed.

        Args:
            name: Human-readable feed name used as the article source.
            url: URL of the RSS feed.

        Returns:
            List of Article objects parsed from the feed.
        """
        parsed = feedparser.parse(url)
        articles: List[Article] = []
        for entry in parsed.entries[: self.max_articles]:
            tags = [t.get("term", "") for t in getattr(entry, "tags", [])]
            articles.append(
                Article(
                    title=entry.get("title", ""),
                    summary=entry.get("summary", entry.get("description", "")),
                    link=entry.get("link", ""),
                    published=entry.get("published", ""),
                    source=name,
                    tags=tags,
                )
            )
        return articles

    def fetch_all(self) -> List[Article]:
        """Fetch articles from all configured feeds.

        Returns:
            Combined list of Article objects from every feed.
        """
        all_articles: List[Article] = []
        for name, url in self.feeds.items():
            all_articles.extend(self.fetch_feed(name, url))
        return all_articles
