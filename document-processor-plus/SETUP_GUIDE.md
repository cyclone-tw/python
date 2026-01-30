# 公文智能處理系統 - 初始環境設定指南

本指南專為**第一次使用本系統**的使用者設計，即使沒有任何程式背景，只要按照步驟操作，就能完成環境建置。

---

## 📋 準備工作清單 (Checklist)

在開始之前，你需要準備：
1. 一個 **Google 帳號** (建議使用個人帳號，公司帳號可能會有限制)
2. 一張 **信用卡** (用於啟用 Google Cloud 帳單，免費額度內不會扣款)
3. 電腦管理員權限 (用於安裝軟體)

---

## 第一階段：安裝基礎軟體 (Python)

本系統是使用 Python 語言編寫，因此必須先安裝 Python。

1. **下載 Python**
   - 前往 [Python 官網](https://www.python.org/downloads/)
   - 下載最新版的 **Python 3.x** (例如 3.12 或 3.11)

2. **安裝 Python (重要步驟！)**
   - 執行下載的安裝檔。
   - **⚠️ 務必勾選底部的 "Add python.exe to PATH"** (這一步非常重要，沒勾選後續會無法執行指令)。
   - 點擊 "Install Now" 完成安裝。

3. **驗證安裝**
   - 按 `Win + R`，輸入 `cmd`，按 Enter 開啟命令提示字元。
   - 輸入 `python --version`，如果有出現版本號 (例如 `Python 3.12.1`) 代表安裝成功。

---

## 第二階段：申請 Gemini API Key (AI 核心功能)

這是讓系統擁有「大腦」的關鍵步驟。

1. **前往 Google AI Studio**
   - 點擊連結：[https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
   - 登入你的 Google 帳號。

2. **啟用帳單 (Billing) - 必做！**
   - Google 目前規定，即使是免費額度，也必須連結 Google Cloud 專案的帳單帳戶。
   - 點擊畫面上的提示啟用 Billing，或前往 [Google Cloud Console Billing](https://console.cloud.google.com/billing) 設定。
   - **放心：** Gemini API 有提供每日免費額度 (每天 1,500 次請求)，本系統不會超過此用量，因此**不會產生費用**。

3. **建立 API Key**
   - 在 AI Studio 點擊 **"Create API Key"**。
   - 選擇 (或建立) 剛才有設定帳單的 Google Cloud 專案。
   - 複製產生出來的 API Key (一長串亂碼，以 `AIza` 開頭)。

4. **設定 API Key**
   - 回到本系統的資料夾。
   - 找到 `.env.example` 檔案，複製一份並改名為 `.env`。
   - 用記事本開啟 `.env`，將你的 Key 填入：
     ```ini
     GEMINI_API_KEY=AIzaSyB... (貼上你的Key)
     ```
   - 儲存檔案。

---

## 第三階段：申請 Google Calendar/Tasks 權限 (行事曆整合)

如果你希望系統能幫你自動建立行事曆和待辦事項，需要申請這個權限。**如果你不需要此功能，可以跳過此階段。**

1. **建立 Google Cloud 專案**
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)。
   - 點擊左上角專案選單 -> "建立新專案" -> 輸入名稱 (如 "DocHelper") -> 建立。

2. **啟用 API**
   - 在搜尋列輸入 **"Google Calendar API"** -> 點擊進入 -> 按下 **"啟用"**。
   - 再次搜尋 **"Google Tasks API"** -> 點擊進入 -> 按下 **"啟用"**。

3. **設定 OAuth 同意畫面**
   - 左側選單點選 **"API 和服務"** -> **"OAuth 同意畫面"**。
   - User Type 選擇 **"External" (外部)** -> 建立。
   - 填寫 App Name (如 "公文小幫手") 和 User Support Email (你的信箱) -> 儲存並繼續。
   - **"測試使用者" (Test Users)** 步驟：點擊 "Add Users"，**輸入你自己的 Gmail** (這一步很重要，因為你的 App 尚未發布，只有加入清單的人能用)。

4. **下載憑證 (credentials.json)**
   - 左側選單點選 **"憑證" (Credentials)**。
   - 點擊上方 **"建立憑證"** -> **"OAuth 用戶端 ID"**。
   - 應用程式類型選 **"Desktop app" (桌面應用程式)**。
   - 建立後，會彈出視窗，點擊 **"下載 JSON"** (下載圖示)。
   - 將下載的檔案改名為 `credentials.json`，並放入本系統的資料夾中。

---

## 第四階段：啟動系統

恭喜！環境都設定好了，現在可以開始使用。

1. **安裝系統依賴套件**
   - 在系統資料夾按右鍵 -> "在終端機開啟" (或用 cmd `cd` 到該目錄)。
   - 執行指令：
     ```bash
     pip install -r requirements.txt
     ```
   - 等待安裝完成。

2. **執行程式**
   - 執行指令：
     ```bash
     python app.py
     ```
   - 如果看到 `Running on http://127.0.0.1:5001` 代表成功啟動。

3. **開始使用**
   - 打開瀏覽器，輸入 `http://127.0.0.1:5001`。
   - 第一次使用 Google 整合功能時，會彈出 Google 登入視窗，請選擇帳號並按「繼續」直到授權完成。

---

## 常見問題 (Q&A)

**Q: 執行 `python` 指令時顯示「不是內部或外部命令」？**
A: 這通常是因為安裝 Python 時沒有勾選 "Add to PATH"。請重新安裝 Python 並確保勾選該選項。

**Q: Gemini API 出現 `limit: 0` 錯誤？**
A: 這是因為你的 Google Cloud 專案沒有啟用帳單 (Billing)。請參考第二階段步驟啟用。

**Q: Google 登入時顯示「Google hasn't verified this app」？**
A: 這是正常的，因為你是用自己的測試專案。直接點擊左下角的 **"Advanced" (進階)** -> **"Go to ... (unsafe)"** 即可繼續。
