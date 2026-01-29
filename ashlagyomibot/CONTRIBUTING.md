# Contributing to Ashlag Yomi

Thank you for your interest in contributing! This document provides guidelines
for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- A Telegram bot token (for testing)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ashlag-yomi.git
cd ashlag-yomi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Copy environment template
cp .env.example .env
# Edit .env with your test credentials
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_formatters.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

### Coverage Requirements

All pull requests must maintain **80% test coverage**. The CI pipeline will
fail if coverage drops below this threshold.

## Code Style

### Python Style

We follow PEP 8 with these tools:

- **Black** for formatting (line length: 88)
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
black src tests scripts

# Lint code
ruff check src tests scripts

# Type check
mypy src
```

### Run All Checks

```bash
make all  # Runs format, lint, type-check, and test
```

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:

```
feat(broadcaster): add idempotent broadcast check
fix(formatters): use HTML parse mode for reliable links
docs(readme): add architecture diagram
test(handlers): add tests for /about command
```

## Adding Quotes

### Quote Format

Quotes are stored in `data/quotes/*.json`:

```json
{
  "id": "category-source-001",
  "text": "Hebrew quote text",
  "source_rabbi": "Rabbi name in Hebrew",
  "source_book": "Book name",
  "source_section": "Chapter/section reference",
  "source_url": "https://source.url/path",
  "category": "category_name",
  "tags": ["tag1", "tag2"],
  "length_estimate": 30
}
```

### Categories

| Category | Hebrew Name | Description |
|----------|-------------|-------------|
| `arizal` | האר״י הקדוש | Lurianic Kabbalah |
| `baal_shem_tov` | הבעל שם טוב | Founder of Chassidut and students |
| `polish_chassidut` | חסידות פולין | Polish Chassidic schools |
| `baal_hasulam` | בעל הסולם | Modern Kabbalah |
| `rabash` | הרב״ש | Practical application |
| `chasdei_ashlag` | חסידי אשלג | Contemporary students |

### Validation

All quote files are validated on every commit:

```bash
# Validate quote files
python -c "from src.data.repository import QuoteRepository; print(QuoteRepository().validate_all())"
```

### Attribution Guidelines

- **Always** attribute to the correct author, not just the book
- For student-authored books (e.g., Degel Machane Efraim), use the student's name as `source_rabbi`
- Keep `category` for lineage connection (e.g., student books stay in `baal_shem_tov` category)

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Run linting: `ruff check && mypy src`
6. Format code: `black src tests`
7. Commit with conventional commit message
8. Push to your fork
9. Open a Pull Request

### PR Checklist

- [ ] Tests pass locally (`pytest`)
- [ ] New tests added for new features
- [ ] Code formatted with Black
- [ ] No linting errors (`ruff check`)
- [ ] Type hints added for new code (`mypy src`)
- [ ] Documentation updated if needed
- [ ] Coverage maintained at 80%+

## Development Tips

### Running the Bot Locally

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Run the bot
python -m src.bot.main

# Or use make
make run
```

### Testing Commands

Once the bot is running locally, you can test commands in Telegram:

- `/start` - Welcome message
- `/today` - Get today's quotes
- `/about` - Lineage information
- `/help` - Command list
- `/feedback` - Feedback info

### HTML Formatting

We use HTML parse mode for Telegram messages (more reliable than Markdown for links):

```python
# Bold
"<b>text</b>"

# Italic
"<i>text</i>"

# Link
'<a href="https://example.com">link text</a>'
```

## Questions?

Open an issue or start a discussion on GitHub.
