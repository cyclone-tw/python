# 解決 Google 憑證經常失效的方法

您遇到的「憑證失效」問題，通常是因為 Google Cloud Project 的 OAuth 同意畫面（Consent Screen）處於 **"Testing"（測試）** 狀態。

## 為什麼會這樣？
在 "Testing" 狀態下，Google 為了安全，會讓授權憑證（Refresh Token）在 **7天後自動過期**。這意味著每週您都需要刪除 `token.pickle` 並重新登入。

## 永久解決方案

要解決此問題，您需要將專案狀態改為 **"Production"（正式發布）**。

### 請依照以下步驟操作：

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)。
2. 選擇您的專案。
3. 在左側選單點選 **API 和服務 (APIs & Services)** > **OAuth 同意畫面 (OAuth consent screen)**。
4. 在「發布狀態 (Publishing status)」區域下，點擊 **[PUBLISH APP] (發布應用程式)** 按鈕。
5. Google 會顯示一個警告視窗，說明進入生產階段的影響。點擊 **確認**。
   - **注意**：如果您使用的是免費 Gmail 帳號 (@gmail.com)，且使用者類型是 "External" (外部)，變成 Production 後，登入時可能會看到「Google 尚未驗證此應用程式」的警告畫面。
   - 這是正常的！因為您是自己使用，**不需要**提交 Google 驗證。
   - 在登入時，點擊 **[進階] (Advanced)** > **[前往... (不安全)] (Go to ... (unsafe))** 即可完成授權。

### 完成後的好處：
一旦狀態變為 "Production"，您的 Refresh Token 將**不會**在 7 天後過期（除非您更改密碼或主動撤銷授權）。您將可以長期使用而無需頻繁重新登入。

## 檢查程式碼設定
目前的程式碼已經包含了自動刷新憑證的機制 (`creds.refresh(Request())`)。只要您完成上述的 GCP 設定，程式碼就能正常運作並自動展延憑證效期。
