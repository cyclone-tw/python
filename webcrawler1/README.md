# AI Pulse Monitor

AI 新聞自動化抓取系統，從多個 AI 新聞源自動收集文章並轉換為結構化 Markdown。

## 功能特色

- **多源抓取**：支援 TLDR AI、The Decoder、Hugging Face Blog
- **智能清理**：自動移除廣告、導航、頭像等雜訊
- **結構化輸出**：每篇文章包含 YAML Frontmatter（標題、來源、URL、日期）
- **異步架構**：基於 asyncio + aiosqlite 的高效設計
- **摘要預留**：預留 LLM API 接口（建議使用 Gemini 2.0 Flash 免費額度）

## 專案結構

```
webcrawler1/
├── pyproject.toml              # 專案配置與依賴
├── README.md
├── CHANGELOG.md                # 開發記錄（人類與 AI 可讀）
├── run.command                 # macOS 一鍵執行腳本
├── data/
│   ├── articles.db             # SQLite 資料庫
│   └── articles/               # Markdown 文章存放
│       ├── tldr_ai/
│       ├── the_decoder/
│       └── huggingface_blog/
└── ai_pulse_monitor/
    ├── __init__.py
    ├── main.py                 # CLI 主控中心
    ├── database.py             # 資料管理層
    ├── summarizer.py           # 摘要端口預留
    ├── utils.py                # 工具函式（Markdown 清理）
    └── scrapers/
        ├── __init__.py
        ├── tldr_ai.py          # TLDR AI 爬蟲
        ├── the_decoder.py      # The Decoder 爬蟲
        └── huggingface_blog.py # HF Blog 爬蟲 (RSS)
```

## 快速開始

```bash
# 1. 安裝依賴
uv sync

# 2. 安裝瀏覽器
uv run playwright install chromium

# 3. 抓取文章
uv run python -m ai_pulse_monitor.main --sync

# 4. 查看狀態
uv run python -m ai_pulse_monitor.main --status
```

### 一鍵執行（macOS）

在 Finder 中雙擊 `run.command` 即可自動抓取文章，無需開啟終端機。

## CLI 指令

| 指令 | 說明 |
|------|------|
| `--sync` | 抓取並同步最新文章 |
| `--status` | 顯示資料庫統計 |
| `--summarize` | 處理待摘要文章（預留端口） |

## 輸出格式

每篇文章儲存為 Markdown，開頭包含 YAML Frontmatter：

```markdown
---
title: 文章標題
source: the_decoder
url: https://the-decoder.com/...
date: 2026-01-14
---

# 文章正文...
```

## 資料庫結構

**articles 表**

| 欄位 | 類型 | 說明 |
|------|------|------|
| url | TEXT (PK) | 文章原始 URL |
| title | TEXT | 文章標題 |
| source | TEXT | 來源 (tldr_ai / the_decoder / huggingface_blog) |
| content_path | TEXT | 本地 Markdown 檔案路徑 |
| is_summarized | INTEGER | 是否已摘要 (0/1) |
| created_at | TEXT | 抓取時間 |

## 技術棧

| 元件 | 用途 |
|------|------|
| uv | 套件管理 |
| Crawl4AI 0.7.x | 網頁爬蟲框架 |
| Playwright | 瀏覽器自動化 |
| aiosqlite | 異步 SQLite |
| feedparser | RSS 解析 |

## 費用說明

- **爬蟲**：完全免費（無 API 呼叫）
- **摘要**（未來）：建議使用 Gemini 2.0 Flash（免費 1,500 次/天）

## License

MIT
