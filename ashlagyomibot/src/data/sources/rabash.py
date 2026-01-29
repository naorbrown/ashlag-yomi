"""
Rabash PDF scraper for ashlagbaroch.org.

Scrapes and extracts text from PDF maamarim of Rabbi Baruch Shalom Ashlag (Rabash).
The site provides downloadable PDFs of his writings.

Source: https://ashlagbaroch.org/rbsMore/
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

from src.data.models import Maamar, MaamarCollection, SourceCategory
from src.data.sources.base import (
    BaseScraper,
    clean_hebrew_text,
    generate_maamar_id,
)
from src.data.sources.pdf_utils import (
    extract_text_from_bytes,
    split_into_articles,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Base URL for Rabash materials
BASE_URL = "https://ashlagbaroch.org/rbsMore/"


class RabashScraper(BaseScraper):
    """
    Scraper for Rabash's writings from ashlagbaroch.org.

    The site has PDF files that can be downloaded and processed.
    Each PDF may contain multiple maamarim that need to be split.
    """

    def __init__(
        self,
        *,
        pdf_cache_dir: Path | None = None,
        **kwargs,
    ) -> None:
        """
        Initialize the Rabash scraper.

        Args:
            pdf_cache_dir: Optional directory to cache downloaded PDFs
            **kwargs: Additional arguments for BaseScraper
        """
        super().__init__(**kwargs)
        self.pdf_cache_dir = pdf_cache_dir

    @property
    def source_category(self) -> SourceCategory:
        return SourceCategory.RABASH

    @property
    def base_url(self) -> str:
        return BASE_URL

    async def get_pdf_list(self) -> list[dict]:
        """
        Get list of available PDF files from the site.

        Returns:
            List of dicts with PDF metadata (name, url, book)
        """
        html = await self.fetch_html(self.base_url)
        if not html:
            logger.error("failed_to_fetch_pdf_list")
            return []

        soup = self.parse_html(html)
        pdfs = []

        # Find all PDF links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.lower().endswith(".pdf"):
                # Get the display text as the book name
                text = link.get_text(strip=True)
                if not text:
                    # Use filename if no text
                    text = href.split("/")[-1].replace(".pdf", "")

                full_url = urljoin(self.base_url, href)
                filename = href.split("/")[-1]

                pdfs.append(
                    {
                        "name": text,
                        "url": full_url,
                        "filename": filename,
                        "book": self._extract_book_name(text, filename),
                    }
                )

        # Also look for links in list items or divs with PDF icons
        for container in soup.find_all(["li", "div", "p"]):
            links = container.find_all("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
            for link in links:
                href = link["href"]
                text = container.get_text(strip=True)
                full_url = urljoin(self.base_url, href)
                filename = href.split("/")[-1]

                # Avoid duplicates
                if full_url not in [p["url"] for p in pdfs]:
                    pdfs.append(
                        {
                            "name": (
                                text[:100] if text else filename.replace(".pdf", "")
                            ),
                            "url": full_url,
                            "filename": filename,
                            "book": self._extract_book_name(text, filename),
                        }
                    )

        logger.info("found_pdfs", count=len(pdfs))
        return pdfs

    def _extract_book_name(self, text: str, filename: str) -> str:
        """
        Extract a clean book name from text or filename.

        Args:
            text: Display text
            filename: PDF filename

        Returns:
            Clean book name
        """
        # Try to extract from text first
        if text:
            # Common patterns for book names
            # Remove common prefixes/suffixes
            cleaned = re.sub(r"(להורדה|PDF|קובץ|הורד)", "", text, flags=re.IGNORECASE)
            cleaned = cleaned.strip(" -–—")
            if cleaned:
                return cleaned

        # Fall back to filename
        name = filename.replace(".pdf", "").replace("_", " ").replace("-", " ")
        return name.strip()

    async def download_and_extract_pdf(self, pdf_meta: dict) -> list[Maamar]:
        """
        Download a PDF and extract maamarim from it.

        Args:
            pdf_meta: Dict with PDF metadata (url, name, book, filename)

        Returns:
            List of Maamar objects extracted from the PDF
        """
        maamarim = []

        # Check cache first
        if self.pdf_cache_dir:
            cache_path = self.pdf_cache_dir / pdf_meta["filename"]
            if cache_path.exists():
                logger.debug("using_cached_pdf", filename=pdf_meta["filename"])
                with open(cache_path, "rb") as f:
                    pdf_bytes = f.read()
            else:
                pdf_bytes = await self.fetch_bytes(pdf_meta["url"])
                if pdf_bytes:
                    self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)
                    with open(cache_path, "wb") as f:
                        f.write(pdf_bytes)
        else:
            pdf_bytes = await self.fetch_bytes(pdf_meta["url"])

        if not pdf_bytes:
            logger.warning("failed_to_download_pdf", url=pdf_meta["url"])
            return []

        try:
            # Extract text from PDF
            pages = extract_text_from_bytes(pdf_bytes, pdf_meta["filename"])

            if not pages:
                logger.warning("no_text_extracted", filename=pdf_meta["filename"])
                return []

            # Try to split into individual articles
            articles = split_into_articles(pages)

            for i, article in enumerate(articles):
                if not article.text or len(article.text) < 50:
                    continue

                maamar = Maamar(
                    id=generate_maamar_id(
                        SourceCategory.RABASH,
                        pdf_meta["book"],
                        article.title,
                        index=i,
                    ),
                    source=SourceCategory.RABASH,
                    title=article.title,
                    subtitle=article.subtitle,
                    text=clean_hebrew_text(article.text),
                    book=pdf_meta["book"],
                    page=article.page_range,
                    source_url=pdf_meta["url"],
                    pdf_filename=pdf_meta["filename"],
                    pdf_start_page=article.start_page,
                    pdf_end_page=article.end_page,
                    scraped_at=datetime.utcnow(),
                )
                maamarim.append(maamar)

            logger.info(
                "extracted_maamarim",
                filename=pdf_meta["filename"],
                count=len(maamarim),
            )

        except Exception as e:
            logger.error(
                "pdf_extraction_failed",
                filename=pdf_meta["filename"],
                error=str(e),
            )

        return maamarim

    async def scrape(self) -> MaamarCollection:
        """
        Scrape all maamarim from Rabash PDFs.

        Returns:
            MaamarCollection with all scraped maamarim
        """
        all_maamarim: list[Maamar] = []

        # Get list of available PDFs
        pdfs = await self.get_pdf_list()

        if not pdfs:
            logger.warning("no_pdfs_found")
            return MaamarCollection(
                source=SourceCategory.RABASH,
                maamarim=[],
            )

        # Process each PDF
        for pdf_meta in pdfs:
            logger.info("processing_pdf", name=pdf_meta["name"])
            maamarim = await self.download_and_extract_pdf(pdf_meta)
            all_maamarim.extend(maamarim)

        logger.info("scraping_complete", total_maamarim=len(all_maamarim))

        return MaamarCollection(
            source=SourceCategory.RABASH,
            maamarim=all_maamarim,
            last_updated=datetime.utcnow(),
        )


async def scrape_rabash(pdf_cache_dir: Path | None = None) -> MaamarCollection:
    """
    Convenience function to scrape Rabash maamarim.

    Args:
        pdf_cache_dir: Optional directory to cache downloaded PDFs

    Returns:
        MaamarCollection with all scraped maamarim
    """
    async with RabashScraper(pdf_cache_dir=pdf_cache_dir) as scraper:
        return await scraper.scrape()
