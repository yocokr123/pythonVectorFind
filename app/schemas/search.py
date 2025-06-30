"""
검색 관련 API 스키마
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """문맥검색 요청 스키마"""
    query: str = Field(..., description="검색 쿼리", min_length=1, max_length=500)
    size: int = Field(default=10, description="반환할 결과 개수", ge=1, le=100)
    category: Optional[str] = Field(default=None, description="카테고리 필터")


class HybridSearchRequest(BaseModel):
    """하이브리드 검색 요청 스키마"""
    query: str = Field(..., description="검색 쿼리", min_length=1, max_length=500)
    size: int = Field(default=10, description="반환할 결과 개수", ge=1, le=100)
    category: Optional[str] = Field(default=None, description="카테고리 필터")
    semantic_weight: float = Field(default=0.7, description="문맥검색 가중치", ge=0.0, le=1.0)
    keyword_weight: float = Field(default=0.3, description="키워드검색 가중치", ge=0.0, le=1.0)


class TagSearchRequest(BaseModel):
    """태그 검색 요청 스키마"""
    tags: List[str] = Field(..., description="검색할 태그들", min_items=1)
    size: int = Field(default=10, description="반환할 결과 개수", ge=1, le=100)


class SearchResult(BaseModel):
    """검색 결과 스키마"""
    id: str = Field(..., description="문서 ID")
    score: float = Field(..., description="검색 점수")
    title: str = Field(..., description="문서 제목")
    content: str = Field(..., description="문서 내용")
    category: Optional[str] = Field(default=None, description="카테고리")
    tags: List[str] = Field(default=[], description="태그들")
    highlights: Dict[str, Any] = Field(default={}, description="하이라이트된 내용")


class SearchResponse(BaseModel):
    """검색 응답 스키마"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    results: List[SearchResult] = Field(..., description="검색 결과")
    total_count: int = Field(..., description="총 결과 개수")
    query_time_ms: Optional[float] = Field(default=None, description="쿼리 실행 시간 (ms)") 