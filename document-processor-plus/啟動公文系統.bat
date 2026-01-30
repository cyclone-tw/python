@echo off
chcp 65001 >nul
echo ========================================
echo 公文智能處理系統 啟動中...
echo ========================================
echo.

cd /d "%~dp0"
venv\Scripts\python.exe app.py

pause
