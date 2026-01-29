"""
Base scraper class for Ashlag Yomi maamarim sources.

Provides common functionality for web scraping and data extraction:
- HTTP client with retry logic and rate limiting
- HTML parsing utilities
- Error handling and logging
- Common scraping patterns
"""

from __future__ import annotations

import asyncio
import random
from abc import ABC, abstractmethod
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from src.data.models import MaamarCollection, SourceCategory
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Default headers to mimic a browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "he,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


class BaseScraper(ABC):
    """
    Abstract base class for maamarim scrapers.

    Subclasses must implement:
    - source_category: The SourceCategory this scraper handles
    - scrape(): Main scraping method that returns a MaamarCollection
    """

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
    ) -> None:
        """
        Initialize the scraper.

        Args:
            timeout: HTTP request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            min_delay: Minimum delay between requests (rate limiting)
            max_delay: Maximum delay between requests (randomized)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._client: httpx.AsyncClient | None = None

    @property
    @abstractmethod
    def source_category(self) -> SourceCategory:
        """The source category this scraper handles."""
        ...

    @property
    @abstractmethod
    def base_url(self) -> str:
        """The base URL for this source."""
        ...

    async def __aenter__(self) -> BaseScraper:
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            headers=DEFAULT_HEADERS,
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, ensuring it's initialized."""
        if self._client is None:
            raise RuntimeError("Scraper must be used as async context manager")
        return self._client

    async def _rate_limit_delay(self) -> None:
        """Apply randomized rate limiting delay between requests."""
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)

    async def fetch_html(self, url: str) -> str | None:
        """
        Fetch HTML content from a URL with retries.

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string, or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                await self._rate_limit_delay()
                response = await self.client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "http_error",
                    url=url,
                    status_code=e.response.status_code,
                    attempt=attempt + 1,
                )
                if e.response.status_code == 404:
                    return None
            except httpx.RequestError as e:
                logger.warning(
                    "request_error",
                    url=url,
                    error=str(e),
                    attempt=attempt + 1,
                )

            # Exponential backoff
            if attempt < self.max_retries - 1:
                backoff = 2**attempt
                await asyncio.sleep(backoff)

        logger.error("fetch_failed", url=url, max_retries=self.max_retries)
        return None

    async def fetch_bytes(self, url: str) -> bytes | None:
        """
        Fetch binary content from a URL with retries.

        Useful for downloading PDFs.

        Args:
            url: The URL to fetch

        Returns:
            Binary content, or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                await self._rate_limit_delay()
                response = await self.client.get(url)
                response.raise_for_status()
                return response.content
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "http_error",
                    url=url,
                    status_code=e.response.status_code,
                    attempt=attempt + 1,
                )
                if e.response.status_code == 404:
                    return None
            except httpx.RequestError as e:
                logger.warning(
                    "request_error",
                    url=url,
                    error=str(e),
                    attempt=attempt + 1,
                )

            # Exponential backoff
            if attempt < self.max_retries - 1:
                backoff = 2**attempt
                await asyncio.sleep(backoff)

        logger.error("fetch_failed", url=url, max_retries=self.max_retries)
        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content into a BeautifulSoup object.

        Args:
            html: HTML content as string

        Returns:
            Parsed BeautifulSoup object
        """
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    async def scrape(self) -> MaamarCollection:
        """
        Scrape all maamarim from this source.

        Returns:
            MaamarCollection containing all scraped maamarim
        """
        ...

    async def save_to_json(self, output_path: Path) -> None:
        """
        Scrape and save collection to JSON file.

        Args:
            output_path: Path to save the JSON file
        """
        collection = await self.scrape()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(collection.model_dump_json(indent=2))
        logger.info(
            "collection_saved",
            path=str(output_path),
            count=collection.count,
        )


def clean_hebrew_text(text: str) -> str:
    """
    Clean and normalize Hebrew text.

    - Remove excessive whitespace
    - Normalize line breaks
    - Remove control characters
    - Preserve Hebrew punctuation
    """
    import re

    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # Normalize whitespace (preserve single newlines for paragraphs)
    text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs to single space
    text = re.sub(r"\n[ \t]+", "\n", text)  # Remove leading whitespace after newlines
    text = re.sub(r"[ \t]+\n", "\n", text)  # Remove trailing whitespace before newlines
    text = re.sub(r"\n{3,}", "\n\n", text)  # Multiple newlines to double newline

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def generate_maamar_id(
    source: SourceCategory,
    book: str,
    title: str,
    index: int = 0,
) -> str:
    """
    Generate a unique ID for a maamar.

    Format: {source}_{book_slug}_{title_slug}_{index}

    Args:
        source: Source category
        book: Book name
        title: Article title
        index: Optional index for disambiguation

    Returns:
        Unique maamar ID
    """
    import re

    def slugify(text: str) -> str:
        # Remove non-alphanumeric characters (keep Hebrew)
        text = re.sub(r"[^\w\s\u0590-\u05FF]", "", text)
        # Replace spaces with underscores
        text = re.sub(r"\s+", "_", text)
        # Truncate to reasonable length
        return text[:50].strip("_")

    book_slug = slugify(book)
    title_slug = slugify(title)

    parts = [source.value, book_slug, title_slug]
    if index > 0:
        parts.append(str(index))

    return "_".join(filter(None, parts))
