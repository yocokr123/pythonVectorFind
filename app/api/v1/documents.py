"""
문서 API 엔드포인트
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.document import DocumentRequest
from app.schemas.common import StatusResponse
from app.services.document_service import DocumentService
from app.core.dependencies import get_search_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=StatusResponse, summary="문서 추가")
async def add_document(
    request: DocumentRequest,
    search_engine = Depends(get_search_engine)
) -> StatusResponse:
    """
    새 문서를 추가합니다.
    
    - **doc_id**: 문서 고유 ID
    - **title**: 문서 제목
    - **content**: 문서 내용
    - **category**: 카테고리 (선택사항)
    - **tags**: 태그들 (선택사항)
    """
    try:
        document_service = DocumentService(search_engine)
        return await document_service.add_document(request)
    except Exception as e:
        logger.error(f"문서 추가 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}", summary="문서 조회")
async def get_document(
    doc_id: str,
    search_engine = Depends(get_search_engine)
):
    """
    특정 문서를 조회합니다.
    
    - **doc_id**: 조회할 문서 ID
    """
    try:
        document_service = DocumentService(search_engine)
        return await document_service.get_document(doc_id)
    except Exception as e:
        logger.error(f"문서 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}", response_model=StatusResponse, summary="문서 삭제")
async def delete_document(
    doc_id: str,
    search_engine = Depends(get_search_engine)
) -> StatusResponse:
    """
    특정 문서를 삭제합니다.
    
    - **doc_id**: 삭제할 문서 ID
    """
    try:
        document_service = DocumentService(search_engine)
        return await document_service.delete_document(doc_id)
    except Exception as e:
        logger.error(f"문서 삭제 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 