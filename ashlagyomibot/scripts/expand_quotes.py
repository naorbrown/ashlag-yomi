#!/usr/bin/env python3
"""Script to expand quote files to 365+ quotes per category."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "quotes"


def get_quote_count(filepath: Path) -> int:
    """Get the number of quotes in a JSON file."""
    with open(filepath) as f:
        data = json.load(f)
    return len(data.get("quotes", []))


def main():
    """Print current quote counts."""
    print("Current quote counts:")
    print("-" * 40)

    total = 0
    for filepath in sorted(DATA_DIR.glob("*.json")):
        count = get_quote_count(filepath)
        total += count
        status = "✓" if count >= 365 else f"need {365 - count} more"
        print(f"{filepath.stem}: {count} ({status})")

    print("-" * 40)
    print(f"Total: {total}")
    print(f"Target: {6 * 365} = 2190")
    print(f"Remaining: {max(0, 6 * 365 - total)}")


if __name__ == "__main__":
    main()
