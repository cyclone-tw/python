@echo off
chcp 65001 >nul
title 工作區管理器
REM ========================================
REM 工作區管理器啟動腳本 (Windows)
REM 雙擊此檔案即可執行
REM ========================================

cd /d "%~dp0"

echo.
echo ========================================
echo   🚀 工作區管理器啟動中...
echo ========================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 錯誤：找不到 Python！
    echo.
    echo 請先安裝 Python：
    echo   1. 前往 https://www.python.org/downloads/
    echo   2. 下載並安裝 Python 3.9+
    echo   3. 安裝時務必勾選 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM 檢查虛擬環境是否存在
if not exist "venv" (
    echo 🔧 首次執行，正在建立虛擬環境...
    echo.
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ 建立虛擬環境失敗！
        pause
        exit /b 1
    )
    
    call venv\Scripts\activate.bat
    
    echo 📦 正在安裝依賴套件...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 安裝依賴失敗！
        pause
        exit /b 1
    )
    
    echo.
    echo ✅ 環境建立完成！
    echo.
) else (
    call venv\Scripts\activate.bat
)

REM 啟動程式
echo 🖥️ 正在啟動視窗...
python workspace_manager.py

REM 如果程式異常結束
if %errorlevel% neq 0 (
    echo.
    echo ❌ 程式執行發生錯誤 (錯誤碼: %errorlevel%)
    echo.
    pause
)
