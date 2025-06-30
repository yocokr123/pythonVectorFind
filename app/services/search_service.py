"""
검색 서비스
비즈니스 로직을 담당하는 서비스 레이어
"""

import time
import logging
from typing import List, Dict, Any, Optional
from app.models.search_engine import ContextualSearchEngine
from app.schemas.search import SearchRequest, HybridSearchRequest, TagSearchRequest, SearchResult, SearchResponse
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class SearchService:
    """검색 서비스 클래스"""
    
    def __init__(self, search_engine: ContextualSearchEngine):
        self.search_engine = search_engine
        self.settings = get_settings()
    
    async def semantic_search(self, request: SearchRequest) -> SearchResponse:
        """문맥검색 (의미적 유사도)"""
        start_time = time.time()
        
        try:
            # 검색 실행
            results = self.search_engine.semantic_search(
                query=request.query,
                size=min(request.size, self.settings.max_search_size),
                category=request.category
            )
            
            # 응답 시간 계산
            query_time_ms = (time.time() - start_time) * 1000
            
            # Pydantic 모델로 변환
            search_results = [
                SearchResult(
                    id=result['id'],
                    score=result['score'],
                    title=result['title'],
                    content=result['content'],
                    category=result.get('category'),
                    tags=result.get('tags', []),
                    highlights=result.get('highlights', {})
                )
                for result in results
            ]
            
            return SearchResponse(
                success=True,
                message=f"문맥검색 완료: '{request.query}'에 대해 {len(results)}개 결과 발견",
                results=search_results,
                total_count=len(results),
                query_time_ms=query_time_ms
            )
            
        except Exception as e:
            logger.error(f"문맥검색 중 오류 발생: {e}")
            raise
    
    async def hybrid_search(self, request: HybridSearchRequest) -> SearchResponse:
        """하이브리드 검색 (키워드 + 문맥)"""
        start_time = time.time()
        
        try:
            # 검색 실행
            results = self.search_engine.hybrid_search(
                query=request.query,
                size=min(request.size, self.settings.max_search_size),
                category=request.category,
                semantic_weight=request.semantic_weight,
                keyword_weight=request.keyword_weight
            )
            
            # 응답 시간 계산
            query_time_ms = (time.time() - start_time) * 1000
            
            # Pydantic 모델로 변환
            search_results = [
                SearchResult(
                    id=result['id'],
                    score=result['score'],
                    title=result['title'],
                    content=result['content'],
                    category=result.get('category'),
                    tags=result.get('tags', []),
                    highlights=result.get('highlights', {})
                )
                for result in results
            ]
            
            return SearchResponse(
                success=True,
                message=f"하이브리드 검색 완료: '{request.query}'에 대해 {len(results)}개 결과 발견",
                results=search_results,
                total_count=len(results),
                query_time_ms=query_time_ms
            )
            
        except Exception as e:
            logger.error(f"하이브리드 검색 중 오류 발생: {e}")
            raise
    
    async def search_by_tags(self, request: TagSearchRequest) -> SearchResponse:
        """태그 기반 검색"""
        start_time = time.time()
        
        try:
            # 검색 실행
            results = self.search_engine.search_by_tags(
                tags=request.tags,
                size=min(request.size, self.settings.max_search_size)
            )
            
            # 응답 시간 계산
            query_time_ms = (time.time() - start_time) * 1000
            
            # Pydantic 모델로 변환
            search_results = [
                SearchResult(
                    id=result['id'],
                    score=result['score'],
                    title=result['title'],
                    content=result['content'],
                    category=result.get('category'),
                    tags=result.get('tags', []),
                    highlights=result.get('highlights', {})
                )
                for result in results
            ]
            
            return SearchResponse(
                success=True,
                message=f"태그 검색 완료: {request.tags}에 대해 {len(results)}개 결과 발견",
                results=search_results,
                total_count=len(results),
                query_time_ms=query_time_ms
            )
            
        except Exception as e:
            logger.error(f"태그 검색 중 오류 발생: {e}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """인덱스 통계 조회"""
        try:
            stats = self.search_engine.get_statistics()
            return stats
        except Exception as e:
            logger.error(f"통계 조회 중 오류 발생: {e}")
            raise 