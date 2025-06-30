"""
API 모듈
"""

from fastapi import APIRouter
from .v1 import search_router, document_router, health_router, agent_router

# API 라우터 등록
api_router = APIRouter(prefix="/api")

# v1 API 등록
api_router.include_router(search_router, prefix="/v1", tags=["search"])
api_router.include_router(document_router, prefix="/v1", tags=["documents"])
api_router.include_router(health_router, prefix="/v1", tags=["health"])
api_router.include_router(agent_router, prefix="/v1", tags=["agent"])

__all__ = ["api_router"] 