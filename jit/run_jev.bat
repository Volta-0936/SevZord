@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_jev.ps1"
echo.
echo done. You can close this window.
pause
