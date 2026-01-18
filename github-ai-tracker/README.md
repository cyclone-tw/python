# GitHub AI Tracker

自動追蹤 AI 開發工具、Vibe Coding、NotebookLM 生態系相關的熱門 GitHub 專案，並將結果同步到 Notion 資料庫。

## 功能特色

- **7 大生態系追蹤**：Vibe Coding IDE、Antigravity、AI Coding Agents、NotebookLM、AI Infrastructure、PDF Tools、繁體中文專案
- **智慧排序**：每個生態系取 Fork 數前 50 名
- **自動分類**：根據 Topics 自動標記工具分類（Cursor、Claude、Ollama 等）
- **Upsert 同步**：新專案新增、舊專案更新、無變化跳過
- **星星成長追蹤**：記錄 Previous Stars 可計算成長率
- **定時執行**：透過 GitHub Actions 每週自動執行

## 追蹤範圍

| 生態系 | 說明 | 範例專案 |
|--------|------|----------|
| Vibe Coding IDE | AI 優先的程式碼編輯器 | Cursor, Windsurf |
| Antigravity | Google Antigravity 相關 | antigravity-manager |
| AI Coding Agents | AI 編程助手 | Cline, Aider, Claude Code |
| NotebookLM | Google NotebookLM 生態系 | open-notebooklm, pdf-to-pptx |
| AI Infrastructure | AI 基礎設施 | Ollama, vLLM, LangChain, MCP |
| PDF Tools | PDF 處理工具 | PDF-Extract-Kit, MinerU |
| 繁體中文專案 | README 含繁體中文的 AI 專案 | 台灣開發者專案 |

## 安裝

### 前置需求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 套件管理工具

### 步驟

```bash
# 1. Clone 專案
git clone https://github.com/cyclone-tw/python.git
cd python/github-ai-tracker

# 2. 安裝依賴
uv sync

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env 填入你的 API keys
```

## 設定

### 環境變數

| 變數名稱 | 說明 | 必要 |
|----------|------|------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | 是 |
| `NOTION_TOKEN` | Notion Integration Token（`ntn_` 或 `secret_` 開頭）| 是 |
| `NOTION_DATABASE_ID` | Notion 資料庫 ID（32 字元）| 是 |
| `LOG_LEVEL` | 日誌等級 (DEBUG/INFO/WARNING/ERROR) | 否 |
| `MAX_REPOS_PER_ECOSYSTEM` | 每個生態系最多抓取數量（預設 50）| 否 |

### 取得 API Keys

#### GitHub Token

1. 前往 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 點擊 "Generate new token (classic)"
3. 勾選 `public_repo` 權限
4. 產生並複製 Token（`ghp_` 開頭）

#### Notion Integration

1. 前往 [Notion Integrations](https://www.notion.so/my-integrations)
2. 點擊 "New integration"
3. 設定名稱，選擇 Workspace
4. 複製 Internal Integration Token（`ntn_` 或 `secret_` 開頭）
5. **重要**：在 Notion Database 頁面，點擊 `...` > `連結` > 加入你的 Integration

#### Notion Database ID

從 Database URL 取得：
```
https://www.notion.so/workspace/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=...
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                這 32 個字元就是 Database ID
```

### Notion Database 欄位

建立 Notion Database 時，請設定以下欄位：

| 欄位名稱 | 類型 | 說明 |
|----------|------|------|
| Name | Title | 專案名稱（預設）|
| Full Name | Text | owner/repo |
| Description | Text | 專案描述 |
| Stars | Number | 星星數 |
| Previous Stars | Number | 上次爬取的星星數 |
| Forks | Number | Fork 數 |
| Open Issues | Number | Open Issues 數 |
| Language | Select | 程式語言 |
| Ecosystem | Select | 生態系分類 |
| Tool Category | Multi-select | 工具細分類 |
| Topics | Multi-select | GitHub Topics |
| GitHub URL | URL | GitHub 連結 |
| Homepage | URL | 專案官網 |
| License | Select | 授權類型 |
| Created At | Date | 專案建立日期 |
| Updated At | Date | 專案更新日期 |
| Fetched At | Date | 爬取日期 |

## 使用方式

### 本地執行

```bash
uv run python -m src.main
```

### GitHub Actions 定時執行

1. 在 GitHub Repository 設定 Secrets：
   - `GH_API_TOKEN`: GitHub Token（注意：不是 `GITHUB_TOKEN`，這是保留字）
   - `NOTION_TOKEN`: Notion Token
   - `NOTION_DATABASE_ID`: Notion Database ID

2. 啟用 GitHub Actions，工作流程會每週一台北時間早上 6 點自動執行

3. 也可以手動觸發：Actions > GitHub AI Tracker > Run workflow

## 專案結構

```
github-ai-tracker/
├── pyproject.toml          # 專案設定
├── .env.example            # 環境變數範例
├── .gitignore
├── README.md
├── SPEC.md                 # 完整規格書
├── src/
│   ├── __init__.py
│   ├── main.py             # 主程式入口
│   ├── config.py           # 設定管理（Topics、分類對照）
│   ├── clients/
│   │   ├── github_client.py    # GitHub API（httpx + async）
│   │   └── notion_sync.py      # Notion API（httpx 直接呼叫）
│   ├── models/
│   │   └── repository.py       # Pydantic 資料模型
│   └── utils/
│       └── logger.py           # Loguru 日誌
├── tests/
│   ├── test_config.py
│   └── test_models.py
└── .github/
    └── workflows/
        └── github-ai-tracker.yml
```

## 執行結果範例

```
==================== vibe_coding_ide ====================
[vibe_coding_ide] Searching topic: cursor
[vibe_coding_ide] Searching topic: cursor-ai
[vibe_coding_ide] Top 50 repositories by forks
...
==================== chinese_traditional ====================
[chinese_traditional] Searching: 繁體中文 + llm
[chinese_traditional] Found 50 Traditional Chinese projects

Total unique repositories: 326
Phase 2: Syncing to Notion database...
[1/326] CREATED: jwasham/coding-interview-university (forks: 335905)
[2/326] CREATED: public-apis/public-apis (forks: 391473)
...
Sync completed! Created: 326, Updated: 0, Skipped: 0
```

## 技術細節

### 為什麼不用 notion-client SDK？

`notion-client 2.7.0` 版本有 bug，`databases.query()` 方法不存在。本專案改用 `httpx` 直接呼叫 Notion REST API。

### Rate Limiting

- **GitHub Search API**: 每分鐘 30 次，程式內建 2 秒間隔
- **Notion API**: 每秒約 3 次，程式內建 0.35 秒間隔

## License

MIT
