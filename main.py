"""
FastAPI 메인 애플리케이션
pythonVectorSearch - OpenSearch와 임베딩을 이용한 강력한 문맥검색 API
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config.settings import get_settings
from app.api import api_router
from app.core.dependencies import get_search_engine
from app.models.data import load_sample_data

# 설정 로드
settings = get_settings()

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    logger.info("애플리케이션 시작 중...")
    
    try:
        # 검색 엔진 초기화
        search_engine = get_search_engine()
        
        # 인덱스 생성
        search_engine.delete_index()
        search_engine.create_index()
        
        # 샘플 데이터 로드
        logger.info("샘플 데이터를 로드하고 있습니다...")
        sample_docs = load_sample_data()
        search_engine.bulk_index_documents(sample_docs)
        
        logger.info("애플리케이션 초기화 완료")
        
    except Exception as e:
        logger.error(f"애플리케이션 초기화 실패: {e}")
        raise
    
    yield
    
    # 종료 시 실행
    logger.info("애플리케이션 종료 중...")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    description="pythonVectorSearch - OpenSearch와 임베딩을 이용한 강력한 문맥검색 API",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# API 라우터 등록
app.include_router(api_router)


# 전역 예외 처리
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP 예외 처리"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 검증 예외 처리"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "요청 데이터 검증 실패",
            "error_code": "VALIDATION_ERROR",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 처리"""
    logger.error(f"예상치 못한 오류 발생: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "서버 내부 오류가 발생했습니다.",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


# 헬스 체크 엔드포인트
@app.get("/health", tags=["health"])
async def health_check():
    """헬스 체크"""
    return {
        "success": True,
        "message": "서버가 정상적으로 동작하고 있습니다.",
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env
    }


# 루트 엔드포인트
@app.get("/", tags=["root"])
async def root():
    """루트 엔드포인트"""
    return {
        "success": True,
        "message": f"{settings.app_name}에 오신 것을 환영합니다! 🚀 Hot Reload 테스트 성공!",
        "version": settings.app_version,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_reload,
        log_level=settings.server_log_level
    ) 