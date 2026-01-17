# GitHub AI/Vibe Coding 趨勢追蹤器

## 專案規格說明書 (Project Specification)

**版本**: 1.0  
**日期**: 2025-01-17  
**作者**: [你的名字]  
**用途**: 線上課程作業 - 網路爬蟲專案

---

## 1. 專案概述

### 1.1 專案目標
建立一個自動化工具，透過 GitHub API 爬取 AI 開發工具、Vibe Coding、NotebookLM 生態系相關的熱門開源專案資料，並將結果同步到 Notion 資料庫，方便追蹤產業趨勢。

### 1.2 解決的問題
- 手動追蹤 GitHub 熱門 AI 專案耗時費力
- 難以系統性比較不同工具的熱門程度
- 缺乏集中化的資料管理與視覺化
- AI 工具生態系變化快速，需要即時追蹤

### 1.3 目標用戶
- 對 AI 開發工具有興趣的開發者
- 想了解 Vibe Coding 生態系的學習者
- 需要追蹤技術趨勢的技術決策者
- NotebookLM 進階用戶與開發者

---

## 2. 追蹤範圍

### 2.1 三大生態系概覽

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI 開發工具生態系追蹤                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🎨 Vibe Coding IDE              🤖 AI Coding Agents            │
│  ├── Cursor                      ├── Claude Code                │
│  ├── Antigravity (Google)        ├── Cline                      │
│  └── Windsurf                    ├── Aider                      │
│                                  └── Continue                   │
│                                                                 │
│  📚 NotebookLM 生態系            🔧 AI 基礎設施                  │
│  ├── PDF 處理工具                ├── Ollama (本地 LLM)          │
│  ├── 圖層分離工具                ├── vllm (推論引擎)            │
│  ├── Podcast 生成                ├── RAGFlow                    │
│  └── 開源替代方案                └── LangChain / LangFlow       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 追蹤的 GitHub Topics

```python
TOPICS = {
    # ===== Vibe Coding IDE =====
    "vibe_coding_ide": [
        "vibe-coding",
        "cursor",
        "cursor-ai",
        "cursor-rules",
        "windsurf",
        "windsurf-ai",
    ],
    
    # ===== Google Antigravity =====
    "antigravity": [
        "antigravity",
        "antigravity-ide",
        "antigravity-ai",
        "gemini-cli",
    ],
    
    # ===== AI Coding Agents =====
    "ai_coding_agents": [
        "ai-agent",
        "coding-assistant",
        "claude-code",
        "cline",
        "aider",
        "continue",
        "copilot",
    ],
    
    # ===== NotebookLM 生態系 ===== ⭐ 重點追蹤
    "notebooklm": [
        "notebooklm",
        "pdf-to-pptx",           # PDF 轉簡報（圖層分離）
        "pdf-text-extraction",   # PDF 文字提取
        "ai-podcast",            # AI Podcast 生成
        "open-notebooklm",       # 開源替代方案
    ],
    
    # ===== AI 基礎設施 =====
    "ai_infrastructure": [
        "llm",
        "ollama",
        "local-llm",
        "rag",
        "ragflow",
        "mcp",                   # Model Context Protocol
        "langchain",
        "langflow",
        "vllm",
    ],
    
    # ===== PDF 處理工具 =====
    "pdf_tools": [
        "pdf-extract",
        "pdf-parser",
        "ocr",
        "document-ai",
        "pdf-to-markdown",
    ],
}
```

### 2.3 重點專案清單

以下是目前已知的重點專案，爬蟲會特別追蹤：

| 分類 | 專案名稱 | 說明 | 預估星星 |
|------|----------|------|----------|
| **Vibe Coding** | cursor | AI-first code editor | 40k+ |
| **Antigravity** | antigravity-manager | 多帳號管理工具 | 500+ |
| **AI Agent** | cline | VS Code AI agent | 39k+ |
| **AI Agent** | aider | Terminal AI pair programmer | 熱門 |
| **NotebookLM** | notebooklm-pdf-to-pptx | PDF 圖層分離轉 PPTX | 114+ |
| **NotebookLM** | open-notebooklm | 開源 NotebookLM 替代 | 熱門 |
| **NotebookLM** | Local-NotebookLM | 本地版 NotebookLM | 熱門 |
| **基礎設施** | ollama | 本地運行 LLM | 150k+ |
| **基礎設施** | vllm | 高效 LLM 推論 | 快速成長 |
| **PDF 工具** | PDF-Extract-Kit | PDF 內容提取工具包 | 熱門 |
| **PDF 工具** | MinerU | PDF 轉 Markdown | 熱門 |

