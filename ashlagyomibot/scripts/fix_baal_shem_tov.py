#!/usr/bin/env python3
"""
Fix Baal Shem Tov quote attributions.

Many quotes in baal_shem_tov.json are from books written by students of the Besht,
not by the Besht himself. This script updates the source_rabbi field to reflect
the actual author while keeping the category as baal_shem_tov (for lineage context).

Student-authored books:
- דגל מחנה אפרים -> רבי משה חיים אפרים מסודילקוב (grandson)
- מאור עינים -> רבי מנחם נחום מטשרנוביל (student)
- נועם אלימלך -> רבי אלימלך מליזענסק (student)
- תולדות יעקב יוסף -> רבי יעקב יוסף מפולנאה (student)
- קדושת לוי -> רבי לוי יצחק מברדיטשוב (student)

Books attributed to the Besht (keep as הבעל שם טוב):
- כתר שם טוב - compilation of his sayings
- צוואת הריב"ש - ethical will
- שבחי הבעל שם טוב - stories about him
"""

import json
from pathlib import Path

# Mapping from book name to actual author
BOOK_TO_AUTHOR = {
    "דגל מחנה אפרים": "רבי משה חיים אפרים מסודילקוב",
    "מאור עינים": "רבי מנחם נחום מטשרנוביל",
    "נועם אלימלך": "רבי אלימלך מליזענסק",
    "תולדות יעקב יוסף": "רבי יעקב יוסף מפולנאה",
    "קדושת לוי": "רבי לוי יצחק מברדיטשוב",
}

# Books that should stay attributed to the Besht
BESHT_BOOKS = {"כתר שם טוב", "צוואת הריב\"ש", "שבחי הבעל שם טוב"}


def main():
    quotes_file = Path(__file__).parent.parent / "data" / "quotes" / "baal_shem_tov.json"

    with open(quotes_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total quotes: {len(data['quotes'])}")

    # Count changes by book
    changes = {}

    for quote in data['quotes']:
        book = quote.get('source_book', '')

        if book in BOOK_TO_AUTHOR:
            new_author = BOOK_TO_AUTHOR[book]
            old_author = quote.get('source_rabbi', '')

            if old_author != new_author:
                quote['source_rabbi'] = new_author
                changes[book] = changes.get(book, 0) + 1

    # Save updated data
    with open(quotes_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nChanges made:")
    for book, count in sorted(changes.items()):
        author = BOOK_TO_AUTHOR[book]
        print(f"  {book}: {count} quotes -> {author}")

    print(f"\nTotal quotes updated: {sum(changes.values())}")


if __name__ == "__main__":
    main()
