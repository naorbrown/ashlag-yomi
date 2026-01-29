FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user (security best practice)
RUN useradd --create-home --shell /bin/bash ashlag

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ src/
COPY data/ data/

# Switch to non-root user
USER ashlag

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.data.repository import QuoteRepository; QuoteRepository()" || exit 1

CMD ["python", "-m", "src.bot.main"]
