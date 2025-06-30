"""
문서 서비스
문서 관련 비즈니스 로직을 담당하는 서비스 레이어
"""

import logging
from typing import Dict, Any
from app.models.search_engine import ContextualSearchEngine
from app.schemas.document import DocumentRequest
from app.schemas.common import StatusResponse
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class DocumentService:
    """문서 서비스 클래스"""
    
    def __init__(self, search_engine: ContextualSearchEngine):
        self.search_engine = search_engine
        self.settings = get_settings()
    
    async def add_document(self, request: DocumentRequest) -> StatusResponse:
        """새 문서 추가"""
        try:
            self.search_engine.index_document(
                doc_id=request.doc_id,
                title=request.title,
                content=request.content,
                category=request.category,
                tags=request.tags
            )
            
            return StatusResponse(
                success=True,
                message=f"문서 '{request.title}'이(가) 성공적으로 추가되었습니다.",
                status="document_added"
            )
            
        except Exception as e:
            logger.error(f"문서 추가 중 오류 발생: {e}")
            raise
    
    async def get_document(self, doc_id: str) -> Dict[str, Any]:
        """문서 조회"""
        try:
            # OpenSearch에서 문서 조회
            response = self.search_engine.client.get(
                index=self.settings.search_index_name,
                id=doc_id
            )
            
            return response['_source']
            
        except Exception as e:
            logger.error(f"문서 조회 중 오류 발생: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> StatusResponse:
        """문서 삭제"""
        try:
            self.search_engine.client.delete(
                index=self.settings.search_index_name,
                id=doc_id
            )
            
            return StatusResponse(
                success=True,
                message=f"문서 '{doc_id}'이(가) 성공적으로 삭제되었습니다.",
                status="document_deleted"
            )
            
        except Exception as e:
            logger.error(f"문서 삭제 중 오류 발생: {e}")
            raise 