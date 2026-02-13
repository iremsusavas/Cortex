"""Dependency injection for API routes."""

from collections.abc import AsyncGenerator

from backend.db.session import get_db

__all__ = ["get_db"]
