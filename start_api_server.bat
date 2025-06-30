@echo off
echo ========================================
echo pythonVectorSearch API 서버 시작
echo ========================================

REM 가상환경 활성화
echo 가상환경을 활성화하고 있습니다...
call venv\Scripts\activate.bat

REM 현재 디렉토리 확인
echo 현재 디렉토리: %CD%

REM Python 경로 확인
echo Python 경로: %PYTHONPATH%

REM 서버 시작
echo API 서버를 시작합니다...
echo 서버 주소: http://localhost:8000
echo API 문서: http://localhost:8000/docs
echo ReDoc 문서: http://localhost:8000/redoc
echo.

python main.py

pause 