---

## 3. 功能需求

### 3.1 核心功能

| 功能 | 描述 | 優先級 |
|------|------|--------|
| GitHub 資料爬取 | 透過 API 取得指定 Topics 的專案資料 | P0 (必要) |
| 多分類追蹤 | 支援 Vibe Coding / Antigravity / NotebookLM 等分類 | P0 (必要) |
| 資料過濾與整理 | 篩選、排序、格式化爬取的資料 | P0 (必要) |
| Notion 同步 | 將資料寫入 Notion 資料庫 | P0 (必要) |
| 分類標籤 | 自動為專案添加所屬生態系標籤 | P1 (重要) |
| 重複資料處理 | 更新已存在的專案，新增不存在的專案 | P1 (重要) |
| 錯誤處理與日誌 | 記錄執行過程與錯誤訊息 | P1 (重要) |
| 趨勢分析 | 計算星星成長率（選配） | P2 (選配) |
| 定時執行 | 支援排程自動執行（選配） | P2 (選配) |

### 3.2 爬取的資料欄位

| 欄位名稱 | GitHub API 對應 | 資料類型 | 說明 |
|----------|-----------------|----------|------|
| 專案名稱 | `name` | string | Repository 名稱 |
| 完整名稱 | `full_name` | string | owner/repo 格式 |
| 描述 | `description` | string | 專案說明 |
| 星星數 | `stargazers_count` | number | ⭐ 數量 |
| Fork 數 | `forks_count` | number | Fork 數量 |
| 主要語言 | `language` | string | 程式語言 |
| Topics | `topics` | list | 標籤列表 |
| 建立時間 | `created_at` | datetime | 專案建立日期 |
| 更新時間 | `updated_at` | datetime | 最後更新日期 |
| 專案網址 | `html_url` | url | GitHub 連結 |
| 首頁網址 | `homepage` | url | 專案官網（如有）|
| Open Issues | `open_issues_count` | number | 開放的 Issue 數 |
| License | `license.name` | string | 授權類型 |
| **生態系分類** | (自訂) | string | vibe_coding / antigravity / notebooklm / ai_agent / infrastructure |

---

## 4. 技術架構

### 4.1 技術棧

```
Python 3.11+
├── uv (套件管理)
├── httpx (HTTP 請求，支援 async)
├── PyGithub (GitHub API 官方套件，選用)
├── notion-client (Notion API 官方套件)
├── python-dotenv (環境變數管理)
├── pydantic (資料驗證)
└── loguru (日誌記錄)
```

### 4.2 系統架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        主程式 (main.py)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   GitHub    │    │    Data     │    │   Notion    │         │
│  │   Client    │ -> │  Processor  │ -> │   Client    │         │
│  │             │    │             │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                 │                   │                 │
│         v                 v                   v                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ GitHub API  │    │   Models    │    │ Notion API  │         │
│  │  (外部)     │    │  (Pydantic) │    │   (外部)    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                      Topics Config                              │
│   (vibe_coding / antigravity / notebooklm / ai_agent / infra)  │
├─────────────────────────────────────────────────────────────────┤
│                     Config & Logging                            │
│              (.env / config.py / logger)                        │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 專案目錄結構

```
github-ai-tracker/
├── pyproject.toml          # uv 專案設定
├── .env                    # 環境變數（API Keys）
├── .env.example            # 環境變數範例
├── .gitignore              # Git 忽略檔案
├── README.md               # 專案說明
│
├── src/
│   ├── __init__.py
│   ├── main.py             # 主程式入口
│   ├── config.py           # 設定管理（含 Topics 定義）
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── github_client.py    # GitHub API 客戶端
│   │   └── notion_client.py    # Notion API 客戶端
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── repository.py       # 資料模型定義
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # 日誌工具
│
├── tests/                  # 測試檔案
│   ├── __init__.py
│   ├── test_github_client.py
│   └── test_notion_client.py
│
└── data/                   # 本地資料暫存（選配）
    └── .gitkeep
```

---

## 5. API 規格

### 5.1 GitHub API

**Base URL**: `https://api.github.com`

**認證方式**: Personal Access Token (PAT)
```
Headers: {
    "Authorization": "Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}
```

**主要 Endpoints**:

