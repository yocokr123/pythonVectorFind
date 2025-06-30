@echo off
echo ========================================
echo 🔍 pythonVectorSearch - OpenSearch 시작
echo ========================================

echo OpenSearch 컨테이너를 시작하고 있습니다...

REM 기존 컨테이너가 있다면 중지하고 삭제
docker stop opensearch 2>nul
docker rm opensearch 2>nul

REM OpenSearch 컨테이너 실행
docker run -d ^
  --name opensearch ^
  -p 9200:9200 ^
  -p 9600:9600 ^
  -e "discovery.type=single-node" ^
  -e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" ^
  opensearchproject/opensearch:latest

if %errorlevel% equ 0 (
    echo.
    echo ✅ OpenSearch가 성공적으로 시작되었습니다!
    echo.
    echo 📍 접속 정보:
    echo    - URL: http://localhost:9200
    echo    - 포트: 9200
    echo.
    echo ⏳ 서버가 완전히 시작될 때까지 잠시 기다려주세요 (약 30초)
    echo.
    echo 🔍 상태 확인: http://localhost:9200/_cluster/health
    echo.
    echo 🚀 이제 pythonVectorSearch를 실행할 수 있습니다:
    echo    python main.py
    echo.
    echo 🛑 OpenSearch 중지: docker stop opensearch
) else (
    echo.
    echo ❌ OpenSearch 시작 중 오류가 발생했습니다.
    echo.
    echo 🔧 문제 해결:
    echo    1. Docker가 설치되어 있고 실행 중인지 확인
    echo    2. 포트 9200이 사용 가능한지 확인
    echo    3. 인터넷 연결 상태 확인
)

pause 