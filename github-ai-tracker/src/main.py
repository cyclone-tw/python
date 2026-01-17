"""
GitHub AI Tracker - 主程式入口

自動爬取 AI 開發工具、Vibe Coding、NotebookLM 生態系相關的熱門 GitHub 專案，
並將結果同步到 Notion 資料庫。
"""

import asyncio
import sys
from datetime import datetime

from src.config import validate_config, TOPICS
from src.clients.github_client import GitHubClient
from src.clients.notion_client import NotionSync
from src.utils.logger import logger


async def main() -> None:
    """主程式"""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Starting GitHub AI Tracker...")
    logger.info("=" * 60)

    # Step 1: 驗證設定
    missing_config = validate_config()
    if missing_config:
        logger.error(f"Missing required configuration: {', '.join(missing_config)}")
        logger.error("Please check your .env file")
        sys.exit(1)

    # 顯示設定摘要
    total_topics = sum(len(topics) for topics in TOPICS.values())
    logger.info(f"Loaded {len(TOPICS)} ecosystems with {total_topics} topics")

    # Step 2: 爬取 GitHub 資料
    logger.info("-" * 40)
    logger.info("Phase 1: Fetching repositories from GitHub...")
    logger.info("-" * 40)

    github_client = GitHubClient()

    # 檢查 rate limit
    try:
        rate_limit = await github_client.check_rate_limit()
        search_limit = rate_limit.get("resources", {}).get("search", {})
        logger.info(
            f"GitHub Search API Rate Limit: "
            f"{search_limit.get('remaining', '?')}/{search_limit.get('limit', '?')}"
        )
    except Exception as e:
        logger.warning(f"Could not check rate limit: {e}")

    # 爬取所有 repositories
    try:
        repositories = await github_client.fetch_all_repositories()
    except Exception as e:
        logger.error(f"Failed to fetch repositories: {e}")
        sys.exit(1)

    if not repositories:
        logger.warning("No repositories found!")
        return

    logger.info(f"Total unique repositories fetched: {len(repositories)}")

    # 顯示 Top 10
    logger.info("Top 10 repositories by stars:")
    for i, repo in enumerate(repositories[:10], 1):
        logger.info(f"  {i}. {repo.full_name} - {repo.stargazers_count:,} stars")

    # Step 3: 同步到 Notion
    logger.info("-" * 40)
    logger.info("Phase 2: Syncing to Notion database...")
    logger.info("-" * 40)

    notion_sync = NotionSync()

    try:
        stats = notion_sync.sync_repositories(repositories)
    except Exception as e:
        logger.error(f"Failed to sync to Notion: {e}")
        sys.exit(1)

    # Step 4: 輸出執行摘要
    elapsed = datetime.now() - start_time
    logger.info("=" * 60)
    logger.info("Execution Summary")
    logger.info("=" * 60)
    logger.info(f"Total repositories processed: {len(repositories)}")
    logger.info(f"  - Created: {stats['created']}")
    logger.info(f"  - Updated: {stats['updated']}")
    logger.info(f"  - Skipped: {stats['skipped']}")
    logger.info(f"Elapsed time: {elapsed.total_seconds():.1f} seconds")
    logger.info("=" * 60)
    logger.info("Done!")


def run() -> None:
    """同步執行入口（供命令列使用）"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