| 用途 | Method | Endpoint | 說明 |
|------|--------|----------|------|
| 搜尋專案 | GET | `/search/repositories` | 依條件搜尋 repos |
| Topic 專案 | GET | `/search/repositories?q=topic:{topic}` | 依 Topic 搜尋 |
| 專案詳情 | GET | `/repos/{owner}/{repo}` | 取得單一專案資訊 |

**Rate Limit**:
- 未認證: 60 requests/hour
- 已認證: 5,000 requests/hour
- Search API: 30 requests/minute (已認證)

**搜尋範例**:
```python
# 搜尋 notebooklm topic，依星星數排序，取前 100 個
GET /search/repositories?q=topic:notebooklm&sort=stars&order=desc&per_page=100

# 搜尋多個關鍵字
GET /search/repositories?q=notebooklm+pdf+pptx&sort=stars&order=desc&per_page=50
```

### 5.2 Notion API

**Base URL**: `https://api.notion.com/v1`

**認證方式**: Integration Token
```
Headers: {
    "Authorization": "Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
```

**主要 Endpoints**:

| 用途 | Method | Endpoint | 說明 |
|------|--------|----------|------|
| 查詢資料庫 | POST | `/databases/{database_id}/query` | 查詢現有資料 |
| 新增頁面 | POST | `/pages` | 新增一筆資料 |
| 更新頁面 | PATCH | `/pages/{page_id}` | 更新現有資料 |

---

## 6. 資料模型

### 6.1 Repository Model (Pydantic)

```python
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, Literal

# 生態系分類類型
EcosystemType = Literal[
    "vibe_coding_ide",
    "antigravity", 
    "ai_coding_agents",
    "notebooklm",
    "ai_infrastructure",
    "pdf_tools"
]

class Repository(BaseModel):
    """GitHub Repository 資料模型"""
    
    # 基本資訊
    name: str                           # 專案名稱
    full_name: str                      # owner/repo
    description: Optional[str] = None   # 專案描述
    html_url: HttpUrl                   # GitHub 網址
    homepage: Optional[HttpUrl] = None  # 專案官網
    
    # 數據指標
    stargazers_count: int               # 星星數
    forks_count: int                    # Fork 數
    open_issues_count: int              # Open Issues
    
    # 分類資訊
    language: Optional[str] = None      # 主要語言
    topics: list[str] = []              # Topics 標籤
    license_name: Optional[str] = None  # 授權類型
    
    # 時間資訊
    created_at: datetime                # 建立時間
    updated_at: datetime                # 更新時間
    
    # 自訂欄位
    ecosystem: EcosystemType            # 生態系分類
    matched_topic: str                  # 匹配的 Topic
    fetched_at: datetime                # 爬取時間
```

### 6.2 Notion Database Schema

| 欄位名稱 | Notion 類型 | 對應欄位 | 說明 |
|----------|-------------|----------|------|
| Name | Title | `name` | 專案名稱 |
| Full Name | Rich Text | `full_name` | owner/repo |
| Description | Rich Text | `description` | 專案描述 |
| Stars ⭐ | Number | `stargazers_count` | 當前星星數 |
| **Previous Stars** | Number | `previous_stars` | 上次爬取的星星數 |
| **Stars Growth** | Formula | (自動計算) | 星星成長數 |
| **Growth Rate %** | Formula | (自動計算) | 成長百分比 |
| Forks | Number | `forks_count` | Fork 數 |
| Language | Select | `language` | 程式語言 |
| **Ecosystem** | Select | `ecosystem` | 生態系大分類 |
| **Tool Category** | Multi-select | `tool_categories` | 工具細分類（可多選）⭐ |
| Topics | Multi-select | `topics` | GitHub Topics |
| GitHub URL | URL | `html_url` | 專案連結 |
| Homepage | URL | `homepage` | 官網連結 |
| License | Select | `license_name` | 授權類型 |
| Created At | Date | `created_at` | 建立日期 |
| Updated At | Date | `updated_at` | 更新日期 |
| Fetched At | Date | `fetched_at` | 本次爬取日期 |
| **Last Fetched** | Date | `last_fetched` | 上次爬取日期 |

---

### 6.3 分類系統設計 ⭐ 新增

#### 6.3.1 Ecosystem（生態系大分類）- Select 單選

