"""主控中心 - 整合所有模組的入口點"""

import argparse
import asyncio
import sys
from pathlib import Path

from .database import init_db, get_article_count
from .scrapers import TLDRAIScraper, TheDecoderScraper, HuggingFaceBlogScraper
from .summarizer import process_pending_summaries

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


async def sync_articles() -> None:
    """執行文章抓取同步"""
    print("=" * 50)
    print("AI Pulse Monitor - 開始同步文章")
    print("=" * 50)

    # 確保資料目錄存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "articles").mkdir(exist_ok=True)

    # 初始化資料庫
    await init_db()

    total_new = 0

    # 初始化所有爬蟲
    scrapers = [
        TLDRAIScraper(DATA_DIR),
        TheDecoderScraper(DATA_DIR),
        HuggingFaceBlogScraper(DATA_DIR),
    ]

    # 依序執行爬蟲
    for scraper in scrapers:
        print(f"\n{'─' * 40}")
        print(f"正在抓取: {scraper.SOURCE_NAME}")
        print("─" * 40)

        try:
            new_count = await scraper.scrape()
            total_new += new_count
        except Exception as e:
            print(f"爬蟲執行失敗: {e}")

    # 顯示統計
    stats = await get_article_count()
    print(f"\n{'=' * 50}")
    print("同步完成!")
    print(f"  本次新增: {total_new} 篇")
    print(f"  資料庫總計: {stats['total']} 篇")
    print(f"  已摘要: {stats['summarized']} 篇")
    print(f"  待摘要: {stats['pending']} 篇")
    print("=" * 50)


async def run_summarize() -> None:
    """執行摘要處理"""
    print("=" * 50)
    print("AI Pulse Monitor - 摘要處理")
    print("=" * 50)

    # 初始化資料庫（確保表存在）
    await init_db()

    await process_pending_summaries()


async def show_status() -> None:
    """顯示系統狀態"""
    await init_db()
    stats = await get_article_count()

    print("=" * 50)
    print("AI Pulse Monitor - 系統狀態")
    print("=" * 50)
    print(f"  資料庫總計: {stats['total']} 篇文章")
    print(f"  已摘要: {stats['summarized']} 篇")
    print(f"  待摘要: {stats['pending']} 篇")
    print("=" * 50)


def main() -> None:
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        prog="ai-pulse",
        description="AI Pulse Monitor - AI 新聞自動化抓取與摘要系統"
    )

    parser.add_argument(
        "--sync",
        action="store_true",
        help="抓取並同步最新文章"
    )

    parser.add_argument(
        "--summarize",
        action="store_true",
        help="處理待摘要的文章（預留端口）"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="顯示系統狀態"
    )

    args = parser.parse_args()

    # 預設顯示幫助
    if not any([args.sync, args.summarize, args.status]):
        parser.print_help()
        sys.exit(0)

    try:
        if args.sync:
            asyncio.run(sync_articles())
        elif args.summarize:
            asyncio.run(run_summarize())
        elif args.status:
            asyncio.run(show_status())
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"執行錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
