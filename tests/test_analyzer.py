"""Tests for news_analyzer.analyzer."""

import pytest

from news_analyzer.analyzer import NewsAnalyzer, AnalysisResult
from news_analyzer.fetcher import Article


def _article(title="", summary="", source="Test"):
    return Article(title=title, summary=summary, link="http://example.com", source=source)


class TestSentimentLabel:
    def test_positive(self):
        assert NewsAnalyzer._sentiment_label(0.5) == "positive"

    def test_negative(self):
        assert NewsAnalyzer._sentiment_label(-0.5) == "negative"

    def test_neutral_zero(self):
        assert NewsAnalyzer._sentiment_label(0.0) == "neutral"

    def test_neutral_borderline_positive(self):
        assert NewsAnalyzer._sentiment_label(0.04) == "neutral"

    def test_neutral_borderline_negative(self):
        assert NewsAnalyzer._sentiment_label(-0.04) == "neutral"

    def test_boundary_positive(self):
        assert NewsAnalyzer._sentiment_label(0.05) == "positive"

    def test_boundary_negative(self):
        assert NewsAnalyzer._sentiment_label(-0.05) == "negative"


class TestKeywordExtraction:
    def setup_method(self):
        self.analyzer = NewsAnalyzer(top_keywords=5)

    def test_returns_list(self):
        keywords = self.analyzer._extract_keywords("Python programming language tutorial")
        assert isinstance(keywords, list)

    def test_strips_stopwords(self):
        keywords = self.analyzer._extract_keywords("the quick brown fox jumps over the lazy dog")
        for word in keywords:
            assert word not in self.analyzer._stop_words

    def test_strips_html(self):
        keywords = self.analyzer._extract_keywords("<p>Python programming</p>")
        assert "p" not in keywords  # HTML tag stripped

    def test_top_keywords_limit(self):
        analyzer = NewsAnalyzer(top_keywords=3)
        text = "apple banana cherry date elderberry fig grape"
        keywords = analyzer._extract_keywords(text)
        assert len(keywords) <= 3

    def test_most_frequent_first(self):
        text = "python python python java java ruby"
        keywords = self.analyzer._extract_keywords(text)
        assert keywords[0] == "python"

    def test_empty_text(self):
        keywords = self.analyzer._extract_keywords("")
        assert keywords == []


class TestAnalyze:
    def setup_method(self):
        self.analyzer = NewsAnalyzer(top_keywords=5)

    def test_returns_analysis_result(self):
        article = _article(title="Happy day", summary="Everything is wonderful today.")
        result = self.analyzer.analyze(article)
        assert isinstance(result, AnalysisResult)

    def test_positive_sentiment(self):
        article = _article(title="Great news", summary="Wonderful, amazing, fantastic achievements celebrated.")
        result = self.analyzer.analyze(article)
        assert result.sentiment_label == "positive"
        assert result.sentiment_score > 0

    def test_negative_sentiment(self):
        article = _article(title="Terrible disaster", summary="Horrific tragedy strikes causing widespread grief and suffering.")
        result = self.analyzer.analyze(article)
        assert result.sentiment_label == "negative"
        assert result.sentiment_score < 0

    def test_score_in_range(self):
        article = _article(title="Some news", summary="Things happened today.")
        result = self.analyzer.analyze(article)
        assert -1.0 <= result.sentiment_score <= 1.0

    def test_article_preserved(self):
        article = _article(title="Test", summary="Content here.")
        result = self.analyzer.analyze(article)
        assert result.article is article

    def test_top_keyword_matches_first_keyword(self):
        article = _article(title="Python Python programming", summary="Python is great.")
        result = self.analyzer.analyze(article)
        if result.keywords:
            assert result.top_keyword == result.keywords[0]

    def test_empty_article(self):
        article = _article(title="", summary="")
        result = self.analyzer.analyze(article)
        assert isinstance(result, AnalysisResult)
        assert result.sentiment_label in ("positive", "negative", "neutral")


class TestAnalyzeAll:
    def setup_method(self):
        self.analyzer = NewsAnalyzer()

    def test_analyze_all_returns_list(self):
        articles = [
            _article(title="Good news", summary="Everything is great."),
            _article(title="Bad news", summary="Terrible things happened."),
        ]
        results = self.analyzer.analyze_all(articles)
        assert len(results) == 2
        assert all(isinstance(r, AnalysisResult) for r in results)

    def test_analyze_all_empty(self):
        results = self.analyzer.analyze_all([])
        assert results == []

    def test_analyze_all_preserves_order(self):
        articles = [_article(title=str(i)) for i in range(5)]
        results = self.analyzer.analyze_all(articles)
        for i, r in enumerate(results):
            assert r.article.title == str(i)
