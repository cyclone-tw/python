# GitHub AI Tracker 開發日誌

**專案名稱**：GitHub AI Tracker
**開發日期**：2025-01-18
**開發者**：Cyclone + Claude Opus 4.5
**用途**：線上課程作業 - 網路爬蟲專案

---

## 專案概述

建立一個自動化工具，透過 GitHub API 爬取 AI 開發工具相關的熱門開源專案，並同步到 Notion 資料庫。

---

## 開發時間軸

### Phase 1: 專案初始化

**完成項目：**
- 建立 `pyproject.toml`（使用 uv 管理套件）
- 建立目錄結構（src/clients, src/models, src/utils）
- 設定 `.gitignore`、`.env.example`

**遇到的問題：**
- `uv sync` 失敗，錯誤：`Unable to determine which files to ship inside the wheel`
- **原因**：`pyproject.toml` 缺少 `[tool.hatch.build.targets.wheel]` 設定
- **解法**：加入 `packages = ["src"]`

---

### Phase 2: 核心功能開發

**完成項目：**
- `src/config.py`：Topics 設定、工具分類對照表
- `src/models/repository.py`：Pydantic 資料模型
- `src/clients/github_client.py`：GitHub API 客戶端（async + httpx）
- `src/clients/notion_client.py`：Notion API 客戶端
- `src/main.py`：主程式入口
- `src/utils/logger.py`：Loguru 日誌設定

---

### Phase 3: GitHub Actions 設定

**遇到的問題 #1：Workflow 沒出現**
- **現象**：在 GitHub Actions 頁面看不到 workflow
- **原因**：workflow 檔案放在 `github-ai-tracker/.github/workflows/`，但 GitHub 只讀取 repo 根目錄的 `.github/workflows/`
- **解法**：將 workflow 移到 `/python/.github/workflows/github-ai-tracker.yml`，並設定 `working-directory: github-ai-tracker`

---

### Phase 4: Notion 同步問題（重點！）

#### 問題 #2：`'DatabasesEndpoint' object has no attribute 'query'`

**現象**：
```
Failed to sync to Notion: 'DatabasesEndpoint' object has no attribute 'query'
```

**排查過程**：
1. 最初以為是檔案命名衝突（`notion_client.py` vs `notion-client` 套件）
2. 將檔案改名為 `notion_sync.py` → 問題依舊
3. 改用 `import notion_client` 而非 `from notion_client import Client` → 問題依舊
4. 檢查 `notion-client 2.7.0` 原始碼，發現 **`databases.query()` 方法真的不存在！**

**根本原因**：
`notion-client 2.7.0` 版本的 `DatabasesEndpoint` class 只有 `create`, `retrieve`, `update` 方法，沒有 `query`。這是 SDK 的 bug 或 breaking change。

**解法**：
放棄使用 SDK，改用 `httpx` 直接呼叫 Notion REST API：
```python
def _request(self, method: str, endpoint: str, json: dict | None = None) -> dict:
    url = f"https://api.notion.com/v1/{endpoint}"
    with httpx.Client(timeout=30) as client:
        response = client.request(method, url, headers=self.headers, json=json)
        response.raise_for_status()
        return response.json()
```

---

#### 問題 #3：`Invalid request URL`

**現象**：
```
Failed to sync to Notion: Invalid request URL.
```

**排查過程**：
1. 檢查 Integration 是否連結到 Database → ✅ 已連結
2. 檢查 Secret 名稱是否正確 → ✅ 名稱正確
3. 懷疑 Secret 值有問題

**根本原因**：
`NOTION_DATABASE_ID` 的值可能有問題（多餘空格、格式錯誤）

**解法**：
重新設定 GitHub Secret，確保：
- Database ID 是 32 字元
- 前後沒有空格
- 沒有連字號

---

#### 問題 #4：Notion Token 格式混淆

**現象**：
使用者不確定 Notion Token 從哪裡取得，以及正確格式

**釐清**：
- **舊版格式**：`secret_xxxxxxxx`
- **新版格式**：`ntn_xxxxxxxx`
- **兩種都可以用！**
- **取得位置**：https://www.notion.so/my-integrations → 選擇 Integration → 「內部整合密鑰」

