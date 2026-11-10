@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ========================================================
echo [KBO 대시보드] GitHub Pages 업데이트 Push 진행 중...
echo ========================================================
echo.
git push origin main
if errorlevel 1 (
    echo.
    echo [알림] 일반 푸시 실패 시 강제 푸시를 시도합니다...
    git push origin main --force
)
echo.
echo ========================================================
echo 업로드 완료! 이제 GitHub Pages에서 사이트가 호스팅됩니다.
echo ========================================================
pause