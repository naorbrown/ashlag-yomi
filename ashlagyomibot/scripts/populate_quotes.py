#!/usr/bin/env python3
"""
Populate the quotes database with initial data.

This script creates sample quote files if they don't exist.
For production, you'll want to manually curate quotes and add them
to the JSON files.

Usage:
    python scripts/populate_quotes.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.models import QuoteCategory

# Sample quotes for each category
# In production, these would be replaced with actual curated quotes
SAMPLE_QUOTES: dict[QuoteCategory, list[dict]] = {
    QuoteCategory.ARIZAL: [
        {
            "id": "arizal-001",
            "text": "כל הנשמות שירדו לעולם הזה, כולם באו מאדם הראשון",
            "source_rabbi": "האר״י הקדוש",
            "source_book": "עץ חיים",
            "source_section": "שער א׳",
            "source_url": "https://www.sefaria.org/Etz_Chaim",
            "category": "arizal",
            "tags": ["נשמות", "אדם הראשון"],
            "length_estimate": 20,
        },
        {
            "id": "arizal-002",
            "text": "כל העולמות נבראו בשביל האדם, שיתקן את עצמו ואת כל העולמות",
            "source_rabbi": "האר״י הקדוש",
            "source_book": "שער הגלגולים",
            "source_url": "https://www.sefaria.org/Shaar_HaGilgulim",
            "category": "arizal",
            "tags": ["תיקון", "עולמות"],
            "length_estimate": 25,
        },
    ],
    QuoteCategory.BAAL_SHEM_TOV: [
        {
            "id": "besht-001",
            "text": "במקום שמחשבתו של אדם שם הוא נמצא כולו",
            "source_rabbi": "הבעל שם טוב",
            "source_book": "כתר שם טוב",
            "source_url": "https://www.sefaria.org/Keter_Shem_Tov",
            "category": "baal_shem_tov",
            "tags": ["מחשבה", "ריכוז"],
            "length_estimate": 15,
        },
        {
            "id": "besht-002",
            "text": "אין דבר בעולם שאין בו ניצוץ קדושה",
            "source_rabbi": "הבעל שם טוב",
            "source_book": "צוואת הריב״ש",
            "source_url": "https://www.sefaria.org/Tzavaas_HaRivash",
            "category": "baal_shem_tov",
            "tags": ["קדושה", "ניצוצות"],
            "length_estimate": 15,
        },
    ],
    QuoteCategory.SIMCHA_BUNIM: [
        {
            "id": "simcha-bunim-001",
            "text": "כל אדם צריך שיהיו לו שני כיסים: בכיס אחד כתוב ״בשבילי נברא העולם״, ובכיס השני ״ואנכי עפר ואפר״",
            "source_rabbi": "רבי שמחה בונים מפשיסחא",
            "source_book": "קול שמחה",
            "source_url": "https://www.orhassulam.com/",
            "category": "simcha_bunim",
            "tags": ["ענווה", "גדלות"],
            "length_estimate": 30,
        },
    ],
    QuoteCategory.KOTZKER: [
        {
            "id": "kotzker-001",
            "text": "אם אני אני בגלל שאתה אתה, ואתה אתה בגלל שאני אני - אז אני לא אני ואתה לא אתה",
            "source_rabbi": "הרבי מקוצק",
            "source_book": "אמת מקוצק",
            "source_url": "https://www.orhassulam.com/",
            "category": "kotzker",
            "tags": ["אמת", "זהות"],
            "length_estimate": 25,
        },
        {
            "id": "kotzker-002",
            "text": "אין דבר שלם יותר מלב שבור",
            "source_rabbi": "הרבי מקוצק",
            "source_book": "אמרי אמת",
            "source_url": "https://www.orhassulam.com/",
            "category": "kotzker",
            "tags": ["לב", "שלמות", "שבירה"],
            "length_estimate": 10,
        },
    ],
    QuoteCategory.BAAL_HASULAM: [
        {
            "id": "baal-hasulam-001",
            "text": "כל המצער את עצמו על צרות הכלל, זוכה ורואה בנחמתו",
            "source_rabbi": "בעל הסולם",
            "source_book": "מאמר לסיום הזוהר",
            "source_url": "https://www.orhassulam.com/",
            "category": "baal_hasulam",
            "tags": ["ערבות", "כלל"],
            "length_estimate": 20,
        },
        {
            "id": "baal-hasulam-002",
            "text": "הסתכלות בתכלית מביאה את האדם לשלמות",
            "source_rabbi": "בעל הסולם",
            "source_book": "מאמרי הסולם",
            "source_url": "https://www.orhassulam.com/",
            "category": "baal_hasulam",
            "tags": ["תכלית", "שלמות"],
            "length_estimate": 15,
        },
        {
            "id": "baal-hasulam-003",
            "text": "אין אור גדול יותר מהאור היוצא מתוך החושך",
            "source_rabbi": "בעל הסולם",
            "source_book": "הקדמה לספר הזוהר",
            "source_url": "https://www.orhassulam.com/",
            "category": "baal_hasulam",
            "tags": ["אור", "חושך"],
            "length_estimate": 15,
        },
    ],
    QuoteCategory.RABASH: [
        {
            "id": "rabash-001",
            "text": "העבודה האמיתית היא לצאת מאהבה עצמית ולהגיע לאהבת הזולת",
            "source_rabbi": 'הרב"ש',
            "source_book": "מאמרי הסולם",
            "source_url": "https://www.orhassulam.com/",
            "category": "rabash",
            "tags": ["אהבה", "עבודה"],
            "length_estimate": 20,
        },
        {
            "id": "rabash-002",
            "text": "החברה היא הכלי שבו האדם יכול לגלות את האמת",
            "source_rabbi": 'הרב"ש',
            "source_book": "מאמרי חברה",
            "source_url": "https://www.orhassulam.com/",
            "category": "rabash",
            "tags": ["חברה", "אמת"],
            "length_estimate": 15,
        },
    ],
    QuoteCategory.TALMIDIM: [
        {
            "id": "talmidim-001",
            "text": "הדרך להתקדמות רוחנית עוברת דרך הקשר עם הזולת",
            "source_rabbi": "התלמידים",
            "source_url": "https://www.orhassulam.com/",
            "category": "talmidim",
            "tags": ["התקדמות", "חיבור"],
            "length_estimate": 15,
        },
    ],
}


def create_quote_file(category: QuoteCategory, quotes: list[dict]) -> None:
    """Create a JSON file for a category's quotes."""
    quotes_dir = project_root / "data" / "quotes"
    quotes_dir.mkdir(parents=True, exist_ok=True)

    file_path = quotes_dir / f"{category.value}.json"

    # Add created_at timestamp to each quote
    for quote in quotes:
        if "created_at" not in quote:
            quote["created_at"] = datetime.utcnow().isoformat()

    data = {
        "category": category.value,
        "display_name_hebrew": category.display_name_hebrew,
        "display_name_english": category.display_name_english,
        "quotes": quotes,
        "last_updated": datetime.utcnow().isoformat(),
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Created {file_path.name} with {len(quotes)} quotes")


def main() -> int:
    """Populate quote files."""
    print("\n📚 Ashlag Yomi Quote Populator\n")
    print("=" * 40)

    total_quotes = 0

    for category in QuoteCategory:
        quotes = SAMPLE_QUOTES.get(category, [])
        if quotes:
            create_quote_file(category, quotes)
            total_quotes += len(quotes)
        else:
            print(f"⚠️  No sample quotes for {category.value}")

    print("\n" + "=" * 40)
    print(f"✅ Created {total_quotes} sample quotes across {len(QuoteCategory)} categories")
    print("\n⚠️  NOTE: These are sample quotes!")
    print("   For production, please curate authentic quotes from primary sources.")
    print("\n   Edit the JSON files in data/quotes/ to add real quotes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