| 選項 | 顏色 | 說明 |
|------|------|------|
| 🎨 Vibe Coding IDE | Purple | AI IDE 工具 |
| 🤖 AI Coding Agents | Green | AI 編程代理 |
| 📚 NotebookLM | Orange | NotebookLM 相關 |
| 🔧 AI Infrastructure | Gray | AI 基礎設施 |
| 📄 PDF Tools | Yellow | PDF 處理工具 |

#### 6.3.2 Tool Category（工具細分類）- Multi-select 多選

專案可能同時屬於多個工具分類，例如一個專案可能同時與 Claude 和 MCP 相關。

| 分類 | 顏色建議 | 相關 Topics |
|------|----------|-------------|
| **Cursor** | Purple | cursor, cursor-ai, cursor-rules |
| **Antigravity** | Blue | antigravity, antigravity-ide, antigravity-ai |
| **Windsurf** | Cyan | windsurf, windsurf-ai |
| **Claude** | Orange | claude-code, claude, anthropic |
| **Cline** | Green | cline |
| **Aider** | Lime | aider |
| **Copilot** | Gray | copilot, github-copilot |
| **NotebookLM** | Red | notebooklm, open-notebooklm |
| **Ollama** | Brown | ollama, local-llm |
| **RAG** | Pink | rag, ragflow, langchain |
| **MCP** | Teal | mcp, model-context-protocol |
| **PDF** | Yellow | pdf-extract, pdf-parser, ocr |
| **Podcast** | Indigo | ai-podcast, tts |
| **vLLM** | Dark Gray | vllm |
| **LangChain** | Light Blue | langchain, langflow |

---

### 6.4 星星成長追蹤 ⭐ 新增

#### 6.4.1 欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| Stars ⭐ | Number | 當前星星數 |
| Previous Stars | Number | 上次爬取時的星星數 |
| Stars Growth | Formula | 星星成長數 = Stars - Previous Stars |
| Growth Rate % | Formula | 成長百分比 |
| Last Fetched | Date | 上次爬取的時間 |

#### 6.4.2 Notion Formula 設定

**Stars Growth（星星成長數）**:
```
prop("Stars") - prop("Previous Stars")
```

**Growth Rate %（成長百分比）**:
```
if(
  prop("Previous Stars") > 0,
  round((prop("Stars") - prop("Previous Stars")) / prop("Previous Stars") * 100 * 10) / 10,
  0
)
```

#### 6.4.3 預期輸出範例

| Name | Stars ⭐ | Previous | Growth | Rate % | Tool Category |
|------|---------|----------|--------|--------|---------------|
| ollama | 150,000 | 148,000 | +2,000 | +1.4% | Ollama |
| cline | 39,000 | 38,500 | +500 | +1.3% | Cline, Claude |
| cursor-rules | 5,200 | 4,800 | +400 | +8.3% | Cursor |
| notebooklm-pdf-to-pptx | 120 | 114 | +6 | +5.3% | NotebookLM, PDF |
| antigravity-manager | 550 | 521 | +29 | +5.6% | Antigravity |

---

### 6.5 自動分類邏輯

根據專案的 Topics 自動判斷 Tool Category：

```python
# 工具分類對照表
TOOL_CATEGORY_MAPPING = {
    # Cursor 相關
    "cursor": "Cursor",
    "cursor-ai": "Cursor",
    "cursor-rules": "Cursor",
    
    # Antigravity 相關
    "antigravity": "Antigravity",
    "antigravity-ide": "Antigravity",
    "antigravity-ai": "Antigravity",
    "gemini-cli": "Antigravity",
    
    # Windsurf 相關
    "windsurf": "Windsurf",
    "windsurf-ai": "Windsurf",
    
    # Claude 相關
    "claude-code": "Claude",
    "claude": "Claude",
    "anthropic": "Claude",
    
    # 其他 AI Agents
    "cline": "Cline",
    "aider": "Aider",
    "copilot": "Copilot",
    "github-copilot": "Copilot",
    
    # NotebookLM 相關
    "notebooklm": "NotebookLM",
    "open-notebooklm": "NotebookLM",
    "ai-podcast": "Podcast",
    
    # AI 基礎設施
    "ollama": "Ollama",
    "local-llm": "Ollama",
    "vllm": "vLLM",
    "rag": "RAG",
    "ragflow": "RAG",
    "langchain": "LangChain",
    "langflow": "LangChain",
    "mcp": "MCP",
    "model-context-protocol": "MCP",
    
    # PDF 工具
    "pdf-extract": "PDF",
    "pdf-parser": "PDF",
    "pdf-to-pptx": "PDF",
    "pdf-text-extraction": "PDF",
    "ocr": "PDF",
    "document-ai": "PDF",
}

def get_tool_categories(topics: list[str]) -> list[str]:
    """根據 Topics 自動判斷工具分類（可能返回多個）"""
    categories = set()
    
    for topic in topics:
        topic_lower = topic.lower()
        if topic_lower in TOOL_CATEGORY_MAPPING:
            categories.add(TOOL_CATEGORY_MAPPING[topic_lower])
    
    return list(categories)


# 使用範例
repo_topics = ["cursor-ai", "mcp", "vibe-coding"]
categories = get_tool_categories(repo_topics)
# 結果: ["Cursor", "MCP"]

repo_topics = ["notebooklm", "pdf-to-pptx"]
categories = get_tool_categories(repo_topics)
# 結果: ["NotebookLM", "PDF"]
```

