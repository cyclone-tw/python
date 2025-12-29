#!/bin/bash
# 工作區管理器啟動腳本 (macOS / Linux)

cd "$(dirname "$0")"

# 檢查虛擬環境是否存在
if [ ! -d "venv" ]; then
    echo "🔧 首次執行，正在建立虛擬環境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ 環境建立完成！"
else
    source venv/bin/activate
fi

# 啟動程式
python workspace_manager.py
