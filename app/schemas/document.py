"""
문서 관련 API 스키마
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    """문서 추가 요청 스키마"""
    doc_id: str = Field(..., description="문서 고유 ID", min_length=1, max_length=100)
    title: str = Field(..., description="문서 제목", min_length=1, max_length=200)
    content: str = Field(..., description="문서 내용", min_length=1, max_length=10000)
    category: Optional[str] = Field(default=None, description="카테고리", max_length=50)
    tags: Optional[List[str]] = Field(default=None, description="태그들")


class DocumentResponse(BaseModel):
    """문서 응답 스키마"""
    id: str = Field(..., description="문서 ID")
    title: str = Field(..., description="문서 제목")
    content: str = Field(..., description="문서 내용")
    category: Optional[str] = Field(default=None, description="카테고리")
    tags: List[str] = Field(default=[], description="태그들")
    created_at: str = Field(..., description="생성일시")
    updated_at: Optional[str] = Field(default=None, description="수정일시") 