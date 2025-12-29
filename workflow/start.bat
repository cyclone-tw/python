@echo off
chcp 65001 >nul
REM 工作區管理器啟動腳本 (Windows)

cd /d "%~dp0"

REM 檢查虛擬環境是否存在
if not exist "venv" (
    echo 🔧 首次執行，正在建立虛擬環境...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo ✅ 環境建立完成！
) else (
    call venv\Scripts\activate.bat
)

REM 啟動程式
python workspace_manager.py
pause
