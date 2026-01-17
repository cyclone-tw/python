"""Notion API Client for syncing repository data"""

from datetime import datetime
from typing import Any

from notion_client import Client

from src.config import NOTION_TOKEN, NOTION_DATABASE_ID, ECOSYSTEM_DISPLAY_NAMES
from src.models.repository import Repository
from src.utils.logger import logger


class NotionSync:
    """Notion 資料庫同步客戶端"""

    def __init__(
        self,
        token: str | None = None,
        database_id: str | None = None,
    ):
        self.token = token or NOTION_TOKEN
        self.database_id = database_id or NOTION_DATABASE_ID
        self.client = Client(auth=self.token)
        self.existing_pages: dict[str, dict[str, Any]] = {}  # {full_name: {page_id, updated_at, stars}}

    def load_existing_pages(self) -> None:
        """載入 Notion 資料庫中現有的所有專案"""
        results = []
        has_more = True
        start_cursor = None

        logger.info("Loading existing pages from Notion...")

        while has_more:
            response = self.client.databases.query(
                database_id=self.database_id,
                start_cursor=start_cursor,
            )
            results.extend(response["results"])
            has_more = response["has_more"]
            start_cursor = response.get("next_cursor")

        # 建立對照表
        for page in results:
            props = page["properties"]

            # 取得 Full Name
            full_name_prop = props.get("Full Name", {})
            rich_text = full_name_prop.get("rich_text", [])
            if not rich_text:
                continue
            full_name = rich_text[0].get("plain_text", "")

            # 取得 Updated At
            updated_at_prop = props.get("Updated At", {})
            date_value = updated_at_prop.get("date")
            updated_at = None
            if date_value and date_value.get("start"):
                try:
                    updated_at = datetime.fromisoformat(date_value["start"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            # 取得目前星星數（用於計算成長）
            stars_prop = props.get("Stars", {})
            current_stars = stars_prop.get("number", 0)

            self.existing_pages[full_name] = {
                "page_id": page["id"],
                "updated_at": updated_at,
                "stars": current_stars,
            }

        logger.info(f"Loaded {len(self.existing_pages)} existing pages from Notion")

    def upsert_repository(self, repo: Repository) -> str:
        """
        Upsert 單一專案到 Notion

        Returns:
            "created" | "updated" | "skipped"
        """
        full_name = repo.full_name

        if full_name in self.existing_pages:
            existing = self.existing_pages[full_name]

            # 比較更新時間（如果 existing 沒有更新時間，則強制更新）
            should_update = True
            if existing["updated_at"] is not None:
                # 移除時區資訊進行比較（避免 naive vs aware 問題）
                existing_time = existing["updated_at"].replace(tzinfo=None)
                repo_time = repo.updated_at.replace(tzinfo=None)
                should_update = repo_time > existing_time

            if should_update:
                # GitHub 資料較新，執行更新
                previous_stars = existing.get("stars", 0)
                self._update_page(existing["page_id"], repo, previous_stars)
                return "updated"
            else:
                # 資料沒有變化，跳過
                return "skipped"
        else:
            # 新專案，執行新增
            self._create_page(repo)
            return "created"

    def _create_page(self, repo: Repository) -> None:
        """新增頁面到 Notion"""
        self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=self._build_properties(repo, previous_stars=None),
        )

    def _update_page(self, page_id: str, repo: Repository, previous_stars: int | None) -> None:
        """更新現有頁面"""
        self.client.pages.update(
            page_id=page_id,
            properties=self._build_properties(repo, previous_stars),
        )

    def _build_properties(self, repo: Repository, previous_stars: int | None) -> dict:
        """建構 Notion 頁面屬性"""
        properties: dict[str, Any] = {
            "Name": {"title": [{"text": {"content": repo.name}}]},
            "Full Name": {"rich_text": [{"text": {"content": repo.full_name}}]},
            "Stars": {"number": repo.stargazers_count},
            "Forks": {"number": repo.forks_count},
            "Open Issues": {"number": repo.open_issues_count},
            "GitHub URL": {"url": str(repo.html_url)},
            "Fetched At": {"date": {"start": repo.fetched_at.isoformat()}},
        }

        # Description (可能很長，截斷到 2000 字元)
        description = repo.description or ""
        if len(description) > 2000:
            description = description[:1997] + "..."
        properties["Description"] = {"rich_text": [{"text": {"content": description}}]}

        # Language (Select)
        if repo.language:
            properties["Language"] = {"select": {"name": repo.language}}

        # Ecosystem (Select) - 使用顯示名稱
        ecosystem_display = ECOSYSTEM_DISPLAY_NAMES.get(repo.ecosystem, repo.ecosystem)
        properties["Ecosystem"] = {"select": {"name": ecosystem_display}}

        # Tool Category (Multi-select)
        if repo.tool_categories:
            properties["Tool Category"] = {
                "multi_select": [{"name": cat} for cat in repo.tool_categories]
            }

        # Topics (Multi-select) - 限制數量避免太多
        if repo.topics:
            limited_topics = repo.topics[:10]  # 最多 10 個 topics
            properties["Topics"] = {
                "multi_select": [{"name": topic} for topic in limited_topics]
            }

        # Homepage (URL)
        if repo.homepage:
            properties["Homepage"] = {"url": repo.homepage}

        # License (Select)
        if repo.license_name:
            properties["License"] = {"select": {"name": repo.license_name}}

        # Created At & Updated At (Date)
        properties["Created At"] = {"date": {"start": repo.created_at.isoformat()}}
        properties["Updated At"] = {"date": {"start": repo.updated_at.isoformat()}}

        # Previous Stars (用於追蹤成長)
        if previous_stars is not None:
            properties["Previous Stars"] = {"number": previous_stars}

        return properties

    def sync_repositories(self, repos: list[Repository]) -> dict[str, int]:
        """
        同步多個 repositories 到 Notion

        Args:
            repos: Repository 列表

        Returns:
            統計結果 {"created": n, "updated": n, "skipped": n}
        """
        # Step 1: 載入現有資料
        self.load_existing_pages()

        # Step 2: Upsert 每個專案
        stats = {"created": 0, "updated": 0, "skipped": 0}

        for i, repo in enumerate(repos, 1):
            try:
                result = self.upsert_repository(repo)
                stats[result] += 1

                # 顯示進度
                if result == "skipped":
                    logger.debug(f"[{i}/{len(repos)}] SKIP: {repo.full_name}")
                else:
                    logger.info(
                        f"[{i}/{len(repos)}] {result.upper()}: {repo.full_name} "
                        f"(stars: {repo.stargazers_count})"
                    )

            except Exception as e:
                logger.error(f"Error syncing {repo.full_name}: {e}")
                continue

        # Step 3: 輸出統計
        logger.info(
            f"Sync completed! Created: {stats['created']}, "
            f"Updated: {stats['updated']}, Skipped: {stats['skipped']}"
        )

        return stats
