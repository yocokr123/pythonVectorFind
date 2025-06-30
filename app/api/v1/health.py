"""
헬스체크 API 엔드포인트
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.common import StatusResponse
from app.core.dependencies import get_search_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=StatusResponse, summary="헬스체크")
async def health_check(search_engine = Depends(get_search_engine)) -> StatusResponse:
    """
    서버 상태를 확인합니다.
    """
    try:
        # OpenSearch 연결 확인
        search_engine.client.cluster.health()
        
        return StatusResponse(
            success=True,
            message="서버가 정상적으로 동작하고 있습니다.",
            status="healthy"
        )
    except Exception as e:
        logger.error(f"헬스체크 API 오류: {e}")
        raise HTTPException(status_code=503, detail=str(e)) 