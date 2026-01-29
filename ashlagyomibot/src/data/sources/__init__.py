"""Data sources for maamarim - web scrapers and PDF extraction."""

from src.data.sources.baal_hasulam import BaalHasulamScraper, scrape_baal_hasulam
from src.data.sources.base import BaseScraper, clean_hebrew_text, generate_maamar_id
from src.data.sources.pdf_utils import (
    PDFArticle,
    PDFPage,
    clean_pdf_text,
    extract_text_from_bytes,
    extract_text_from_pdf,
    merge_pages_text,
    split_into_articles,
)
from src.data.sources.rabash import RabashScraper, scrape_rabash

__all__ = [
    # Base classes
    "BaseScraper",
    "clean_hebrew_text",
    "generate_maamar_id",
    # PDF utilities
    "PDFArticle",
    "PDFPage",
    "clean_pdf_text",
    "extract_text_from_bytes",
    "extract_text_from_pdf",
    "merge_pages_text",
    "split_into_articles",
    # Scrapers
    "BaalHasulamScraper",
    "scrape_baal_hasulam",
    "RabashScraper",
    "scrape_rabash",
]
