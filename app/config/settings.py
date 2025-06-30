"""
애플리케이션 설정
현업에서 사용하는 Pydantic Settings 패턴
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 애플리케이션 기본 설정
    app_name: str = Field(default="pythonVectorSearch")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # 서버 설정
    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=8000)
    server_reload: bool = Field(default=True)
    server_log_level: str = Field(default="info")
    
    # OpenSearch 설정
    opensearch_host: str = Field(default="localhost")
    opensearch_port: int = Field(default=9200)
    opensearch_username: Optional[str] = Field(default=None)
    opensearch_password: Optional[str] = Field(default=None)
    opensearch_use_ssl: bool = Field(default=False)
    opensearch_verify_certs: bool = Field(default=False)
    
    # 검색 엔진 설정
    search_index_name: str = Field(default="contextual_documents")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    
    # CORS 설정
    cors_allow_origins: List[str] = Field(default=["*"])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])
    
    # 로깅 설정
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # 검색 기본값 설정
    default_search_size: int = Field(default=10)
    default_semantic_weight: float = Field(default=0.7)
    default_keyword_weight: float = Field(default=0.3)
    
    # 성능 설정
    max_search_size: int = Field(default=100)
    request_timeout: int = Field(default=30)
    
    # 보안 설정
    secret_key: str = Field(default="your-secret-key-here")
    access_token_expire_minutes: int = Field(default=30)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.app_env.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """운영 환경 여부"""
        return self.app_env.lower() == "production"
    
    @property
    def is_test(self) -> bool:
        """테스트 환경 여부"""
        return self.app_env.lower() == "test"


# 전역 설정 인스턴스
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """설정 인스턴스를 반환합니다 (싱글톤 패턴)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# 환경별 설정 클래스들
class DevelopmentSettings(Settings):
    """개발 환경 설정"""
    debug: bool = True
    server_reload: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    """운영 환경 설정"""
    debug: bool = False
    server_reload: bool = False
    log_level: str = "WARNING"
    cors_allow_origins: List[str] = ["https://yourdomain.com"]  # 실제 도메인으로 변경


class TestSettings(Settings):
    """테스트 환경 설정"""
    server_port: int = 8001
    opensearch_port: int = 9201
    search_index_name: str = "test_contextual_documents"
    debug: bool = True


def get_settings_by_env(env: Optional[str] = None) -> Settings:
    """환경에 따른 설정 반환"""
    if env is None:
        env = os.getenv("APP_ENV", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "test":
        return TestSettings()
    else:
        return DevelopmentSettings() 