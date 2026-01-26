# 公文智能處理系統 v1.1

基於 Google Gemini 2.0 Flash 的智能公文處理系統，提供自動分析、重命名、歸檔和 Google 整合功能。

## 最新更新 (2026-01-13)
- **模型升級**: 預設使用 `gemini-2.0-flash` (2025年推薦免費模型)。
- **掃描邏輯優化**: 僅掃描 `_print.pdf` 結尾的公文本文，並自動關聯同前綴的附件 (`_ATTACHn.pdf`)。
- **安全性增強**: 支援 `.env` 環境變數管理 API Key。

> **👋 第一次使用？** 請參考 [初始環境設定指南 (SETUP_GUIDE.md)](SETUP_GUIDE.md) 進行安裝與設定。

## 功能特色

### 🤖 AI 智能分析
- 使用 Google Gemini API 自動分析公文內容
- 提取關鍵資訊：主旨、重要日期、行動項目、聯絡人
- 智能建議檔案命名和歸檔位置

### 📁 智能檔案管理
- 自動重命名 PDF 檔案（格式：YYYY-MM-DD_主旨）
- 智能歸檔到建議的子目錄
- **自動搬移相關附件**：歸檔時會一併移動與公文關聯的所有附件
- 建立詳細的處理記錄

### 📅 Google 整合
- 根據公文內容自動建立 Google Calendar 事件
- 建立 Google Tasks 任務提醒
- 包含完整的公文資訊和截止日期

## 專案檔案結構說明

以下列出專案中各個檔案的用途與保留必要性：

### ✅ 核心檔案 (必須保留)

| 檔案/目錄 | 類別 | 必要性 | 用途說明 |
|:--- |:--- |:--- |:--- |
| **`app.py`** | 程式 | **核心** | 程式入口點 (Flask Web Server)，負責啟動網頁介面。 |
| **`config.py`** | 設定 | **核心** | 系統全域設定檔，包含路徑、模型參數等設定。 |
| **`.env`** | 設定 | **核心** | 存放敏感資訊 (API Key)，不會被上傳到版控。 |
| **`modules/`** | 程式 | **核心** | 包含所有功能模組 (`gemini_analyzer`, `file_manager` 等)。 |
| **`templates/`** | UI | **核心** | 存放網頁 HTML 模板 (`index.html`)。 |
| **`static/`** | UI | **核心** | 存放網頁 CSS 樣式與 icon (`style.css`)。 |
| **`requirements.txt`** | 設定 | **核心** | 定義專案所需的 Python 套件清單。 |

### 🔑 認證與暫存檔案 (視功能需求)

| 檔案 | 用途 | 必要性 | 詳細說明 |
|:--- |:--- |:--- |:--- |
| **`token.pickle`** | Google 登入憑證 | **高** | 儲存 Google 登入狀態。**若刪除，下次使用 Google 功能需重新登入**。 |
| **`credentials.json`** | Google OAuth 設定 | **高** | Google Cloud 下載的認證檔。若要使用 Calendar/Tasks 功能則必須存在。 |
| **`user_settings.json`** | 使用者偏好 | 中 | 記住上次掃描的路徑等 UI 設定。若刪除，設定會重置。 |
| **`__pycache__/`** | Python 快取 | 低 | 加速程式載入。可隨時刪除，程式執行時會自動重建。 |

### 📄 說明文件

| 檔案 | 用途 | 必要性 | 說明 |
|:--- |:--- |:--- |:--- |
| **`README.md`** | 專案說明 | 高 | 專案安裝、設定與使用手冊 (本文件)。 |
| **`DEVELOPMENT_LOG.md`**| 開發紀錄 | 中 | 記錄開發過程與問題解決方案。 |
| **`_deprecated_files/`**| 舊檔備份 | 低 | 存放已停用的舊程式碼與測試檔，可隨時清理。 |

---

## 安裝步驟

### 1. 安裝 Python 套件
```bash
pip install -r requirements.txt
```

### 2. 設定 Gemini API (使用 .env)
1. 前往 [Google AI Studio](https://aistudio.google.com/apikey) 取得 API Key
2. **重要：請務必在 Google Cloud Console 中啟用「帳單帳戶 (Billing Account)」，否則免費額度無法使用 (會出現 limit: 0 錯誤)。**
3. 複製 `.env.example` 為 `.env`：
   - Windows: `copy .env.example .env`
   - Mac/Linux: `cp .env.example .env`
4. 編輯 `.env` 檔案，填入你的 API Key：
```ini
GEMINI_API_KEY=你的_API_KEY
```

### 3. 設定 Google API（可選）
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Calendar API 和 Google Tasks API
4. 建立 OAuth 2.0 憑證
5. 下載 `credentials.json` 到專案根目錄

### 4. 設定路徑
編輯 `config.py` 中的路徑設定：
```python
'paths': {
    'scan_directory': r"你的掃描目錄路徑",
    'target_directory': r"你的歸檔目錄路徑",
}
```

## 使用方法

### 啟動 Web UI
```bash
python app.py
```
啟動後請使用瀏覽器訪問 [http://127.0.0.1:5001](http://127.0.0.1:5001)

### 使用流程
1. **重新掃描**: 點擊按鈕掃描目錄中的 `_print.pdf` 公文
2. **AI 分析**: 點擊「開始分析」或「批次分析全部」
3. **確認/編輯**: 查看分析結果，可編輯主旨或日期
4. **執行動作**: 選擇是否建立日曆/任務，並勾選歸檔
5. **執行選定項目**: 系統將自動歸檔文件與附件，並同步至 Google

## 常見問題

### Q: 出現 `429 You exceeded your current quota ... limit: 0` 錯誤？
A: 這是因為 Google 新政策要求即使是免費額度，也必須在專案中連結帳單帳戶。請前往 Google Cloud Console 啟用帳單功能。

### Q: 找不到公文？
A: 系統目前設定僅掃描檔名結尾為 `_print.pdf` 的檔案作為公文本文。請確認您的檔案命名格式。

## 系統需求
- Python 3.8+
- Windows (推薦) / macOS / Linux
- 穩定的網路連線（Gemini API）
- Google 帳戶（Google 整合功能）
