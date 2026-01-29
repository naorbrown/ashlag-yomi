#!/usr/bin/env python3
"""
Fix Chasdei Ashlag quotes - remove RABASH duplicates.

The chasdei_ashlag.json file contains quotes from "הרב ברוך אשלג" which is
actually RABASH (Rabbi Baruch Shalom Ashlag) - he already has his own category.

Chasdei Ashlag should only contain students who came AFTER RABASH, such as:
- הרב מיכאל לייטמן

This script removes the RABASH quotes from chasdei_ashlag.json.
"""

import json
from datetime import datetime
from pathlib import Path


def main():
    quotes_file = (
        Path(__file__).parent.parent / "data" / "quotes" / "chasdei_ashlag.json"
    )

    with open(quotes_file, encoding="utf-8") as f:
        data = json.load(f)

    original_count = len(data["quotes"])
    print(f"Original quote count: {original_count}")

    # Count by rabbi
    rabbi_counts = {}
    for quote in data["quotes"]:
        rabbi = quote.get("source_rabbi", "Unknown")
        rabbi_counts[rabbi] = rabbi_counts.get(rabbi, 0) + 1

    print("\nRabbi distribution before:")
    for rabbi, count in sorted(rabbi_counts.items()):
        print(f"  {rabbi}: {count}")

    # Remove RABASH quotes (הרב ברוך אשלג)
    # Note: RABASH can appear under different names
    rabash_names = {"הרב ברוך אשלג", "הרב ברוך שלום אשלג", "הרבש"}

    filtered_quotes = [
        quote
        for quote in data["quotes"]
        if quote.get("source_rabbi", "") not in rabash_names
    ]

    removed_count = original_count - len(filtered_quotes)
    print(f"\nQuotes removed: {removed_count}")

    # Update data
    data["quotes"] = filtered_quotes
    data["last_updated"] = datetime.now().isoformat()

    # Save
    with open(quotes_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"New quote count: {len(filtered_quotes)}")

    # Verify final rabbi distribution
    print("\nRabbi distribution after:")
    rabbi_counts_after = {}
    for quote in filtered_quotes:
        rabbi = quote.get("source_rabbi", "Unknown")
        rabbi_counts_after[rabbi] = rabbi_counts_after.get(rabbi, 0) + 1

    for rabbi, count in sorted(rabbi_counts_after.items()):
        print(f"  {rabbi}: {count}")


if __name__ == "__main__":
    main()
