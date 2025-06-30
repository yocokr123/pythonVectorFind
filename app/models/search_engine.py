"""
OpenSearch를 이용한 임베딩 기반 문맥검색 엔진
이 클래스는 문서를 임베딩하여 벡터로 변환하고 문맥기반 검색을 수행합니다.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch, helpers
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer
import torch

# 로깅 설정 (프로그램 실행 중 발생하는 정보를 기록)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextualSearchEngine:
    """
    임베딩 기반 문맥검색 엔진 클래스
    
    이 클래스는 다음과 같은 기능을 제공합니다:
    1. OpenSearch에 연결
    2. 문서를 임베딩하여 벡터로 변환
    3. 문맥기반 벡터 유사도 검색
    4. 하이브리드 검색 (키워드 + 벡터)
    """
    
    def __init__(self, host='localhost', port=9200, username=None, password=None, 
                 model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """
        검색 엔진 초기화
        
        Args:
            host (str): OpenSearch 서버 주소
            port (int): OpenSearch 포트 번호
            username (str): 사용자 이름 (보안이 설정된 경우)
            password (str): 비밀번호 (보안이 설정된 경우)
            model_name (str): 사용할 임베딩 모델명
        """
        self.host = host
        self.port = port
        self.model_name = model_name
        
        # 임베딩 모델 로드
        logger.info(f"임베딩 모델 '{model_name}'을 로드하고 있습니다...")
        self.embedding_model = SentenceTransformer(model_name)
        self.vector_dimension = self.embedding_model.get_sentence_embedding_dimension()
        logger.info(f"임베딩 모델 로드 완료 (벡터 차원: {self.vector_dimension})")
        
        # OpenSearch 연결 설정
        if username and password:
            self.client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                http_auth=(username, password),
                use_ssl=True,
                verify_certs=False,
                ssl_show_warn=False
            )
        else:
            self.client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                http_compress=True,
                timeout=30
            )
        
        self.index_name = 'contextual_documents'
        logger.info(f"OpenSearch에 연결되었습니다: {host}:{port}")
    
    def delete_index(self):
        """
        기존 인덱스를 삭제합니다.
        """
        if self.client.indices.exists(index=self.index_name):
            self.client.indices.delete(index=self.index_name)
            logger.info(f"인덱스 '{self.index_name}'가 삭제되었습니다.")
        else:
            logger.info(f"인덱스 '{self.index_name}'가 존재하지 않습니다.")
    
    def create_index(self):
        """
        벡터 검색을 위한 인덱스(데이터베이스)를 생성합니다.
        """
        # 인덱스가 이미 존재하는지 확인
        if self.client.indices.exists(index=self.index_name):
            logger.info(f"인덱스 '{self.index_name}'가 이미 존재합니다.")
            return
        
        # 벡터 검색을 위한 인덱스 설정 (매핑)
        index_settings = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "title_vector": {
                        "type": "knn_vector",
                        "dimension": self.vector_dimension
                    },
                    "content_vector": {
                        "type": "knn_vector",
                        "dimension": self.vector_dimension
                    },
                    "category": {
                        "type": "keyword"
                    },
                    "tags": {
                        "type": "keyword"
                    },
                    "created_at": {
                        "type": "date"
                    }
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "knn": True,
                "knn.algo_param.ef_search": 100
            }
        }
        
        # 인덱스 생성
        self.client.indices.create(index=self.index_name, body=index_settings)
        logger.info(f"벡터 검색 인덱스 '{self.index_name}'가 생성되었습니다.")
    
    def _generate_embeddings(self, text: str) -> List[float]:
        """
        텍스트를 임베딩 벡터로 변환합니다.
        
        Args:
            text (str): 임베딩할 텍스트
            
        Returns:
            List[float]: 임베딩 벡터
        """
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"임베딩 생성 중 오류: {e}")
            return [0.0] * self.vector_dimension
    
    def index_document(self, doc_id: str, title: str, content: str, 
                      category: Optional[str] = '', tags: Optional[List[str]] = None, created_at: Optional[str] = None):
        """
        문서를 임베딩하여 인덱스에 저장합니다.
        
        Args:
            doc_id (str): 문서 고유 ID
            title (str): 문서 제목
            content (str): 문서 내용
            category (str): 문서 카테고리
            tags (List[str]): 문서 태그들
            created_at (str): 생성일시(ISO 포맷)
        """
        # 제목과 내용을 임베딩
        title_vector = self._generate_embeddings(title)
        content_vector = self._generate_embeddings(content)
        
        document = {
            "title": title,
            "content": content,
            "title_vector": title_vector,
            "content_vector": content_vector,
            "category": category or '',
            "tags": tags or [],
            "created_at": created_at or datetime.utcnow().isoformat()
        }
        
        try:
            self.client.index(
                index=self.index_name,
                id=doc_id,
                body=document
            )
            logger.info(f"문서 '{title}'이(가) 임베딩과 함께 인덱스에 저장되었습니다.")
        except Exception as e:
            logger.error(f"문서 저장 중 오류 발생: {e}")
    
    def bulk_index_documents(self, documents: List[Dict[str, Any]]):
        """
        여러 문서를 임베딩하여 한 번에 인덱스에 저장합니다.
        
        Args:
            documents (List[Dict]): 저장할 문서들의 리스트
        """
        actions = []
        for doc in documents:
            # 제목과 내용을 임베딩
            title_vector = self._generate_embeddings(doc.get("title", ""))
            content_vector = self._generate_embeddings(doc.get("content", ""))
            
            action = {
                "_index": self.index_name,
                "_id": doc.get("id"),
                "_source": {
                    "title": doc.get("title"),
                    "content": doc.get("content"),
                    "title_vector": title_vector,
                    "content_vector": content_vector,
                    "category": doc.get("category", ''),
                    "tags": doc.get("tags", []),
                    "created_at": doc.get("created_at") or datetime.utcnow().isoformat()
                }
            }
            actions.append(action)
        
        try:
            helpers.bulk(self.client, actions)
            logger.info(f"{len(documents)}개의 문서가 임베딩과 함께 성공적으로 저장되었습니다.")
        except Exception as e:
            logger.error(f"대량 저장 중 오류 발생: {e}")
    
    def semantic_search(self, query: str, size: int = 10, category: Optional[str] = '') -> List[Dict]:
        """
        임베딩 기반 문맥검색을 수행합니다.
        
        Args:
            query (str): 검색 쿼리
            size (int): 반환할 결과 개수
            category (str): 특정 카테고리로 검색 범위 제한
            
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        # 쿼리를 임베딩
        query_vector = self._generate_embeddings(query)
        
        # 벡터 검색 쿼리 구성
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "content_vector": {
                                    "vector": query_vector,
                                    "k": size
                                }
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                }
            },
            "size": size
        }
        
        # 카테고리 필터 추가
        if category:
            search_body["query"]["bool"]["filter"] = [
                {"term": {"category": category}}
            ]
        
        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            # 검색 결과 처리
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'title': hit['_source']['title'],
                    'content': hit['_source']['content'],
                    'category': hit['_source'].get('category'),
                    'tags': hit['_source'].get('tags', []),
                    'highlights': hit.get('highlight', {})
                }
                results.append(result)
            
            logger.info(f"문맥검색 '{query}' 결과: {len(results)}개 발견")
            return results
            
        except Exception as e:
            logger.error(f"문맥검색 중 오류 발생: {e}")
            return []
    
    def hybrid_search(self, query: str, size: int = 10, category: Optional[str] = '', 
                     semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> List[Dict]:
        """
        하이브리드 검색 (키워드 + 문맥)을 수행합니다.
        
        Args:
            query (str): 검색 쿼리
            size (int): 반환할 결과 개수
            category (str): 특정 카테고리로 검색 범위 제한
            semantic_weight (float): 문맥검색 가중치
            keyword_weight (float): 키워드검색 가중치
            
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        # 쿼리를 임베딩
        query_vector = self._generate_embeddings(query)
        
        # 하이브리드 검색 쿼리 구성
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "content"],
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                                "boost": keyword_weight
                            }
                        },
                        {
                            "knn": {
                                "content_vector": {
                                    "vector": query_vector,
                                    "k": size,
                                    "boost": semantic_weight
                                }
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                }
            },
            "size": size
        }
        
        # 카테고리 필터 추가
        if category:
            search_body["query"]["bool"]["filter"] = [
                {"term": {"category": category}}
            ]
        
        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            # 검색 결과 처리
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'title': hit['_source']['title'],
                    'content': hit['_source']['content'],
                    'category': hit['_source'].get('category'),
                    'tags': hit['_source'].get('tags', []),
                    'highlights': hit.get('highlight', {})
                }
                results.append(result)
            
            logger.info(f"하이브리드 검색 '{query}' 결과: {len(results)}개 발견")
            return results
            
        except Exception as e:
            logger.error(f"하이브리드 검색 중 오류 발생: {e}")
            return []
    
    def search_by_tags(self, tags: Optional[List[str]], size: int = 10) -> List[Dict]:
        """
        태그를 기반으로 검색합니다.
        
        Args:
            tags (List[str]): 검색할 태그들
            size (int): 반환할 결과 개수
            
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        search_body = {
            "query": {
                "terms": {
                    "tags": tags
                }
            },
            "size": size
        }
        
        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'title': hit['_source']['title'],
                    'content': hit['_source']['content'],
                    'category': hit['_source'].get('category'),
                    'tags': hit['_source'].get('tags', [])
                }
                results.append(result)
            
            logger.info(f"태그 {tags} 검색 결과: {len(results)}개 발견")
            return results
            
        except Exception as e:
            logger.error(f"태그 검색 중 오류 발생: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        인덱스 통계 정보를 반환합니다.
        
        Returns:
            Dict: 통계 정보
        """
        try:
            stats = self.client.indices.stats(index=self.index_name)
            index_stats = stats['indices'][self.index_name]
            
            return {
                'total_documents': index_stats['total']['docs']['count'],
                'index_size': index_stats['total']['store']['size_in_bytes'],
                'index_name': self.index_name,
                'embedding_model': self.model_name,
                'vector_dimension': self.vector_dimension
            }
        except Exception as e:
            logger.error(f"통계 정보 조회 중 오류 발생: {e}")
            return {} 