# 開發紀錄 (Development Log)

## 2026-01-13 開發與除錯紀錄

### 1. 系統啟動與初始化優化
- **問題**: 應用程式啟動時「Gemini API 初始化成功」訊息出現兩次，且取消 Google 認證後無法進入 Web UI。
- **原因**: Flask 在 debug 模式下的 Watchdog 機制導致程式載入兩次。
- **解決**: 
  - 修改 `app.py`，實作延遲初始化 (`init_modules`)。
  - 加入 `WERKZEUG_RUN_MAIN` 環境變數檢查，確保只在主程序中初始化一次。
  - 調整 `use_reloader=False` 設定（視情況調整）。

### 2. 掃描邏輯變更
- **需求**: 只需掃描公文本文 (`_print.pdf`)，並自動關聯附件 (`_ATTACHn.pdf`)。
- **修改**:
  - 更新 `app.py` 中的 `scan_docs` 函式。
  - 邏輯改為搜尋 `*_print.pdf`，並解析前綴來尋找對應的 `*_ATTACH*.pdf`。
  - 更新前端 `index.html` 顯示邏輯，在卡片上標示「公文本文」與「附件數量」。
  - 更新歸檔 API (`/api/archive`) 與前端呼叫，確保歸檔時會一併搬移附件。

### 3. Gemini 模型與 API 設定更新
- **需求**: 檢查免費額度並更新模型。
- **修改**:
  - `config.py` 更新模型為 `gemini-2.0-flash` (2025 年推薦免費模型)。
  - (試錯過程): 曾短暫嘗試 `gemini-1.5-flash`，後確認 `2.0` 為新標準。

### 4. API Key 安全性與環境變數
- **需求**: 將 API Key 移出程式碼，改用 `.env` 管理。
- **修改**:
  - 建立 `.env` (存放真實 Key) 與 `.env.example` (範例)。
  - 更新 `.gitignore` 排除 `.env`。
  - 在 `requirements.txt` 加入 `python-dotenv`。
  - 更新 `config.py` 使用 `os.getenv` 讀取 `GEMINI_API_KEY`。

### 5. API Quota 限制除錯 (今日重點)
- **問題**: 即使更換新的 API Key，仍持續出現 `429 You exceeded your current quota ... limit: 0` 錯誤。
- **試錯分析**:
  - 初步懷疑是舊 Key 額度用完 -> 更換新 Key (未解決)。
  - 懷疑程式未讀取到新 Key -> 改用 `.env` 並確認載入成功 (未解決)。
  - **最終原因確認**: Google 自 2024/2025 年起的新政策，要求 **Google AI Studio / Cloud Project 必須連結「帳單帳戶 (Billing Account)」** 才能啟用免費額度。若未綁定帳單，額度上限 (Limit) 會被強制設為 0。
- **解決方案**: 
  - 必須前往 Google Cloud Console 或 AI Studio 啟用 Billing (即使使用免費層級也需綁定)。

---

## 待辦事項 / Next Steps
- [ ] 使用者需自行前往 Google 後台綁定帳單帳戶以解除 API 限制。
- [ ] 確認歸檔功能在附件多的情況下運作正常。
