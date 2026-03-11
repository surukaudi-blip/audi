"""Tests for news_analyzer.reporter."""

import io
import sys
import pytest

from news_analyzer.reporter import NewsReporter
from news_analyzer.analyzer import AnalysisResult
from news_analyzer.fetcher import Article


def _make_result(title="Test Article", source="TestFeed", sentiment_label="positive",
                 sentiment_score=0.5, keywords=None, link="http://example.com"):
    article = Article(title=title, summary="A summary.", link=link, source=source)
    return AnalysisResult(
        article=article,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score,
        keywords=keywords or ["python", "news"],
        top_keyword="python",
    )


class TestNewsReporter:
    def setup_method(self):
        self.reporter = NewsReporter(use_colour=False, width=40)

    def _capture(self, results):
        """Capture stdout while printing results."""
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            self.reporter.print_results(results)
        finally:
            sys.stdout = old
        return buf.getvalue()

    def test_no_articles_message(self):
        output = self._capture([])
        assert "No articles" in output

    def test_article_title_appears(self):
        result = _make_result(title="Breaking News Today")
        output = self._capture([result])
        assert "Breaking News Today" in output

    def test_source_appears(self):
        result = _make_result(source="Reuters")
        output = self._capture([result])
        assert "Reuters" in output

    def test_sentiment_label_appears(self):
        result = _make_result(sentiment_label="positive")
        output = self._capture([result])
        assert "positive" in output

    def test_keywords_appear(self):
        result = _make_result(keywords=["economy", "growth"])
        output = self._capture([result])
        assert "economy" in output
        assert "growth" in output

    def test_summary_section_present(self):
        results = [_make_result(), _make_result(sentiment_label="negative", sentiment_score=-0.3)]
        output = self._capture(results)
        assert "SUMMARY" in output

    def test_summary_counts(self):
        results = [
            _make_result(sentiment_label="positive", sentiment_score=0.5),
            _make_result(sentiment_label="negative", sentiment_score=-0.5),
            _make_result(sentiment_label="neutral", sentiment_score=0.0),
        ]
        output = self._capture(results)
        assert "Total articles" in output

    def test_format_result_no_colour(self):
        result = _make_result(title="Climate Change Report", source="BBC")
        text = self.reporter.format_result(result)
        assert "Climate Change Report" in text
        assert "BBC" in text
        assert "positive" in text
        assert "\033[" not in text  # no ANSI codes

    def test_format_result_with_colour(self):
        reporter = NewsReporter(use_colour=True)
        result = _make_result(sentiment_label="positive")
        text = reporter.format_result(result)
        assert "positive" in text

    def test_multiple_articles_all_shown(self):
        results = [_make_result(title=f"Article {i}") for i in range(3)]
        output = self._capture(results)
        for i in range(3):
            assert f"Article {i}" in output
