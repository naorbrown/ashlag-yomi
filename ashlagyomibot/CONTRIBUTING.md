# Contributing to Ashlag Yomi

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Quick Setup

```bash
# Clone
git clone https://github.com/naorbrown/ashlag-yomi.git
cd ashlag-yomi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Copy environment template
cp .env.example .env
# Edit .env with your test bot token
```

## 🧪 Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_handlers.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

**Coverage requirement:** All PRs must maintain **80% test coverage**.

## 📝 Code Style

We use these tools for consistent code:

| Tool | Purpose |
|------|---------|
| **Black** | Code formatting (line length: 88) |
| **Ruff** | Fast linting |
| **MyPy** | Type checking |

```bash
# Format
black src tests scripts

# Lint
ruff check src tests scripts

# Type check
mypy src

# Run all checks
make all
```

## 💬 Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
```
feat(handlers): add /quote command for single quotes
fix(formatters): escape HTML entities in quote text
docs(readme): update installation instructions
test(repository): add tests for get_random_quote
```

## 📚 Adding Quotes

Quotes live in `data/quotes/*.json`. Each category has its own file.

### Quote Format

```json
{
  "id": "category-source-001",
  "text": "Hebrew quote text",
  "source_rabbi": "Rabbi name in Hebrew",
  "source_book": "Book name",
  "source_section": "Chapter/section",
  "source_url": "https://source.url/path",
  "category": "category_name",
  "tags": ["tag1", "tag2"],
  "length_estimate": 30
}
```

### Categories

| Category | Hebrew | Description |
|----------|--------|-------------|
| `arizal` | האר״י הקדוש | Lurianic Kabbalah |
| `baal_shem_tov` | הבעל שם טוב | Chassidut founder and students |
| `polish_chassidut` | חסידות פולין | Polish Chassidic schools |
| `baal_hasulam` | בעל הסולם | Modern Kabbalah |
| `rabash` | הרב״ש | Practical application |
| `chasdei_ashlag` | חסידי אשלג | Contemporary students |

### Validation

```bash
# Validate all quote files
python -c "from src.data.repository import QuoteRepository; print(QuoteRepository().validate_all())"
```

### Attribution Guidelines

- **Always** attribute to the correct author
- For student-authored books, use the student's name as `source_rabbi`
- Keep `category` for lineage connection

## 🔄 Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run all checks: `make all`
5. Commit with conventional commit message
6. Push and open a Pull Request

### PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] New tests for new features
- [ ] Code formatted (`black`)
- [ ] No lint errors (`ruff check`)
- [ ] Type hints added (`mypy src`)
- [ ] Coverage ≥ 80%

## 🛠️ Development Tips

### Running the Bot Locally

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"

# Run
python -m src.bot.main
```

### Testing Commands in Telegram

| Command | What to test |
|---------|--------------|
| `/start` | Welcome message appears |
| `/today` | 6 quotes with source buttons |
| `/quote` | Single quote with source button |
| `/about` | Lineage information |
| `/help` | Command list |
| `/feedback` | GitHub link works |

### HTML Formatting

We use HTML parse mode (more reliable than Markdown):

```python
"<b>bold</b>"
"<i>italic</i>"
'<a href="https://example.com">link</a>'
```

## 🆘 Questions?

- Open an [issue](https://github.com/naorbrown/ashlag-yomi/issues)
- Start a [discussion](https://github.com/naorbrown/ashlag-yomi/discussions)

---

Thank you for helping spread spiritual wisdom! 🕯️
