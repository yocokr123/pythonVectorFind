"""
공통 API 스키마
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """상태 응답 스키마"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    status: str = Field(..., description="상태 코드")


class StatisticsResponse(BaseModel):
    """통계 응답 스키마"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    statistics: Dict[str, Any] = Field(..., description="통계 정보")


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    success: bool = Field(default=False, description="성공 여부")
    message: str = Field(..., description="에러 메시지")
    error_code: Optional[str] = Field(default=None, description="에러 코드")
    details: Optional[Dict[str, Any]] = Field(default=None, description="상세 정보")


class PaginationResponse(BaseModel):
    """페이지네이션 응답 스키마"""
    page: int = Field(..., description="현재 페이지", ge=1)
    size: int = Field(..., description="페이지 크기", ge=1)
    total: int = Field(..., description="총 개수", ge=0)
    total_pages: int = Field(..., description="총 페이지 수", ge=0)
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부") 