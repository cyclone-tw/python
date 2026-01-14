# 開發記錄 (Development Log)

> 本文件設計為**人類與 AI 都能理解**的格式，方便後續接手開發。
> 包含：版本歷史、技術決策、程式碼位置、API 介面、待辦事項。

---

## 專案概覽

| 項目 | 說明 |
|------|------|
| 專案名稱 | AI Pulse Monitor |
| 目的 | 自動抓取 AI 新聞並轉換為結構化 Markdown |
| 當前版本 | 0.2.0 |
| 主要語言 | Python 3.11+ |
| 套件管理 | uv |

---

## 版本歷史

### [0.2.0] - 2026-01-14

#### 修復：Crawl4AI 0.7.x API 相容性

**問題**：Crawl4AI 更新至 0.7.x 後，`CrawlerRunConfig` 不再支援 `content_filter` 參數。

**解決方案**：
```python
# 舊版 (不再支援)
crawl_config = CrawlerRunConfig(
    content_filter=PruningContentFilter(threshold=0.4)
)

# 新版 (0.7.x)
crawl_config = CrawlerRunConfig(
    word_count_threshold=50,
    css_selector="article, .content",
    excluded_selector="nav, header, footer, .sidebar"
)
```

**影響檔案**：
- `ai_pulse_monitor/scrapers/tldr_ai.py`
- `ai_pulse_monitor/scrapers/the_decoder.py`
- `ai_pulse_monitor/scrapers/huggingface_blog.py`

---

#### 新增：Markdown 清理工具 (`utils.py`)

**檔案位置**：`ai_pulse_monitor/utils.py`

**功能**：移除爬蟲抓取的 HTML 雜訊，包括：
- 頭像連結 (cdn-avatars.huggingface.co)
- 廣告標記 (Ad, DEC_D_Incontent-*)
- 訂閱推廣區塊
- 空連結、Follow 按鈕
- LinkedIn Profile 連結

**主要函式**：
```python
def clean_markdown(content: str) -> str:
    """
    清理 Markdown 內容，移除雜訊

    Args:
        content: 原始 Markdown 內容

    Returns:
        清理後的 Markdown 內容
    """
```

**使用方式**：
```python
from ai_pulse_monitor.utils import clean_markdown

cleaned = clean_markdown(raw_markdown)
```

**擴展清理規則**：在 `clean_markdown()` 函式內新增 regex 規則即可。

---

#### 新增：YAML Frontmatter 元資料

**功能**：每篇文章開頭自動加入結構化元資料。

**格式**：
```yaml
---
title: 文章標題
source: the_decoder
url: https://example.com/article
date: 2026-01-14
---
```

**實作位置**：各爬蟲的 `_save_markdown()` 方法

**程式碼範例**：
```python
async def _save_markdown(self, title: str, url: str, content: str) -> Optional[Path]:
    header = f"""---
title: {title}
source: {self.SOURCE_NAME}
url: {url}
date: {datetime.now().strftime("%Y-%m-%d")}
---

"""
    final_content = header + cleaned_content
```

---

### [0.1.0] - 2026-01-14

#### 專案初始化

**建立檔案結構**：
```
ai_pulse_monitor/
├── __init__.py          # 版本號: 0.1.0
├── main.py              # CLI 入口點
├── database.py          # SQLite 操作
├── summarizer.py        # 摘要預留端口
├── utils.py             # 工具函式
└── scrapers/
    ├── __init__.py      # 匯出所有爬蟲類別
    ├── tldr_ai.py       # TLDR AI 爬蟲
    ├── the_decoder.py   # The Decoder 爬蟲
    └── huggingface_blog.py  # HF Blog 爬蟲
```

---

## 模組介面說明

### database.py

```python
async def init_db() -> None
    """初始化資料庫，建立 articles 表"""

async def insert_article(url: str, title: str, source: str, content_path: Optional[str]) -> bool
    """插入文章，回傳 True 表示新增成功，False 表示已存在"""

async def get_pending_summaries() -> list[dict]
    """取得所有 is_summarized=0 的文章"""

async def mark_as_summarized(url: str) -> None
    """將文章標記為已摘要"""

async def get_article_count() -> dict
    """回傳 {"total": int, "summarized": int, "pending": int}"""
```

