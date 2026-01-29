"""
PDF text extraction utilities for Ashlag Yomi.

Uses PyMuPDF (fitz) to extract text from Hebrew PDFs.
Handles RTL text, Hebrew fonts, and common PDF formatting issues.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PDFPage:
    """Represents extracted content from a single PDF page."""

    page_number: int
    text: str
    word_count: int


@dataclass
class PDFArticle:
    """Represents an article extracted from a PDF."""

    title: str
    subtitle: str | None
    text: str
    start_page: int
    end_page: int

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    @property
    def page_range(self) -> str:
        if self.start_page == self.end_page:
            return str(self.start_page)
        return f"{self.start_page}-{self.end_page}"


def extract_text_from_pdf(pdf_path: Path | str) -> list[PDFPage]:
    """
    Extract text from all pages of a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of PDFPage objects containing extracted text
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = []
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text")
                text = clean_pdf_text(text)
                pages.append(
                    PDFPage(
                        page_number=page_num,
                        text=text,
                        word_count=len(text.split()),
                    )
                )
        logger.debug(
            "pdf_extracted",
            path=str(pdf_path),
            pages=len(pages),
            total_words=sum(p.word_count for p in pages),
        )
    except Exception as e:
        logger.error("pdf_extraction_failed", path=str(pdf_path), error=str(e))
        raise

    return pages


def extract_text_from_bytes(
    pdf_bytes: bytes, filename: str = "unknown.pdf"
) -> list[PDFPage]:
    """
    Extract text from PDF bytes (for in-memory processing).

    Args:
        pdf_bytes: PDF content as bytes
        filename: Optional filename for logging

    Returns:
        List of PDFPage objects containing extracted text
    """
    pages = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text")
                text = clean_pdf_text(text)
                pages.append(
                    PDFPage(
                        page_number=page_num,
                        text=text,
                        word_count=len(text.split()),
                    )
                )
        logger.debug(
            "pdf_extracted",
            filename=filename,
            pages=len(pages),
            total_words=sum(p.word_count for p in pages),
        )
    except Exception as e:
        logger.error("pdf_extraction_failed", filename=filename, error=str(e))
        raise

    return pages


def clean_pdf_text(text: str) -> str:
    """
    Clean and normalize text extracted from PDFs.

    Handles common PDF extraction issues:
    - Excessive whitespace
    - Page numbers and headers
    - Broken lines
    - Hebrew punctuation normalization
    """
    # Remove control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # Remove common PDF artifacts (page numbers, headers)
    # Pattern for standalone numbers (likely page numbers)
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)

    # Normalize Hebrew quotation marks
    text = text.replace("״", '"')
    text = text.replace("׳", "'")

    # Normalize whitespace while preserving paragraph structure
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        # Strip whitespace from line
        line = line.strip()
        # Skip empty lines (will be handled by paragraph logic)
        if line:
            cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1] != "":
            # Preserve paragraph breaks (empty line after content)
            cleaned_lines.append("")

    text = "\n".join(cleaned_lines)

    # Final cleanup
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def split_into_articles(
    pages: list[PDFPage],
    title_pattern: str | None = None,
) -> list[PDFArticle]:
    """
    Split PDF pages into individual articles based on title patterns.

    Args:
        pages: List of PDFPage objects
        title_pattern: Regex pattern to identify article titles
                      Default: Hebrew text followed by digits (מאמר א׳, etc.)

    Returns:
        List of PDFArticle objects
    """
    if not pages:
        return []

    # Default pattern for Hebrew article titles
    if title_pattern is None:
        # Match common Hebrew article header patterns:
        # - מאמר (article) followed by Hebrew numerals
        # - Lines that are mostly bold/large (appear at start of line, short)
        title_pattern = r"^(מאמר\s+[א-ת]{1,3}[\׳\']?|שיעור\s+[א-ת]{1,3}[\׳\']?)"

    pattern = re.compile(title_pattern, re.MULTILINE)

    # Combine all pages into single text with page markers
    full_text = ""
    page_positions: list[tuple[int, int]] = []  # (start_pos, page_num)

    for page in pages:
        page_positions.append((len(full_text), page.page_number))
        full_text += page.text + "\n\n"

    # Find all article boundaries
    matches = list(pattern.finditer(full_text))

    if not matches:
        # No articles found, return entire PDF as single article
        return [
            PDFArticle(
                title="מאמר",
                subtitle=None,
                text=full_text.strip(),
                start_page=pages[0].page_number if pages else 1,
                end_page=pages[-1].page_number if pages else 1,
            )
        ]

    articles = []
    for i, match in enumerate(matches):
        start_pos = match.start()
        # End position is start of next article or end of document
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)

        article_text = full_text[start_pos:end_pos].strip()

        # Extract title (first line)
        lines = article_text.split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        # Try to extract subtitle (second line if short)
        subtitle = None
        body_lines = body.split("\n", 1)
        if body_lines and len(body_lines[0]) < 100:
            first_line = body_lines[0].strip()
            # Check if it looks like a subtitle (not starting with common body text)
            if first_line and first_line[0] not in "אבגדהוזחטיכלמנסעפצקרשת":
                # Probably not a subtitle if starts with common letter
                pass
            elif first_line and len(first_line) < 80:
                subtitle = first_line
                body = body_lines[1] if len(body_lines) > 1 else ""

        # Determine page range
        start_page = 1
        end_page = 1
        for pos, page_num in page_positions:
            if pos <= start_pos:
                start_page = page_num
            if pos <= end_pos:
                end_page = page_num

        articles.append(
            PDFArticle(
                title=title,
                subtitle=subtitle,
                text=body.strip(),
                start_page=start_page,
                end_page=end_page,
            )
        )

    logger.info("articles_split", count=len(articles))
    return articles


def merge_pages_text(pages: list[PDFPage]) -> str:
    """
    Merge all pages into a single text string.

    Args:
        pages: List of PDFPage objects

    Returns:
        Combined text from all pages
    """
    return "\n\n".join(page.text for page in pages if page.text)


def iter_pdf_pages(pdf_path: Path | str) -> Iterator[PDFPage]:
    """
    Iterate over PDF pages lazily (memory efficient for large PDFs).

    Args:
        pdf_path: Path to the PDF file

    Yields:
        PDFPage objects one at a time
    """
    pdf_path = Path(pdf_path)
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            text = clean_pdf_text(text)
            yield PDFPage(
                page_number=page_num,
                text=text,
                word_count=len(text.split()),
            )
