# 📝 開發日誌 (Development Log)

## 版本紀錄

### v1.0.1 - 2024-12-30

#### 🔧 啟動腳本改進

**新增：**
- ✅ macOS: 新增 `啟動工作區管理器.command` 雙擊即可執行
- ✅ Windows: `start.bat` 加入詳細錯誤訊息，不再閃退

**修復：**
- macOS 雙擊 `.sh` 會開啟文字編輯器的問題
- Windows `.bat` 執行失敗時會閃退的問題

---

### v1.0.0 - 2024-12-30

#### 🎉 初始版本發布

**功能實現：**
- ✅ Material Design 深色主題 UI
- ✅ 動態工作區卡片生成
- ✅ 一鍵啟動資料夾、檔案、網址
- ✅ 新增/編輯/刪除工作區
- ✅ JSON 設定檔持久化
- ✅ 可滾動的編輯對話框
- ✅ macOS/Windows/Linux 跨平台支援

**技術選型：**
- UI 框架：CustomTkinter 5.2.2
- 配色：Material Design 2 規範
- 資料格式：JSON
- 路徑處理：pathlib

**已知限制：**
- 需要手動安裝 Python 和 Tkinter
- 暫無拖放功能新增路徑
- 暫無工作區圖示自訂

---

## 開發筆記

### 2024-12-30

#### 問題：編輯視窗按鈕被裁切
- **原因**：視窗高度 500px 不足以顯示所有元素
- **解決**：
  1. 增加視窗高度至 700px
  2. 將按鈕區固定在底部 (`side="bottom"`)
  3. 中間內容區使用 `CTkScrollableFrame`
  4. 輸入框改用 `CTkTextbox` 支援多行

#### 問題：macOS 缺少 Tkinter 模組
- **錯誤**：`ModuleNotFoundError: No module named '_tkinter'`
- **解決**：`brew install python-tk@3.12`

#### 問題：Python 外部管理環境限制
- **錯誤**：`externally-managed-environment`
- **解決**：使用虛擬環境 `python3 -m venv venv`

---

## 未來規劃

### v1.1.0 (計劃中)
- [ ] 拖放功能新增路徑
- [ ] 工作區圖示/表情符號選擇
- [ ] 匯入/匯出設定檔
- [ ] 搜尋過濾工作區

### v1.2.0 (計劃中)
- [ ] 系統托盤常駐
- [ ] 快捷鍵支援
- [ ] 多語言介面
- [ ] 自動更新檢查
