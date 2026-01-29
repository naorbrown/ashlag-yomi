#!/usr/bin/env python3
"""
Scrape maamarim from Baal Hasulam and Rabash sources.

This script fetches content from:
- Baal Hasulam: https://search.orhasulam.org/ (כתבי בעל הסולם)
- Rabash: https://ashlagbaroch.org/rbsMore/ (PDFs)

The scraped content is saved as JSON cache files in data/maamarim/

Usage:
    # Scrape all sources
    python scripts/scrape_maamarim.py

    # Scrape specific source
    python scripts/scrape_maamarim.py --source baal_hasulam
    python scripts/scrape_maamarim.py --source rabash

    # Use custom output directory
    python scripts/scrape_maamarim.py --output-dir /path/to/output

    # Enable PDF caching
    python scripts/scrape_maamarim.py --cache-pdfs
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.data.models import MaamarCollection, SourceCategory
from src.data.sources.baal_hasulam import scrape_baal_hasulam
from src.data.sources.rabash import scrape_rabash
from src.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


async def scrape_source(
    source: SourceCategory,
    output_dir: Path,
    pdf_cache_dir: Path | None = None,
) -> MaamarCollection | None:
    """
    Scrape a single source and save the results.

    Args:
        source: The source category to scrape
        output_dir: Directory to save the JSON cache
        pdf_cache_dir: Optional directory to cache downloaded PDFs

    Returns:
        The scraped MaamarCollection, or None if scraping failed
    """
    logger.info("scraping_source", source=source.value)

    try:
        if source == SourceCategory.BAAL_HASULAM:
            collection = await scrape_baal_hasulam()
        elif source == SourceCategory.RABASH:
            collection = await scrape_rabash(pdf_cache_dir=pdf_cache_dir)
        else:
            logger.error("unknown_source", source=source.value)
            return None

        if not collection.maamarim:
            logger.warning("no_maamarim_scraped", source=source.value)
            return collection

        # Save to JSON file
        output_file = output_dir / f"{source.value}.json"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(collection.model_dump_json(indent=2))

        logger.info(
            "source_scraped",
            source=source.value,
            maamarim_count=len(collection.maamarim),
            output_file=str(output_file),
        )

        return collection

    except Exception as e:
        logger.error(
            "scraping_failed",
            source=source.value,
            error=str(e),
        )
        return None


async def scrape_all(
    output_dir: Path,
    pdf_cache_dir: Path | None = None,
) -> dict[SourceCategory, MaamarCollection]:
    """
    Scrape all sources.

    Args:
        output_dir: Directory to save the JSON cache files
        pdf_cache_dir: Optional directory to cache downloaded PDFs

    Returns:
        Dict mapping source categories to their collections
    """
    results: dict[SourceCategory, MaamarCollection] = {}

    for source in SourceCategory:
        collection = await scrape_source(source, output_dir, pdf_cache_dir)
        if collection:
            results[source] = collection

    return results


def create_sample_maamarim(output_dir: Path) -> None:
    """
    Create sample maamarim JSON files for testing.

    This is useful when the actual websites are unavailable.
    """
    from src.data.models import Maamar

    # Sample Baal Hasulam maamar
    baal_hasulam_maamar = Maamar(
        id="baal_hasulam_sample_1",
        source=SourceCategory.BAAL_HASULAM,
        title="מהות חכמת הקבלה",
        subtitle="הקדמה לחכמת הקבלה",
        text="""חכמת הקבלה היא בעצם חכמת הקבלה של האור העליון.

כי כל מה שאנו משיגים, הוא רק האור העליון הנמשך מאין סוף ומתפשט בנו דרך ההסתרות והלבושים.

הקבלה מלמדת אותנו כיצד להרחיב את הכלים שלנו כדי לקבל יותר אור, ובכך להתקרב יותר ויותר לבורא.

העבודה העיקרית היא לתקן את הרצון לקבל שלנו - להפוך אותו מרצון לקבל לעצמו, לרצון לקבל על מנת להשפיע.

זהו התיקון האמיתי, וזו מטרת כל הבריאה.""",
        book="הקדמה לחכמת הקבלה",
        page="1",
        source_url="https://search.orhasulam.org/",
        scraped_at=datetime.utcnow(),
    )

    baal_hasulam_collection = MaamarCollection(
        source=SourceCategory.BAAL_HASULAM,
        maamarim=[baal_hasulam_maamar],
        last_updated=datetime.utcnow(),
    )

    # Sample Rabash maamar
    rabash_maamar = Maamar(
        id="rabash_sample_1",
        source=SourceCategory.RABASH,
        title="מהו שנתנו הסולם להעלות בו",
        subtitle="מאמר ג",
        text="""נתנו לנו את הסולם להעלות בו, פירוש, שהאדם צריך לעלות ממדרגה למדרגה.

והעלייה היא בכח התורה והמצוות. כי בכל פעם שהאדם עוסק בתורה ומקיים מצוות, הוא עולה מדרגה אחת.

אבל יש לדעת שהעלייה אינה אוטומטית. האדם צריך להשתוקק לעלות, צריך לרצות להתקרב לבורא.

העבודה היא לשים לב לכוונה - לא רק לעשות, אלא לעשות עם הכוונה הנכונה.

וזוהי העבודה האמיתית - לתקן את הכוונה שלנו בכל מעשה ומעשה.""",
        book="שמעתי",
        page="25",
        source_url="https://ashlagbaroch.org/rbsMore/",
        pdf_filename="shamati.pdf",
        pdf_start_page=25,
        pdf_end_page=26,
        scraped_at=datetime.utcnow(),
    )

    rabash_collection = MaamarCollection(
        source=SourceCategory.RABASH,
        maamarim=[rabash_maamar],
        last_updated=datetime.utcnow(),
    )

    # Save sample files
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "baal_hasulam.json", "w", encoding="utf-8") as f:
        f.write(baal_hasulam_collection.model_dump_json(indent=2))

    with open(output_dir / "rabash.json", "w", encoding="utf-8") as f:
        f.write(rabash_collection.model_dump_json(indent=2))

    print(f"Created sample maamarim in {output_dir}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape maamarim from Baal Hasulam and Rabash sources"
    )
    parser.add_argument(
        "--source",
        choices=["baal_hasulam", "rabash", "all"],
        default="all",
        help="Source to scrape (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "data" / "maamarim",
        help="Output directory for JSON cache files",
    )
    parser.add_argument(
        "--cache-pdfs",
        action="store_true",
        help="Cache downloaded PDFs locally",
    )
    parser.add_argument(
        "--pdf-cache-dir",
        type=Path,
        default=project_root / "data" / "pdf_cache",
        help="Directory to cache downloaded PDFs",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Create sample maamarim for testing (no scraping)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # For sample creation, use basic logging (no env vars required)
    if args.sample:
        import logging

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        create_sample_maamarim(args.output_dir)
        print(f"Sample maamarim created in {args.output_dir}")
        return 0

    # Setup full logging (requires env vars)
    setup_logging()

    pdf_cache_dir = args.pdf_cache_dir if args.cache_pdfs else None

    async def run() -> dict:
        if args.source == "all":
            return await scrape_all(args.output_dir, pdf_cache_dir)
        else:
            source = SourceCategory(args.source)
            collection = await scrape_source(source, args.output_dir, pdf_cache_dir)
            return {source: collection} if collection else {}

    results = asyncio.run(run())

    total = sum(len(c.maamarim) for c in results.values() if c)
    logger.info("scraping_complete", total_maamarim=total, sources=len(results))

    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
