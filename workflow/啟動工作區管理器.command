#!/bin/bash
# 工作區管理器啟動腳本 (macOS)
# 雙擊此檔案即可執行

cd "$(dirname "$0")"

echo "🚀 啟動工作區管理器..."
echo ""

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3！請先安裝 Python。"
    echo "   執行: brew install python@3.12 python-tk@3.12"
    echo ""
    read -p "按 Enter 關閉..."
    exit 1
fi

# 檢查虛擬環境是否存在
if [ ! -d "venv" ]; then
    echo "🔧 首次執行，正在建立虛擬環境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ 環境建立完成！"
    echo ""
else
    source venv/bin/activate
fi

# 啟動程式
python workspace_manager.py

# 如果程式異常結束，暫停
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 程式執行發生錯誤"
    read -p "按 Enter 關閉..."
fi