---

## 7. 執行流程

### 7.1 主要流程

```
開始
  │
  ▼
載入設定 (.env + Topics Config)
  │
  ▼
初始化 GitHub Client
  │
  ▼
┌─────────────────────────────────────────┐
│  For each ecosystem (6 個生態系):        │
│    For each topic in ecosystem:         │
│      1. 搜尋 GitHub repos               │
│      2. 解析回應資料                     │
│      3. 標記 ecosystem 分類              │
│      4. 轉換成 Repository Model         │
│      5. 加入結果列表                     │
│      6. 處理 Rate Limit (如需要)        │
└─────────────────────────────────────────┘
  │
  ▼
資料去重（同一 repo 可能匹配多個 topic）
  │
  ▼
依星星數排序
  │
  ▼
初始化 Notion Client
  │
  ▼
查詢 Notion 現有資料
  │
  ▼
┌─────────────────────────────────────────┐
│  For each repository:                   │
│    If exists in Notion (by full_name):  │
│      -> 更新資料（星星數、更新時間等）    │
│    Else:                                │
│      -> 新增資料                        │
└─────────────────────────────────────────┘
  │
  ▼
輸出執行摘要
  │
  ▼
結束
```

### 7.2 重複資料處理機制（Upsert 邏輯）⭐ 重要

為了避免重複寫入，系統採用 **Upsert（Update or Insert）** 策略：

#### 7.2.1 唯一識別碼
使用 `full_name`（格式：`owner/repo`）作為專案的唯一識別碼，例如：
- `ollama/ollama`
- `anthropics/claude-code`

#### 7.2.2 處理流程

```
┌─────────────────────────────────────────────────────────────┐
│                    Upsert 處理流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 爬取 GitHub 資料                                        │
│     └── 取得 repos 列表（含 full_name, updated_at 等）       │
│                                                             │
│  2. 查詢 Notion 現有資料                                     │
│     └── 建立 {full_name: page_id} 的對照表                  │
│                                                             │
│  3. 逐一處理每個 repo:                                       │
│     │                                                       │
│     ├── full_name 存在於 Notion？                           │
│     │   │                                                   │
│     │   ├── YES → 比較 updated_at                          │
│     │   │   │                                               │
│     │   │   ├── GitHub 較新 → UPDATE 該頁面                 │
│     │   │   │                                               │
│     │   │   └── 相同或較舊 → SKIP（不處理）                  │
│     │   │                                                   │
│     │   └── NO → INSERT 新頁面                              │
│     │                                                       │
│  4. 輸出統計：Created / Updated / Skipped                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 7.2.3 判斷更新的條件

| 情況 | GitHub `updated_at` | Notion `Updated At` | 動作 |
|------|---------------------|---------------------|------|
| 專案有更新 | 2025-01-17 | 2025-01-10 | ✅ UPDATE |
| 專案無變化 | 2025-01-10 | 2025-01-10 | ⏭️ SKIP |
| 新專案 | 任意 | (不存在) | ➕ INSERT |

#### 7.2.4 程式碼範例

```python
from datetime import datetime
from notion_client import Client