### scrapers/*.py

每個爬蟲類別都遵循相同介面：

```python
class XXXScraper:
    SOURCE_NAME: str          # 來源識別碼

    def __init__(self, data_dir: Path):
        """初始化，設定資料儲存目錄"""

    async def scrape(self) -> int:
        """執行抓取，回傳新增文章數量"""
```

### summarizer.py

```python
class Summarizer:
    async def summarize_article(self, content_path: str) -> Optional[str]
        """對單篇文章進行摘要（待實作）"""

    async def generate_daily_digest(self) -> Optional[str]
        """生成每日摘要報告（待實作）"""

async def process_pending_summaries() -> int
    """處理所有待摘要文章，回傳處理數量"""
```

---

## 資料流程圖

```
[新聞網站]
    ↓ (Crawl4AI + Playwright)
[HTML 頁面]
    ↓ (CrawlerRunConfig: css_selector, excluded_selector)
[原始 Markdown]
    ↓ (utils.clean_markdown)
[清理後 Markdown]
    ↓ (加入 YAML Frontmatter)
[最終 .md 檔案] → 儲存至 data/articles/{source}/
    ↓
[SQLite 資料庫] → 記錄 url, title, source, content_path
```

---

## 待辦事項 (TODO)

### 高優先級
- [ ] 實作摘要功能（建議使用 Gemini 2.0 Flash）
- [ ] 改進 The Decoder URL 過濾（目前會抓到分類頁面）

### 中優先級
- [ ] 新增更多新聞源（arXiv, MIT Tech Review, VentureBeat AI）
- [ ] 支援定時排程（cron / schedule 套件）
- [ ] 新增 Discord/Slack 通知

### 低優先級
- [ ] Web UI 儀表板
- [ ] 文章去重（基於內容相似度）
- [ ] 多語言摘要支援

---

## 技術決策記錄 (ADR)

### ADR-001: 選用 Crawl4AI 而非 Scrapy

**背景**：需要抓取 JavaScript 渲染的頁面並轉換為 Markdown。

**決策**：使用 Crawl4AI

**原因**：
1. 內建 Playwright 支援 JS 渲染
2. 原生 Markdown 輸出
3. 異步架構與專案設計一致
4. `css_selector` 和 `excluded_selector` 方便過濾內容

**取捨**：相比 Scrapy，社群較小，文件較少。

---

### ADR-002: 選用 aiosqlite 而非 PostgreSQL

**背景**：需要儲存文章元資料和抓取狀態。

**決策**：使用 aiosqlite（本地 SQLite）

**原因**：
1. 無需額外資料庫服務
2. 單檔案便於備份和遷移
3. 原生異步支援
4. 對於每日數十篇文章的規模足夠

**取捨**：不支援併發寫入，不適合大規模部署。

---

### ADR-003: 使用 YAML Frontmatter 而非純 JSON

**背景**：需要在 Markdown 檔案中嵌入元資料。

**決策**：使用 YAML Frontmatter

**原因**：
1. 人類可讀性佳
2. 大多數 Markdown 工具支援（Obsidian, Hugo, Jekyll）
3. 方便後續用 LLM 解析

---

## 已知問題

### Issue-001: The Decoder 抓取到分類頁面

**現象**：部分抓取結果是分類頁面（如 "AI and society"）而非單篇文章。

**原因**：`_is_article_url()` 過濾規則不夠精確。

**暫時解法**：這些頁面仍可作為索引使用。

**建議修復**：在 `the_decoder.py` 中增加 URL 路徑深度檢查或日期格式檢測。

---

## 環境資訊

```bash
# 檢查安裝的套件版本
uv pip list | grep -E "crawl4ai|playwright|aiosqlite|feedparser"

# 預期輸出
crawl4ai      0.7.8
playwright    1.57.0
aiosqlite     0.22.1
feedparser    6.0.12
```

---

## 聯絡與貢獻

如需接手開發，建議先閱讀：
1. 本文件了解整體架構
2. `main.py` 了解 CLI 入口
3. `scrapers/the_decoder.py` 作為爬蟲範本
4. `utils.py` 了解 Markdown 清理邏輯
