# 🗂️ 工作區管理器 (Workspace Manager)

一個視覺化的多重工作區切換工具，讓你可以一鍵開啟多個資料夾、檔案和網址。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 功能特色

- 🎨 **Material Design UI** - 現代化深色主題介面
- 📁 **一鍵啟動** - 同時開啟工作區內所有資料夾、檔案、網址
- ➕ **視覺化編輯** - 直接在介面新增/編輯/刪除工作區
- 💾 **JSON 持久化** - 設定自動儲存，重啟後保留
- 📊 **項目統計** - 顯示每個工作區的資料夾/檔案/網址數量

---

## 🚀 快速開始

### 前置需求

| 系統 | 需安裝項目 |
|------|-----------|
| **Windows** | Python 3.9+ (含 tkinter) |
| **macOS** | Python 3.9+ + python-tk |
| **Linux** | Python 3.9+ + python3-tk |

### 安裝步驟

#### 🍎 macOS

```bash
# 1. 安裝 Homebrew (如果尚未安裝)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安裝 Python 和 Tkinter
brew install python@3.12 python-tk@3.12

# 3. 下載專案後執行
chmod +x start.sh
./start.sh
```

#### 🪟 Windows

```powershell
# 1. 下載並安裝 Python
#    前往 https://www.python.org/downloads/
#    ⚠️ 安裝時務必勾選 "Add Python to PATH" 和 "tcl/tk and IDLE"

# 2. 下載專案後，雙擊執行
start.bat
```

#### 🐧 Linux (Ubuntu/Debian)

```bash
# 1. 安裝 Python 和 Tkinter
sudo apt update
sudo apt install python3 python3-venv python3-tk

# 2. 下載專案後執行
chmod +x start.sh
./start.sh
```

---

## 📂 專案結構

```
workflow/
├── workspace_manager.py   # 主程式
├── workspaces.json        # 工作區設定檔 (自動生成)
├── requirements.txt       # Python 依賴
├── start.sh              # macOS/Linux 啟動腳本
├── start.bat             # Windows 啟動腳本
├── README.md             # 說明文件
└── DEVLOG.md             # 開發日誌
```

---

## 🛠️ 設定檔格式

`workspaces.json` 儲存所有工作區設定：

```json
{
  "工作區名稱": {
    "folders": ["/path/to/folder1", "/path/to/folder2"],
    "files": ["/path/to/file.txt"],
    "urls": ["https://github.com", "https://notion.so"]
  }
}
```

---

## 📸 截圖

| 主介面 | 編輯工作區 |
|--------|-----------|
| 卡片式工作區列表 | 可滾動的多行輸入 |

---

## ❓ 常見問題

### Q: 出現 `No module named '_tkinter'`
**A:** 需要安裝 Tkinter GUI 套件：
- macOS: `brew install python-tk@3.12`
- Linux: `sudo apt install python3-tk`
- Windows: 重新安裝 Python 時勾選 "tcl/tk and IDLE"

### Q: 啟動時找不到 Python
**A:** 確認 Python 已加入系統 PATH：
- Windows: 重新安裝 Python 並勾選 "Add Python to PATH"
- macOS/Linux: 執行 `which python3` 確認路徑

### Q: 如何備份我的工作區設定？
**A:** 只需備份 `workspaces.json` 檔案即可。

---

## 📄 授權

MIT License - 自由使用、修改、分發。
