"""Hugging Face Blog 抓取模組 - 技術趨勢與模型發布"""

import asyncio
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

import feedparser
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

from ..database import insert_article
from ..utils import clean_markdown


class HuggingFaceBlogScraper:
    """Hugging Face Blog 爬蟲 (使用 RSS Feed)"""

    RSS_URL = "https://huggingface.co/blog/feed.xml"
    BASE_URL = "https://huggingface.co/blog"
    SOURCE_NAME = "huggingface_blog"

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "articles" / self.SOURCE_NAME
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def scrape(self) -> int:
        """
        抓取 Hugging Face Blog 最新文章

        Returns:
            int: 新增的文章數量
        """
        new_count = 0

        try:
            # 使用 feedparser 解析 RSS
            feed = await asyncio.to_thread(feedparser.parse, self.RSS_URL)

            if feed.bozo:
                print(f"[HF Blog] RSS 解析警告: {feed.bozo_exception}")

            entries = feed.entries[:10]  # 限制數量
            print(f"[HF Blog] 從 RSS 發現 {len(entries)} 篇文章")

            browser_config = BrowserConfig(headless=True)
            # 文章頁配置 - 只提取正文內容
            crawl_config = CrawlerRunConfig(
                word_count_threshold=50,
                wait_until="domcontentloaded",
                page_timeout=30000,
                css_selector="article, .prose, main .blog-content, .markdown-body",
                excluded_selector="nav, header, footer, .sidebar, .toc, script, style, .author-info"
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                for entry in entries:
                    title = entry.get("title", "").strip()
                    url = entry.get("link", "")

                    if not title or not url:
                        continue

                    try:
                        saved = await self._fetch_and_save_article(
                            crawler, crawl_config, url, title
                        )
                        if saved:
                            new_count += 1
                            print(f"[HF Blog] 新增: {title}")
                    except asyncio.TimeoutError:
                        print(f"[HF Blog] 超時跳過: {title}")
                    except Exception as e:
                        print(f"[HF Blog] 抓取失敗 {title}: {e}")

        except Exception as e:
            print(f"[HF Blog] 爬蟲錯誤: {e}")

        return new_count

    async def _fetch_and_save_article(
        self,
        crawler: AsyncWebCrawler,
        config: CrawlerRunConfig,
        url: str,
        title: str
    ) -> bool:
        """抓取並儲存單篇文章"""
        result = await crawler.arun(url=url, config=config)

        if not result.success:
            return False

        # 儲存 Markdown 檔案
        content_path = await self._save_markdown(title, url, result.markdown)

        # 寫入資料庫
        return await insert_article(
            url=url,
            title=title,
            source=self.SOURCE_NAME,
            content_path=str(content_path) if content_path else None
        )

    async def _save_markdown(self, title: str, url: str, content: str) -> Optional[Path]:
        """儲存 Markdown 內容到檔案"""
        if not content:
            return None

        # 清理 Markdown 雜訊
        cleaned_content = clean_markdown(content)
        if not cleaned_content:
            return None

        # 加入文章元資料
        header = f"""---
title: {title}
source: {self.SOURCE_NAME}
url: {url}
date: {datetime.now().strftime("%Y-%m-%d")}
---

"""
        final_content = header + cleaned_content

        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:50]
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{date_str}_{safe_title}.md"
        filepath = self.data_dir / filename

        filepath.write_text(final_content, encoding="utf-8")
        return filepath
