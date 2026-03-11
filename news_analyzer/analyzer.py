"""Analyzes news articles for sentiment and keywords."""

import re
import string
from dataclasses import dataclass, field
from typing import List, Tuple

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from .fetcher import Article

# Ensure required NLTK data is available
_NLTK_PATHS = {
    "vader_lexicon": "sentiment/vader_lexicon",
    "punkt": "tokenizers/punkt",
    "punkt_tab": "tokenizers/punkt_tab",
    "stopwords": "corpora/stopwords",
}
for _resource, _path in _NLTK_PATHS.items():
    try:
        nltk.data.find(_path)
    except LookupError:
        nltk.download(_resource, quiet=True)


@dataclass
class AnalysisResult:
    """Holds the analysis output for a single article."""

    article: Article
    sentiment_label: str  # "positive", "negative", or "neutral"
    sentiment_score: float  # compound VADER score in [-1, 1]
    keywords: List[str] = field(default_factory=list)
    top_keyword: str = ""


class NewsAnalyzer:
    """Performs sentiment analysis and keyword extraction on articles."""

    def __init__(self, top_keywords: int = 5):
        """
        Initialize the analyzer.

        Args:
            top_keywords: Number of top keywords to extract per article.
        """
        self.top_keywords = top_keywords
        self._sia = SentimentIntensityAnalyzer()
        self._stop_words = set(stopwords.words("english"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, article: Article) -> AnalysisResult:
        """Analyze a single article.

        Args:
            article: The article to analyze.

        Returns:
            An AnalysisResult with sentiment and keyword data.
        """
        text = f"{article.title}. {article.summary}"
        scores = self._sia.polarity_scores(text)
        compound = scores["compound"]
        label = self._sentiment_label(compound)
        keywords = self._extract_keywords(text)
        return AnalysisResult(
            article=article,
            sentiment_label=label,
            sentiment_score=round(compound, 4),
            keywords=keywords,
            top_keyword=keywords[0] if keywords else "",
        )

    def analyze_all(self, articles: List[Article]) -> List[AnalysisResult]:
        """Analyze a list of articles.

        Args:
            articles: Articles to analyze.

        Returns:
            List of AnalysisResult objects in the same order.
        """
        return [self.analyze(a) for a in articles]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sentiment_label(compound: float) -> str:
        """Map a compound VADER score to a human-readable label."""
        if compound >= 0.05:
            return "positive"
        if compound <= -0.05:
            return "negative"
        return "neutral"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract the most frequent meaningful words from *text*.

        Returns up to ``self.top_keywords`` words, sorted by frequency
        (descending) with ties broken alphabetically.
        """
        # Strip HTML tags that may appear in RSS summaries
        clean = re.sub(r"<[^>]+>", " ", text)
        tokens = word_tokenize(clean.lower())
        # Keep only alphabetic tokens that are not stop words
        words = [
            w
            for w in tokens
            if w.isalpha() and w not in self._stop_words and len(w) > 2
        ]
        freq: dict = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        ranked: List[Tuple[str, int]] = sorted(
            freq.items(), key=lambda x: (-x[1], x[0])
        )
        return [w for w, _ in ranked[: self.top_keywords]]