class NotionSync:
    def __init__(self, token: str, database_id: str):
        self.client = Client(auth=token)
        self.database_id = database_id
        self.existing_pages = {}  # {full_name: {page_id, updated_at}}
    
    def load_existing_pages(self):
        """載入 Notion 資料庫中現有的所有專案"""
        results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            response = self.client.databases.query(
                database_id=self.database_id,
                start_cursor=start_cursor
            )
            results.extend(response["results"])
            has_more = response["has_more"]
            start_cursor = response.get("next_cursor")
        
        # 建立對照表
        for page in results:
            props = page["properties"]
            full_name = props["Full Name"]["rich_text"][0]["plain_text"]
            updated_at = props["Updated At"]["date"]["start"]
            
            self.existing_pages[full_name] = {
                "page_id": page["id"],
                "updated_at": datetime.fromisoformat(updated_at)
            }
        
        print(f"Loaded {len(self.existing_pages)} existing pages from Notion")
    
    def upsert_repository(self, repo: Repository) -> str:
        """
        Upsert 單一專案到 Notion
        
        Returns:
            "created" | "updated" | "skipped"
        """
        full_name = repo.full_name
        
        if full_name in self.existing_pages:
            existing = self.existing_pages[full_name]
            
            # 比較更新時間
            if repo.updated_at > existing["updated_at"]:
                # GitHub 資料較新，執行更新
                self._update_page(existing["page_id"], repo)
                return "updated"
            else:
                # 資料沒有變化，跳過
                return "skipped"
        else:
            # 新專案，執行新增
            self._create_page(repo)
            return "created"
    
    def _create_page(self, repo: Repository):
        """新增頁面到 Notion"""
        self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=self._build_properties(repo)
        )
    
    def _update_page(self, page_id: str, repo: Repository):
        """更新現有頁面"""
        self.client.pages.update(
            page_id=page_id,
            properties=self._build_properties(repo)
        )
    
    def _build_properties(self, repo: Repository) -> dict:
        """建構 Notion 頁面屬性"""
        return {
            "Name": {"title": [{"text": {"content": repo.name}}]},
            "Full Name": {"rich_text": [{"text": {"content": repo.full_name}}]},
            "Description": {"rich_text": [{"text": {"content": repo.description or ""}}]},
            "Stars": {"number": repo.stargazers_count},
            "Forks": {"number": repo.forks_count},
            "Language": {"select": {"name": repo.language} if repo.language else None},
            "Ecosystem": {"select": {"name": repo.ecosystem}},
            "GitHub URL": {"url": str(repo.html_url)},
            "Updated At": {"date": {"start": repo.updated_at.isoformat()}},
            "Fetched At": {"date": {"start": repo.fetched_at.isoformat()}},
        }


# 使用範例
def sync_to_notion(repos: list[Repository]):
    notion = NotionSync(
        token=os.getenv("NOTION_TOKEN"),
        database_id=os.getenv("NOTION_DATABASE_ID")
    )
    
    # Step 1: 載入現有資料
    notion.load_existing_pages()
    
    # Step 2: Upsert 每個專案
    stats = {"created": 0, "updated": 0, "skipped": 0}
    
    for repo in repos:
        result = notion.upsert_repository(repo)
        stats[result] += 1
        print(f"[{result.upper()}] {repo.full_name}")
    
    # Step 3: 輸出統計
    print(f"\n✅ Done!")
    print(f"   Created: {stats['created']}")
    print(f"   Updated: {stats['updated']}")
    print(f"   Skipped: {stats['skipped']}")
```

#### 7.2.5 執行結果範例

```
2025-01-17 10:00:00 | INFO | Loading existing pages from Notion...
2025-01-17 10:00:02 | INFO | Loaded 150 existing pages

[SKIP] ollama/ollama (no changes)
[SKIP] cline/cline (no changes)
[UPDATE] anthropics/claude-code (stars: 5000 → 5234)
[CREATE] new-project/awesome-tool (new project)
...

✅ Done!
   Created: 12
   Updated: 28
   Skipped: 110
