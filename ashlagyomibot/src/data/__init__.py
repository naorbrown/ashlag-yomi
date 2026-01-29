"""Data layer for Ashlag Yomi - models, repository, and data sources."""

from src.data.maamar_repository import MaamarRepository, get_maamar_repository
from src.data.models import (
    DailyBundle,
    DailyMaamar,
    Maamar,
    MaamarCollection,
    MaamarSentRecord,
    Quote,
    QuoteCategory,
    SourceCategory,
)
from src.data.repository import QuoteRepository, get_repository

__all__ = [
    # New maamar models and repository
    "DailyMaamar",
    "Maamar",
    "MaamarCollection",
    "MaamarRepository",
    "MaamarSentRecord",
    "SourceCategory",
    "get_maamar_repository",
    # Legacy quote models (deprecated)
    "DailyBundle",
    "Quote",
    "QuoteCategory",
    "QuoteRepository",
    "get_repository",
]
