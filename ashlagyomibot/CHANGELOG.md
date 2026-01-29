# Changelog

All notable changes to Ashlag Yomi are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-29

### Added

- **6 daily quotes** from the Ashlag Kabbalistic lineage
- **Commands**: `/start`, `/today`, `/quote`, `/about`, `/help`, `/feedback`
- **Inline keyboards** for source links (nachyomi-bot pattern)
- **Rate limiting** — 5 requests per minute per user
- **Torah Yomi integration** — unified channel publishing
- **GitHub Actions** — automated daily broadcasts at 6:00 AM Israel time
- **80%+ test coverage** with pytest

### Quote Database

- **2,011 quotes** across 6 categories
- 🕯️ Arizal (365 quotes)
- ✨ Baal Shem Tov (365 quotes)
- 🔥 Polish Chassidut (365 quotes)
- 📖 Baal HaSulam (365 quotes)
- 💎 Rabash (365 quotes)
- 🌱 Chasdei Ashlag (186 quotes)

### Technical

- Python 3.11+ with python-telegram-bot v20+
- Pydantic v2 for data validation
- Dual-cron scheduling for DST handling (3am + 4am UTC)
- Idempotent broadcasts (safe duplicate triggers)