```

#### 7.2.6 額外追蹤欄位（選配）

如果想追蹤星星變化趨勢，可以新增這些欄位：

| 欄位名稱 | Notion 類型 | 說明 |
|----------|-------------|------|
| Previous Stars | Number | 上次爬取的星星數 |
| Stars Growth | Number | 星星成長數（本次 - 上次）|
| Last Fetched | Date | 上次爬取時間 |

這樣每次更新時，可以計算並記錄成長趨勢！

### 7.3 錯誤處理策略

| 錯誤類型 | 處理方式 |
|----------|----------|
| GitHub Rate Limit | 等待 60 秒後重試，或提早結束並記錄 |
| Search Rate Limit | 每次搜尋後等待 2 秒 |
| 網路錯誤 | 重試 3 次，間隔指數退避 |
| 資料格式錯誤 | 記錄錯誤，跳過該筆資料 |
| Notion 寫入失敗 | 記錄錯誤，繼續處理下一筆 |

---

## 8. 設定與環境變數

### 8.1 環境變數 (.env)

```env
# GitHub API
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Notion API
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 選配設定
LOG_LEVEL=INFO
MAX_REPOS_PER_TOPIC=50
REQUEST_TIMEOUT=30
SEARCH_DELAY_SECONDS=2
```

### 8.2 取得 API Keys 步驟

**GitHub Token**:
1. 前往 GitHub Settings > Developer settings > Personal access tokens
2. 點擊 "Generate new token (classic)"
3. 勾選 `public_repo` 權限
4. 產生並複製 Token

**Notion Integration**:
1. 前往 https://www.notion.so/my-integrations
2. 點擊 "New integration"
3. 設定名稱，選擇 Workspace
4. 複製 Internal Integration Token
5. 在 Notion 資料庫頁面，點擊 "..." > "Add connections" > 選擇你的 Integration

---

## 9. Notion 資料庫建立指南

### 9.1 建立步驟

1. 在 Notion 建立新的 Database（Full page）
2. 設定以下欄位：

| 欄位名稱 | 類型 | 設定 |
|----------|------|------|
| Name | Title | (預設) |
| Full Name | Text | |
| Description | Text | |
| Stars | Number | Format: Number with commas |
| Forks | Number | Format: Number with commas |
| Language | Select | 動態新增選項 |
| Ecosystem | Select | 預先建立 6 個選項 |
| Topics | Multi-select | 動態新增選項 |
| GitHub URL | URL | |
| Homepage | URL | |
| License | Select | 動態新增選項 |
| Created At | Date | |
| Updated At | Date | |
| Fetched At | Date | |

### 9.2 Ecosystem 選項設定

| 選項名稱 | 顏色建議 |
|----------|----------|
| 🎨 Vibe Coding IDE | Purple |
| 🚀 Antigravity | Blue |
| 🤖 AI Coding Agents | Green |
| 📚 NotebookLM | Orange |
| 🔧 AI Infrastructure | Gray |
| 📄 PDF Tools | Yellow |

### 9.3 建議的 View 設定

**View 1: By Ecosystem（看板視圖）**
- Group by: Ecosystem
- Sort: Stars (Descending)

**View 2: All Projects（表格視圖）**
- Sort: Stars (Descending)

**View 3: NotebookLM Only（表格視圖）**
- Filter: Ecosystem = 📚 NotebookLM
- Sort: Stars (Descending)

**View 4: Recently Updated（表格視圖）**
- Sort: Updated At (Descending)

---

## 10. 預期輸出範例

### 10.1 Notion 資料庫預覽

| Name | Stars ⭐ | Ecosystem | Language | Description |
|------|---------|-----------|----------|-------------|
| ollama | 150,000 | 🔧 AI Infrastructure | Go | Get up and running with Llama 3... |
| cline | 39,000 | 🤖 AI Coding Agents | TypeScript | Autonomous coding agent... |
| open-notebooklm | 1,200 | 📚 NotebookLM | Python | Open source NotebookLM alternative |
| notebooklm-pdf-to-pptx | 114 | 📚 NotebookLM | HTML | Convert PDFs to PPTX with layers... |
| antigravity-manager | 521 | 🚀 Antigravity | TypeScript | Multi-account manager |

### 10.2 執行日誌範例

```
2025-01-17 10:00:00 | INFO | Starting GitHub AI Tracker...
2025-01-17 10:00:01 | INFO | Loaded 6 ecosystems with 25 topics
2025-01-17 10:00:02 | INFO | [vibe_coding_ide] Searching: cursor
2025-01-17 10:00:03 | INFO | [vibe_coding_ide] Found 45 repositories
2025-01-17 10:00:05 | INFO | [notebooklm] Searching: notebooklm
2025-01-17 10:00:06 | INFO | [notebooklm] Found 28 repositories
...
2025-01-17 10:02:30 | INFO | Total unique repositories: 312
2025-01-17 10:02:31 | INFO | Syncing to Notion...
2025-01-17 10:03:45 | INFO | Created: 45, Updated: 267
2025-01-17 10:03:45 | INFO | Done! ✅
```

---

## 11. 定時任務設定（GitHub Actions）

### 11.1 概述

使用 GitHub Actions 實現每週自動執行爬蟲，免費且安全。

| 項目 | 設定 |
|------|------|
| 執行頻率 | 每週一次 |
| 執行時間 | 台北時間 週一 06:00 |
| UTC 時間 | 週日 22:00 |
| Cron 表達式 | `0 22 * * 0` |

### 11.2 Workflow 檔案

建立 `.github/workflows/crawler.yml`：

```yaml
name: GitHub AI Tracker

