"""TLDR AI 抓取模組 - 每日 AI 快訊"""

import asyncio
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

from ..database import insert_article
from ..utils import clean_markdown


class TLDRAIScraper:
    """TLDR AI Newsletter 爬蟲"""

    BASE_URL = "https://tldr.tech/ai"
    SOURCE_NAME = "tldr_ai"

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "articles" / self.SOURCE_NAME
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def scrape(self) -> int:
        """
        抓取 TLDR AI 最新文章

        Returns:
            int: 新增的文章數量
        """
        new_count = 0
        browser_config = BrowserConfig(headless=True)
        # 列表頁配置
        list_config = CrawlerRunConfig(
            word_count_threshold=10,
            wait_until="domcontentloaded",
            page_timeout=30000
        )
        # 文章頁配置 - 只提取正文內容
        article_config = CrawlerRunConfig(
            word_count_threshold=50,
            wait_until="domcontentloaded",
            page_timeout=30000,
            css_selector="article, main, .content, .newsletter-content, .post-body",
            excluded_selector="nav, header, footer, .sidebar, .subscribe-form, .social-links, script, style"
        )

        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                # 抓取主頁取得文章列表
                result = await crawler.arun(
                    url=self.BASE_URL,
                    config=list_config
                )

                if not result.success:
                    print(f"[TLDR AI] 抓取主頁失敗: {result.error_message}")
                    return 0

                # 解析文章連結
                article_links = self._extract_article_links(result.html)
                print(f"[TLDR AI] 發現 {len(article_links)} 篇文章")

                # 逐一抓取文章內容
                for title, url in article_links[:10]:  # 限制每次抓取數量
                    try:
                        saved = await self._fetch_and_save_article(
                            crawler, article_config, url, title
                        )
                        if saved:
                            new_count += 1
                            print(f"[TLDR AI] 新增: {title}")
                    except asyncio.TimeoutError:
                        print(f"[TLDR AI] 超時跳過: {title}")
                    except Exception as e:
                        print(f"[TLDR AI] 抓取失敗 {title}: {e}")

        except Exception as e:
            print(f"[TLDR AI] 爬蟲錯誤: {e}")

        return new_count

    def _extract_article_links(self, html: str) -> list[tuple[str, str]]:
        """從 HTML 中提取文章連結"""
        links = []
        # 匹配 TLDR 的文章連結格式
        pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE)

        for url, title in matches:
            # 過濾出實際的文章連結
            if self._is_article_url(url):
                full_url = urljoin(self.BASE_URL, url)
                clean_title = title.strip()
                if clean_title and len(clean_title) > 10:
                    links.append((clean_title, full_url))

        # 去重
        seen = set()
        unique_links = []
        for title, url in links:
            if url not in seen:
                seen.add(url)
                unique_links.append((title, url))

        return unique_links

    def _is_article_url(self, url: str) -> bool:
        """判斷是否為文章 URL"""
        exclude_patterns = [
            "javascript:", "#", "mailto:", "twitter.com",
            "linkedin.com", "facebook.com", "/subscribe",
            "/advertise", "/about"
        ]
        return not any(p in url.lower() for p in exclude_patterns)

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

        # 清理標題作為檔名
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:50]
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{date_str}_{safe_title}.md"
        filepath = self.data_dir / filename

        filepath.write_text(final_content, encoding="utf-8")
        return filepath
