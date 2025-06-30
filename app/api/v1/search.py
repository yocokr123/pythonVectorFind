"""
검색 API 엔드포인트
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.search import (
    SearchRequest, 
    HybridSearchRequest, 
    TagSearchRequest, 
    SearchResponse
)
from app.schemas.common import StatisticsResponse
from app.services.search_service import SearchService
from app.core.dependencies import get_search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/semantic", response_model=SearchResponse, summary="문맥검색")
async def semantic_search(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service)
) -> SearchResponse:
    """
    임베딩 기반 문맥검색을 수행합니다.
    
    - **query**: 검색 쿼리
    - **size**: 반환할 결과 개수 (기본값: 10)
    - **category**: 카테고리 필터 (선택사항)
    """
    try:
        return await search_service.semantic_search(request)
    except Exception as e:
        logger.error(f"문맥검색 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid", response_model=SearchResponse, summary="하이브리드 검색")
async def hybrid_search(
    request: HybridSearchRequest,
    search_service: SearchService = Depends(get_search_service)
) -> SearchResponse:
    """
    하이브리드 검색 (키워드 + 문맥)을 수행합니다.
    
    - **query**: 검색 쿼리
    - **size**: 반환할 결과 개수 (기본값: 10)
    - **category**: 카테고리 필터 (선택사항)
    - **semantic_weight**: 문맥검색 가중치 (기본값: 0.7)
    - **keyword_weight**: 키워드검색 가중치 (기본값: 0.3)
    """
    try:
        return await search_service.hybrid_search(request)
    except Exception as e:
        logger.error(f"하이브리드 검색 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tags", response_model=SearchResponse, summary="태그 검색")
async def search_by_tags(
    request: TagSearchRequest,
    search_service: SearchService = Depends(get_search_service)
) -> SearchResponse:
    """
    태그를 기반으로 검색합니다.
    
    - **tags**: 검색할 태그들
    - **size**: 반환할 결과 개수 (기본값: 10)
    """
    try:
        return await search_service.search_by_tags(request)
    except Exception as e:
        logger.error(f"태그 검색 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=StatisticsResponse, summary="통계 조회")
async def get_statistics(
    search_service: SearchService = Depends(get_search_service)
) -> StatisticsResponse:
    """
    인덱스 통계 정보를 조회합니다.
    """
    try:
        stats = await search_service.get_statistics()
        return StatisticsResponse(
            success=True,
            message="통계 정보를 성공적으로 조회했습니다.",
            statistics=stats
        )
    except Exception as e:
        logger.error(f"통계 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 