"""Tests for news_analyzer.fetcher."""

from unittest.mock import MagicMock, patch

import pytest

from news_analyzer.fetcher import Article, NewsFetcher, DEFAULT_FEEDS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_entry(title="Test Headline", summary="A brief summary.", link="http://example.com/1", published="Mon, 01 Jan 2024 00:00:00 +0000", tags=None):
    entry = MagicMock()
    entry.get = lambda key, default="": {
        "title": title,
        "summary": summary,
        "link": link,
        "published": published,
    }.get(key, default)
    entry.tags = [MagicMock(get=lambda k, d="", _t=t: {"term": _t}.get(k, d)) for t in (tags or [])]
    return entry


def _make_parsed(entries):
    parsed = MagicMock()
    parsed.entries = entries
    return parsed


# ---------------------------------------------------------------------------
# Article dataclass
# ---------------------------------------------------------------------------

class TestArticle:
    def test_defaults(self):
        a = Article(title="T", summary="S", link="http://x.com")
        assert a.published == ""
        assert a.source == ""
        assert a.tags == []

    def test_with_values(self):
        a = Article(title="T", summary="S", link="http://x.com", source="BBC", tags=["world"])
        assert a.source == "BBC"
        assert a.tags == ["world"]


# ---------------------------------------------------------------------------
# NewsFetcher
# ---------------------------------------------------------------------------

class TestNewsFetcher:
    def test_default_feeds(self):
        fetcher = NewsFetcher()
        assert fetcher.feeds is DEFAULT_FEEDS
        assert fetcher.max_articles == 10

    def test_custom_feeds_and_limit(self):
        feeds = {"Test": "http://test.com/rss"}
        fetcher = NewsFetcher(feeds=feeds, max_articles=3)
        assert fetcher.feeds == feeds
        assert fetcher.max_articles == 3

    @patch("news_analyzer.fetcher.feedparser.parse")
    def test_fetch_feed_returns_articles(self, mock_parse):
        entries = [_make_entry(title=f"Article {i}") for i in range(5)]
        mock_parse.return_value = _make_parsed(entries)

        fetcher = NewsFetcher(max_articles=10)
        articles = fetcher.fetch_feed("Test Feed", "http://test.com/rss")

        assert len(articles) == 5
        assert all(isinstance(a, Article) for a in articles)
        assert articles[0].source == "Test Feed"
        assert articles[0].title == "Article 0"

    @patch("news_analyzer.fetcher.feedparser.parse")
    def test_fetch_feed_respects_max_articles(self, mock_parse):
        entries = [_make_entry(title=f"Article {i}") for i in range(20)]
        mock_parse.return_value = _make_parsed(entries)

        fetcher = NewsFetcher(max_articles=3)
        articles = fetcher.fetch_feed("Feed", "http://test.com/rss")
        assert len(articles) == 3

    @patch("news_analyzer.fetcher.feedparser.parse")
    def test_fetch_feed_tags(self, mock_parse):
        entry = _make_entry(tags=["politics", "world"])
        mock_parse.return_value = _make_parsed([entry])

        fetcher = NewsFetcher()
        articles = fetcher.fetch_feed("Feed", "http://test.com/rss")
        assert articles[0].tags == ["politics", "world"]

    @patch("news_analyzer.fetcher.feedparser.parse")
    def test_fetch_all_combines_feeds(self, mock_parse):
        entries = [_make_entry()]
        mock_parse.return_value = _make_parsed(entries)

        feeds = {"A": "http://a.com/rss", "B": "http://b.com/rss"}
        fetcher = NewsFetcher(feeds=feeds, max_articles=5)
        articles = fetcher.fetch_all()

        # 1 article per feed × 2 feeds
        assert len(articles) == 2
        sources = {a.source for a in articles}
        assert sources == {"A", "B"}

    @patch("news_analyzer.fetcher.feedparser.parse")
    def test_fetch_feed_empty_feed(self, mock_parse):
        mock_parse.return_value = _make_parsed([])
        fetcher = NewsFetcher()
        articles = fetcher.fetch_feed("Empty", "http://empty.com/rss")
        assert articles == []
