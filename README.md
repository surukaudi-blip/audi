# audi — News Analyzer

A Python command-line tool that fetches news articles from RSS feeds and analyzes them for sentiment and keywords.

## Features

- Fetches articles from multiple configurable RSS feeds
- Performs sentiment analysis (positive / negative / neutral) using VADER
- Extracts top keywords per article
- Displays colour-coded terminal output with a summary

## Requirements

- Python 3.8+
- `feedparser`
- `nltk`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Analyze articles from the built-in default feeds
python main.py

# Limit to 3 articles per feed and show 3 keywords
python main.py --max-articles 3 --keywords 3

# Use custom RSS feeds
python main.py --feeds "BBC=https://feeds.bbci.co.uk/news/rss.xml" "NPR=https://feeds.npr.org/1001/rss.xml"

# Disable colour output (useful for piping)
python main.py --no-colour

# List the built-in default feeds
python main.py --list-feeds
```

## Running Tests

```bash
pip install pytest
pytest
```

## Project Structure

```
news_analyzer/
├── __init__.py    # Package exports
├── fetcher.py     # RSS feed fetching (NewsFetcher, Article)
├── analyzer.py    # Sentiment analysis & keyword extraction (NewsAnalyzer)
├── reporter.py    # Terminal output formatting (NewsReporter)
└── cli.py         # Argument parsing and entry point
main.py            # Top-level entry point
tests/             # Unit tests
requirements.txt
```