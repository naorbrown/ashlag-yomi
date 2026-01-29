"""
Baal Hasulam scraper for orhasulam.org.

Scrapes maamarim from the כתבי בעל הסולם (Writings of Baal HaSulam) section.
The site structure is a tree of categories leading to individual maamarim.

Source: https://search.orhasulam.org/
"""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

from src.data.models import Maamar, MaamarCollection, SourceCategory
from src.data.sources.base import (
    BaseScraper,
    clean_hebrew_text,
    generate_maamar_id,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Base URL for Or HaSulam search site
BASE_URL = "https://search.orhasulam.org/"

# The root category for Baal Hasulam's writings
BAAL_HASULAM_SECTION = "כתבי בעל הסולם"


class BaalHasulamScraper(BaseScraper):
    """
    Scraper for Baal Hasulam's writings from orhasulam.org.

    The site has a hierarchical structure:
    - Root categories (כתבי בעל הסולam, etc.)
    - Sub-categories (books like הקדמות, מאמרים, etc.)
    - Individual maamarim (articles)

    Each maamar page contains:
    - Title (Hebrew)
    - Full text content
    - Source book reference
    """

    @property
    def source_category(self) -> SourceCategory:
        return SourceCategory.BAAL_HASULAM

    @property
    def base_url(self) -> str:
        return BASE_URL

    async def get_category_tree(self) -> dict:
        """
        Fetch the category tree structure from the site.

        Returns:
            Dictionary representing the category hierarchy
        """
        html = await self.fetch_html(self.base_url)
        if not html:
            logger.error("failed_to_fetch_category_tree")
            return {}

        soup = self.parse_html(html)

        # Find the navigation/menu structure
        # The exact structure depends on the site's HTML
        # This is a placeholder - actual implementation needs site inspection
        categories = {}

        # Look for links containing Hebrew text related to Baal Hasulam
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            href = link["href"]

            # Filter for relevant sections
            if BAAL_HASULAM_SECTION in text or "בעל הסולם" in text:
                full_url = urljoin(self.base_url, href)
                categories[text] = full_url
                logger.debug("found_category", name=text, url=full_url)

        return categories

    async def get_maamarim_from_category(
        self, category_url: str, book_name: str
    ) -> list[dict]:
        """
        Get list of maamarim from a category page.

        Args:
            category_url: URL of the category page
            book_name: Name of the book/category

        Returns:
            List of dicts with maamar metadata
        """
        html = await self.fetch_html(category_url)
        if not html:
            return []

        soup = self.parse_html(html)
        maamarim = []

        # Find article links - structure depends on site HTML
        # Look for list items or article containers
        for article in soup.find_all(
            ["article", "li", "div"], class_=re.compile(r"article|item|maamar")
        ):
            link = article.find("a", href=True)
            if not link:
                continue

            title = link.get_text(strip=True)
            href = link["href"]
            full_url = urljoin(category_url, href)

            maamarim.append(
                {
                    "title": title,
                    "url": full_url,
                    "book": book_name,
                }
            )

        # Also check for direct links in content area
        content_area = soup.find(
            ["main", "article", "div"], class_=re.compile(r"content|main")
        )
        if content_area:
            for link in content_area.find_all("a", href=True):
                text = link.get_text(strip=True)
                if text and len(text) > 5 and not text.startswith("http"):
                    href = link["href"]
                    full_url = urljoin(category_url, href)
                    if full_url not in [m["url"] for m in maamarim]:
                        maamarim.append(
                            {
                                "title": text,
                                "url": full_url,
                                "book": book_name,
                            }
                        )

        logger.info("found_maamarim", count=len(maamarim), book=book_name)
        return maamarim

    async def scrape_maamar(self, maamar_meta: dict) -> Maamar | None:
        """
        Scrape a single maamar from its URL.

        Args:
            maamar_meta: Dict with title, url, and book

        Returns:
            Maamar object or None if scraping failed
        """
        html = await self.fetch_html(maamar_meta["url"])
        if not html:
            return None

        soup = self.parse_html(html)

        # Extract the main content
        content = soup.find(
            ["article", "div"], class_=re.compile(r"content|text|maamar|article")
        )
        if not content:
            # Try finding the largest text block
            content = soup.find("main") or soup.find("body")

        if not content:
            logger.warning("no_content_found", url=maamar_meta["url"])
            return None

        # Get the text
        text = content.get_text(separator="\n")
        text = clean_hebrew_text(text)

        if len(text) < 50:
            logger.warning(
                "content_too_short", url=maamar_meta["url"], length=len(text)
            )
            return None

        # Try to extract subtitle from the text
        subtitle = None
        lines = text.split("\n", 3)
        if len(lines) >= 2 and len(lines[1]) < 100:
            # Second line might be subtitle
            potential_subtitle = lines[1].strip()
            if potential_subtitle and potential_subtitle != lines[0]:
                subtitle = potential_subtitle
                text = "\n".join([lines[0]] + lines[2:]).strip()

        return Maamar(
            id=generate_maamar_id(
                SourceCategory.BAAL_HASULAM,
                maamar_meta["book"],
                maamar_meta["title"],
            ),
            source=SourceCategory.BAAL_HASULAM,
            title=maamar_meta["title"],
            subtitle=subtitle,
            text=text,
            book=maamar_meta["book"],
            source_url=maamar_meta["url"],
            scraped_at=datetime.utcnow(),
        )

    async def scrape(self) -> MaamarCollection:
        """
        Scrape all maamarim from Baal Hasulam's writings.

        Returns:
            MaamarCollection with all scraped maamarim
        """
        maamarim: list[Maamar] = []

        # Get category tree
        categories = await self.get_category_tree()

        if not categories:
            logger.warning("no_categories_found")
            return MaamarCollection(
                source=SourceCategory.BAAL_HASULAM,
                maamarim=[],
            )

        # Iterate through categories
        for category_name, category_url in categories.items():
            logger.info("scraping_category", name=category_name)

            # Get maamarim list from this category
            maamar_list = await self.get_maamarim_from_category(
                category_url, category_name
            )

            # Scrape each maamar
            for maamar_meta in maamar_list:
                maamar = await self.scrape_maamar(maamar_meta)
                if maamar:
                    maamarim.append(maamar)
                    logger.debug("scraped_maamar", title=maamar.title)

        logger.info("scraping_complete", total_maamarim=len(maamarim))

        return MaamarCollection(
            source=SourceCategory.BAAL_HASULAM,
            maamarim=maamarim,
            last_updated=datetime.utcnow(),
        )


async def scrape_baal_hasulam() -> MaamarCollection:
    """
    Convenience function to scrape Baal Hasulam maamarim.

    Returns:
        MaamarCollection with all scraped maamarim
    """
    async with BaalHasulamScraper() as scraper:
        return await scraper.scrape()
