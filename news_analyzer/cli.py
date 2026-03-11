"""Command-line interface for the news analyzer."""

import argparse
import sys
from typing import Optional

from .fetcher import NewsFetcher, DEFAULT_FEEDS
from .analyzer import NewsAnalyzer
from .reporter import NewsReporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="news-analyzer",
        description="Fetch news articles from RSS feeds and analyze their sentiment.",
    )
    parser.add_argument(
        "--feeds",
        nargs="+",
        metavar="NAME=URL",
        help=(
            "Custom RSS feeds in NAME=URL format. "
            "If omitted the built-in default feeds are used."
        ),
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=5,
        metavar="N",
        help="Maximum number of articles to fetch per feed (default: 5).",
    )
    parser.add_argument(
        "--keywords",
        type=int,
        default=5,
        metavar="K",
        help="Number of top keywords to extract per article (default: 5).",
    )
    parser.add_argument(
        "--no-colour",
        action="store_true",
        help="Disable ANSI colour output.",
    )
    parser.add_argument(
        "--list-feeds",
        action="store_true",
        help="List the default RSS feeds and exit.",
    )
    return parser


def _parse_feeds(raw: list) -> dict:
    """Parse a list of 'NAME=URL' strings into a dict."""
    feeds = {}
    for item in raw:
        if "=" not in item:
            print(f"Error: feed must be in NAME=URL format, got: {item!r}", file=sys.stderr)
            sys.exit(1)
        name, _, url = item.partition("=")
        feeds[name.strip()] = url.strip()
    return feeds


def main(argv: Optional[list] = None) -> int:
    """Entry point for the CLI.

    Returns:
        Exit code (0 on success, non-zero on error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_feeds:
        print("Default RSS feeds:")
        for name, url in DEFAULT_FEEDS.items():
            print(f"  {name:<20} {url}")
        return 0

    feeds = _parse_feeds(args.feeds) if args.feeds else None

    fetcher = NewsFetcher(feeds=feeds, max_articles=args.max_articles)
    analyzer = NewsAnalyzer(top_keywords=args.keywords)
    reporter = NewsReporter(use_colour=not args.no_colour)

    print("Fetching articles…")
    articles = fetcher.fetch_all()

    if not articles:
        print("No articles retrieved. Check your feed URLs or network connection.")
        return 1

    print(f"Analyzing {len(articles)} article(s)…\n")
    results = analyzer.analyze_all(articles)
    reporter.print_results(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
