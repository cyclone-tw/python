# GitHub AI Tracker

自動追蹤 AI 開發工具、Vibe Coding、NotebookLM 生態系相關的熱門 GitHub 專案，並將結果同步到 Notion 資料庫。

## 功能特色

- **多生態系追蹤**：Vibe Coding IDE、AI Coding Agents、NotebookLM、AI Infrastructure、PDF Tools
- **自動分類**：根據 Topics 自動標記工具分類
- **智慧同步**：Upsert 邏輯避免重複，追蹤星星成長趨勢
- **定時執行**：透過 GitHub Actions 每週自動執行

## 追蹤範圍

| 生態系 | 說明 | 範例專案 |
|--------|------|----------|
| Vibe Coding IDE | AI 優先的程式碼編輯器 | Cursor, Windsurf |
| AI Coding Agents | AI 編程助手 | Cline, Aider, Claude Code |
| NotebookLM | Google NotebookLM 生態系 | open-notebooklm, pdf-to-pptx |
| AI Infrastructure | AI 基礎設施 | Ollama, vLLM, LangChain |
| PDF Tools | PDF 處理工具 | PDF-Extract-Kit, MinerU |

## 安裝

### 前置需求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 套件管理工具

### 步驟

1. Clone 專案

```bash
git clone https://github.com/yourusername/github-ai-tracker.git
cd github-ai-tracker
```

2. 安裝依賴

```bash
uv sync
```

3. 設定環境變數

```bash
cp .env.example .env
# 編輯 .env 填入你的 API keys
```

## 設定

### 環境變數

| 變數名稱 | 說明 | 必要 |
|----------|------|------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | 是 |
| `NOTION_TOKEN` | Notion Integration Token | 是 |
| `NOTION_DATABASE_ID` | Notion 資料庫 ID | 是 |
| `LOG_LEVEL` | 日誌等級 (DEBUG/INFO/WARNING/ERROR) | 否 |
| `MAX_REPOS_PER_TOPIC` | 每個 topic 最多抓取數量 | 否 |

### 取得 API Keys

#### GitHub Token

1. 前往 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 點擊 "Generate new token (classic)"
3. 勾選 `public_repo` 權限
4. 產生並複製 Token

#### Notion Integration

1. 前往 [Notion Integrations](https://www.notion.so/my-integrations)
2. 點擊 "New integration"
3. 設定名稱，選擇 Workspace
4. 複製 Internal Integration Token
5. 在 Notion 資料庫頁面，點擊 "..." > "Add connections" > 選擇你的 Integration

### Notion 資料庫欄位

建立 Notion Database 時，請設定以下欄位：

| 欄位名稱 | 類型 | 說明 |
|----------|------|------|
| Name | Title | 專案名稱 |
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
   - `GH_API_TOKEN`: GitHub Token
   - `NOTION_TOKEN`: Notion Token
   - `NOTION_DATABASE_ID`: Notion Database ID

2. 啟用 GitHub Actions，工作流程會每週一自動執行

3. 也可以手動觸發：Actions > GitHub AI Tracker > Run workflow

## 專案結構

```
github-ai-tracker/
├── pyproject.toml          # 專案設定
├── .env.example            # 環境變數範例
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py             # 主程式入口
│   ├── config.py           # 設定管理
│   ├── clients/
│   │   ├── github_client.py    # GitHub API
│   │   └── notion_client.py    # Notion API
│   ├── models/
│   │   └── repository.py       # 資料模型
│   └── utils/
│       └── logger.py           # 日誌工具
├── tests/
└── .github/
    └── workflows/
        └── crawler.yml     # GitHub Actions
```

## 執行結果範例

```
2025-01-17 10:00:00 | INFO | Starting GitHub AI Tracker...
2025-01-17 10:00:01 | INFO | Loaded 6 ecosystems with 35 topics
2025-01-17 10:00:02 | INFO | [vibe_coding_ide] Searching topic: cursor
2025-01-17 10:00:03 | INFO | [vibe_coding_ide] Found 45 repositories
...
2025-01-17 10:02:30 | INFO | Total unique repositories: 312
2025-01-17 10:02:31 | INFO | Phase 2: Syncing to Notion database...
2025-01-17 10:03:45 | INFO | Sync completed! Created: 45, Updated: 267, Skipped: 0
```

## License

MIT
