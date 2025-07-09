"""
API v1 모듈
"""

from .search import router as search_router
from .documents import router as document_router
from .health import router as health_router

__all__ = ["search_router", "document_router", "health_router"] 