on:
  # 定時執行：台北時間每週一早上 6 點
  schedule:
    - cron: '0 22 * * 0'  # UTC 週日 22:00 = 台北週一 06:00
  
  # 也可以手動觸發（方便測試）
  workflow_dispatch:

jobs:
  crawl:
    runs-on: ubuntu-latest
    
    steps:
      # 1. 取得程式碼
      - name: Checkout repository
        uses: actions/checkout@v4
      
      # 2. 安裝 Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      # 3. 安裝 uv
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      # 4. 安裝依賴
      - name: Install dependencies
        run: uv sync
      
      # 5. 執行爬蟲
      - name: Run crawler
        env:
          GITHUB_TOKEN: ${{ secrets.GH_API_TOKEN }}
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        run: uv run python src/main.py
```

### 11.3 設定 GitHub Secrets

在 GitHub Repo 中設定以下 Secrets：

```
位置：Repo → Settings → Secrets and variables → Actions → New repository secret
```

| Secret 名稱 | 值 | 說明 |
|-------------|-----|------|
| `GH_API_TOKEN` | `ghp_xxx...` | GitHub Personal Access Token |
| `NOTION_TOKEN` | `secret_xxx...` | Notion Integration Token |
| `NOTION_DATABASE_ID` | `abc123...` | Notion 資料庫 ID |

> ⚠️ 注意：GitHub Token 的 Secret 名稱用 `GH_API_TOKEN` 而非 `GITHUB_TOKEN`，因為 `GITHUB_TOKEN` 是 GitHub Actions 的保留名稱。

### 11.4 專案目錄結構（含 GitHub Actions）

```
github-ai-tracker/
├── .github/
│   └── workflows/
│       └── crawler.yml      ← GitHub Actions 設定
├── src/
│   ├── main.py
│   └── ...
├── pyproject.toml
├── CLAUDE.md                ← Spec 規格書
└── README.md
```

### 11.5 手動觸發測試

設定完成後，可以手動測試：

```
GitHub Repo → Actions → GitHub AI Tracker → Run workflow
```

### 11.6 執行紀錄

每次執行後可在 Actions 頁面查看：
- ✅ 成功 / ❌ 失敗
- 執行時間
- 詳細日誌

---

## 12. 未來擴展（Optional）

### Phase 2
- [ ] 每週趨勢報告自動發送 Email
- [ ] Discord/Slack 通知新專案
- [ ] 錯誤時自動通知

### Phase 3
- [ ] Web Dashboard 視覺化
- [ ] 專案品質評分
- [ ] 相似專案推薦

---

## 12. 參考資源

### 官方文件
- [GitHub REST API](https://docs.github.com/en/rest)
- [Notion API](https://developers.notion.com/)
- [uv Documentation](https://docs.astral.sh/uv/)

### 相關專案
- NotebookLM PDF to PPTX - PDF 圖層分離工具
- PDF-Extract-Kit - PDF 內容提取
- awesome-vibe-coding - Vibe Coding 工具清單

---

## 附錄：完整 Topics 清單

```python
ALL_TOPICS = [
    # Vibe Coding IDE
    "vibe-coding", "cursor", "cursor-ai", "cursor-rules", 
    "windsurf", "windsurf-ai",
    
    # Antigravity
    "antigravity", "antigravity-ide", "antigravity-ai", "gemini-cli",
    
    # AI Coding Agents
    "ai-agent", "coding-assistant", "claude-code", 
    "cline", "aider", "continue", "copilot",
    
    # NotebookLM
    "notebooklm", "pdf-to-pptx", "pdf-text-extraction",
    "ai-podcast", "open-notebooklm",
    
    # AI Infrastructure
    "llm", "ollama", "local-llm", "rag", "ragflow",
    "mcp", "langchain", "langflow", "vllm",
    
    # PDF Tools
    "pdf-extract", "pdf-parser", "ocr", 
    "document-ai", "pdf-to-markdown",
]
```

---

**文件版本**: 1.0 | **最後更新**: 2025-01-17
