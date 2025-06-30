"""
의존성 주입 모듈
"""

from typing import Optional
from app.models.search_engine import ContextualSearchEngine
from app.services.search_service import SearchService
from app.services.agent_service import get_agent_service
from app.config.settings import get_settings

# 전역 변수로 검색 엔진 인스턴스 관리
_search_engine: Optional[ContextualSearchEngine] = None
_search_service: Optional[SearchService] = None


def get_search_engine() -> ContextualSearchEngine:
    """검색 엔진 인스턴스를 반환합니다 (싱글톤 패턴)"""
    global _search_engine
    
    if _search_engine is None:
        settings = get_settings()
        
        _search_engine = ContextualSearchEngine(
            host=settings.opensearch_host,
            port=settings.opensearch_port,
            username=settings.opensearch_username,
            password=settings.opensearch_password,
            model_name=settings.embedding_model
        )
    
    return _search_engine


def get_search_service() -> SearchService:
    """검색 서비스 인스턴스를 반환합니다 (싱글톤 패턴)"""
    global _search_service
    
    if _search_service is None:
        search_engine = get_search_engine()
        _search_service = SearchService(search_engine)
    
    return _search_service 