---

#### 問題 #5：Notion Database 欄位未建立

**現象**：
使用者以為程式會自動建立 Notion Database 欄位

**釐清**：
- Notion API **不會** 自動建立欄位
- 必須**手動**在 Notion Database 建立所有需要的欄位
- 欄位名稱必須**完全一致**（包括大小寫）

---

### Phase 5: 功能優化

**使用者需求變更**：
1. 原本每個 topic 抓 50 個，總共 1261 筆太多
2. 改為每個**生態系**取 Fork 數前 50 名
3. 新增「繁體中文專案」類別（搜尋 README 含繁中的 AI 專案）
4. Notion 同步加入速率限制（避免被封鎖）

**修改項目**：
- `MAX_REPOS_PER_TOPIC` → `MAX_REPOS_PER_ECOSYSTEM`
- 排序方式從 Stars 改為 Forks
- 新增 `search_chinese_projects()` 方法
- 新增 `NOTION_RATE_LIMIT_DELAY = 0.35` 秒

---

## 技術決策記錄

### 決策 1：為什麼用 httpx 而不是 requests？
- 支援 async（GitHub 爬蟲用 async）
- 同時支援 sync（Notion 同步用 sync）
- 是 notion-client SDK 的底層依賴，不用額外安裝

### 決策 2：為什麼放棄 notion-client SDK？
- SDK 2.7.0 版本有 bug
- 直接用 httpx 呼叫 REST API 更可控
- 方便 debug

### 決策 3：為什麼用 Fork 數排序而不是 Stars？
- 使用者需求
- Fork 數代表「實際被使用」的程度
- Stars 可能被灌水

### 決策 4：為什麼每個生態系限制 50 個？
- 減少 Notion API 呼叫次數
- 避免被 rate limit
- 資料量更精簡，方便瀏覽

---

## GitHub Secrets 設定注意事項

| Secret 名稱 | 格式 | 常見錯誤 |
|-------------|------|----------|
| `GH_API_TOKEN` | `ghp_xxx...` | 不能用 `GITHUB_TOKEN`（保留字）|
| `NOTION_TOKEN` | `ntn_xxx...` 或 `secret_xxx...` | 前後有空格 |
| `NOTION_DATABASE_ID` | 32 字元 | 包含連字號、貼錯 URL 片段 |

---

## Notion 設定注意事項

1. **必須建立 Integration**
   - https://www.notion.so/my-integrations

2. **必須連結 Integration 到 Database**
   - Database 頁面 → `...` → `連結` → 加入 Integration

3. **必須手動建立欄位**
   - Name, Full Name, Stars, Forks, Ecosystem, GitHub URL, Fetched At...

4. **欄位名稱區分大小寫**
   - `Stars` ✅
   - `stars` ❌

---

## 未來改進方向

- [ ] 錯誤時發送通知（Discord/Slack）
- [ ] 每週趨勢報告
- [ ] Web Dashboard 視覺化
- [ ] 支援更多篩選條件

---

## Commit 歷史

| Commit | 說明 |
|--------|------|
| `81df44f` | 初始版本 |
| `b137c51` | 修正 workflow 位置 |
| `ed159b7` | 修正 notion_client 命名衝突 |
| `9ec351a` | 優化爬蟲邏輯 + 新增繁體中文類別 |
| `2124cc7` | 嘗試修正 databases.query bug |
| `d467ba0` | 改用 httpx 直接呼叫 Notion API |

---

## 給未來自己的提醒

1. **Notion SDK 不可靠**：直接用 REST API 比較穩
2. **GitHub Actions workflow 位置**：必須在 repo 根目錄的 `.github/workflows/`
3. **Secret 值要小心空格**：複製貼上時容易多空格
4. **Notion Database 欄位要先建**：API 不會自動建立
5. **Integration 要連結到 Database**：建立 Integration 不夠，還要加到 Database 的連結

---

*此文件由 Claude Opus 4.5 協助撰寫，記錄與 Cyclone 的協作開發過程。*
