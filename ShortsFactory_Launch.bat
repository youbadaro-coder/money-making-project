@echo off
title 쇼츠 팩토리 스튜디오 실행기
echo ==========================================
echo   쇼츠 팩토리 스튜디오를 시작합니다...
echo ==========================================
echo.

:: 서버가 이미 실행 중인지 확인
netstat -ano | findstr :5000 > nul
if %errorlevel% equ 0 (
    echo 서버가 이미 실행 중입니다. 대시보드를 엽니다...
) else (
    echo 백엔드 서버를 시작하는 중...
    set "PROJECT_DIR=%~dp0"
    start /b "" "%PROJECT_DIR%.bin\python\python.exe" "%PROJECT_DIR%server.py"
    timeout /t 3 > nul
)

echo 스튜디오 제어판을 브라우저에서 여는 중...
start http://localhost:5000

echo.
echo ==========================================
echo   STAY CRAZY, STAY SHORTS! (의장님 가즈아!)
echo ==========================================
echo.
pause
