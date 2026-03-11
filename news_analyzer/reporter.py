"""Formats and prints analysis results to the terminal."""

from typing import List

from .analyzer import AnalysisResult

# ANSI colour codes
_GREEN = "\033[92m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_CYAN = "\033[96m"
_BOLD = "\033[1m"
_RESET = "\033[0m"

_SENTIMENT_COLOUR = {
    "positive": _GREEN,
    "negative": _RED,
    "neutral": _YELLOW,
}


class NewsReporter:
    """Renders AnalysisResult objects as human-readable terminal output."""

    def __init__(self, use_colour: bool = True, width: int = 80):
        """
        Args:
            use_colour: When *False* ANSI codes are omitted (useful for
                piped output or non-ANSI terminals).
            width: Terminal column width used for separator lines.
        """
        self.use_colour = use_colour
        self.width = width

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def print_results(self, results: List[AnalysisResult]) -> None:
        """Print a formatted summary of all analysis results.

        Args:
            results: List of AnalysisResult objects to display.
        """
        if not results:
            print("No articles to display.")
            return

        self._print_header(len(results))
        for i, result in enumerate(results, start=1):
            self._print_article(i, result)
        self._print_summary(results)

    def format_result(self, result: AnalysisResult) -> str:
        """Return a multi-line string representation of a single result.

        Args:
            result: The AnalysisResult to format.

        Returns:
            Formatted string ready for display or logging.
        """
        lines = []
        a = result.article
        lines.append(f"Title    : {a.title}")
        lines.append(f"Source   : {a.source}")
        if a.published:
            lines.append(f"Published: {a.published}")
        lines.append(f"Link     : {a.link}")
        lines.append(
            f"Sentiment: {result.sentiment_label} "
            f"(score: {result.sentiment_score:+.4f})"
        )
        if result.keywords:
            lines.append(f"Keywords : {', '.join(result.keywords)}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _c(self, colour: str, text: str) -> str:
        """Wrap *text* in *colour* if colour output is enabled."""
        if self.use_colour:
            return f"{colour}{text}{_RESET}"
        return text

    def _separator(self, char: str = "-") -> str:
        return char * self.width

    def _print_header(self, count: int) -> None:
        print(self._separator("="))
        print(self._c(_BOLD, f"  NEWS ANALYZER  —  {count} article(s)"))
        print(self._separator("="))

    def _print_article(self, index: int, result: AnalysisResult) -> None:
        a = result.article
        colour = _SENTIMENT_COLOUR.get(result.sentiment_label, _RESET)

        print(f"\n[{index}] {self._c(_BOLD, a.title)}")
        if a.source:
            print(f"    Source   : {a.source}")
        if a.published:
            print(f"    Published: {a.published}")
        if a.link:
            print(f"    Link     : {self._c(_CYAN, a.link)}")

        sentiment_str = (
            f"{result.sentiment_label} (score: {result.sentiment_score:+.4f})"
        )
        print(f"    Sentiment: {self._c(colour, sentiment_str)}")

        if result.keywords:
            print(f"    Keywords : {', '.join(result.keywords)}")

        print(self._separator())

    def _print_summary(self, results: List[AnalysisResult]) -> None:
        total = len(results)
        counts = {"positive": 0, "negative": 0, "neutral": 0}
        for r in results:
            counts[r.sentiment_label] = counts.get(r.sentiment_label, 0) + 1

        avg_score = sum(r.sentiment_score for r in results) / total if total else 0.0

        print(f"\n{self._c(_BOLD, 'SUMMARY')}")
        print(self._separator())
        print(f"  Total articles : {total}")
        print(
            f"  Positive       : "
            f"{self._c(_GREEN, str(counts['positive']))} "
            f"({counts['positive'] / total * 100:.1f}%)"
        )
        print(
            f"  Negative       : "
            f"{self._c(_RED, str(counts['negative']))} "
            f"({counts['negative'] / total * 100:.1f}%)"
        )
        print(
            f"  Neutral        : "
            f"{self._c(_YELLOW, str(counts['neutral']))} "
            f"({counts['neutral'] / total * 100:.1f}%)"
        )
        print(f"  Average score  : {avg_score:+.4f}")
        print(self._separator("="))
