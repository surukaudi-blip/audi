"""Tests for news_analyzer.cli."""

import sys
import pytest
from unittest.mock import patch, MagicMock

from news_analyzer.cli import main, build_parser, _parse_feeds
from news_analyzer.fetcher import Article
from news_analyzer.analyzer import AnalysisResult


def _dummy_article(title="Test"):
    return Article(title=title, summary="Summary.", link="http://example.com", source="Feed")


def _dummy_result(title="Test", label="neutral", score=0.0):
    return AnalysisResult(
        article=_dummy_article(title),
        sentiment_label=label,
        sentiment_score=score,
        keywords=["test"],
        top_keyword="test",
    )


class TestBuildParser:
    def test_defaults(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.max_articles == 5
        assert args.keywords == 5
        assert not args.no_colour
        assert not args.list_feeds
        assert args.feeds is None


class TestParseFeeds:
    def test_valid_feed(self):
        feeds = _parse_feeds(["BBC=http://bbc.com/rss"])
        assert feeds == {"BBC": "http://bbc.com/rss"}

    def test_multiple_feeds(self):
        feeds = _parse_feeds(["A=http://a.com", "B=http://b.com"])
        assert len(feeds) == 2

    def test_invalid_feed_exits(self):
        with pytest.raises(SystemExit):
            _parse_feeds(["no-equals-sign"])


class TestMain:
    @patch("news_analyzer.cli.NewsFetcher")
    @patch("news_analyzer.cli.NewsAnalyzer")
    @patch("news_analyzer.cli.NewsReporter")
    def test_successful_run(self, MockReporter, MockAnalyzer, MockFetcher, capsys):
        articles = [_dummy_article()]
        results = [_dummy_result()]

        MockFetcher.return_value.fetch_all.return_value = articles
        MockAnalyzer.return_value.analyze_all.return_value = results
        reporter_instance = MagicMock()
        MockReporter.return_value = reporter_instance

        exit_code = main([])
        assert exit_code == 0
        reporter_instance.print_results.assert_called_once_with(results)

    @patch("news_analyzer.cli.NewsFetcher")
    def test_no_articles_returns_error(self, MockFetcher, capsys):
        MockFetcher.return_value.fetch_all.return_value = []
        exit_code = main([])
        assert exit_code == 1
        out = capsys.readouterr().out
        assert "No articles" in out

    def test_list_feeds(self, capsys):
        exit_code = main(["--list-feeds"])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "BBC" in out or "Reuters" in out

    @patch("news_analyzer.cli.NewsFetcher")
    @patch("news_analyzer.cli.NewsAnalyzer")
    @patch("news_analyzer.cli.NewsReporter")
    def test_no_colour_flag(self, MockReporter, MockAnalyzer, MockFetcher):
        MockFetcher.return_value.fetch_all.return_value = [_dummy_article()]
        MockAnalyzer.return_value.analyze_all.return_value = [_dummy_result()]
        MockReporter.return_value = MagicMock()

        main(["--no-colour"])
        MockReporter.assert_called_once_with(use_colour=False)

    @patch("news_analyzer.cli.NewsFetcher")
    @patch("news_analyzer.cli.NewsAnalyzer")
    @patch("news_analyzer.cli.NewsReporter")
    def test_custom_max_articles(self, MockReporter, MockAnalyzer, MockFetcher):
        MockFetcher.return_value.fetch_all.return_value = [_dummy_article()]
        MockAnalyzer.return_value.analyze_all.return_value = [_dummy_result()]
        MockReporter.return_value = MagicMock()

        main(["--max-articles", "3"])
        call_kwargs = MockFetcher.call_args[1]
        assert call_kwargs["max_articles"] == 3
