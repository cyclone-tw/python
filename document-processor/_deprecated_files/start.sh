#!/bin/bash

# 設定虛擬環境名稱
VENV_NAME="venv"

# 檢查虛擬環境是否存在
if [ ! -d "$VENV_NAME" ]; then
    echo "正在建立虛擬環境..."
    python3 -m venv $VENV_NAME
fi

# 啟動虛擬環境
source $VENV_NAME/bin/activate

# 安裝依賴
echo "正在檢查並安裝依賴套件..."
pip install -r requirements.txt

# 啟動應用程式
echo "啟動公文智能處理系統 Web UI..."
echo "請在瀏覽器開啟: http://localhost:5001"
python3 app.py
