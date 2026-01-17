"""GitHub API Client for searching repositories"""

import asyncio
from typing import AsyncGenerator

import httpx

from src.config import (
    GITHUB_TOKEN,
    GITHUB_API_BASE_URL,
    GITHUB_API_VERSION,
    TOPICS,
    MAX_REPOS_PER_TOPIC,
    REQUEST_TIMEOUT,
    SEARCH_DELAY_SECONDS,
    get_tool_categories,
    EcosystemType,
)
from src.models.repository import Repository
from src.utils.logger import logger


class GitHubClient:
    """GitHub API 客戶端"""

    def __init__(self, token: str | None = None):
        self.token = token or GITHUB_TOKEN
        self.base_url = GITHUB_API_BASE_URL
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def search_by_topic(
        self,
        topic: str,
        ecosystem: EcosystemType,
        max_results: int = MAX_REPOS_PER_TOPIC,
    ) -> list[Repository]:
        """
        根據 topic 搜尋 GitHub repositories

        Args:
            topic: GitHub topic 名稱
            ecosystem: 所屬生態系分類
            max_results: 最大回傳數量

        Returns:
            Repository 列表
        """
        repos: list[Repository] = []
        page = 1
        per_page = min(100, max_results)  # GitHub API 最多一次 100 筆

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            while len(repos) < max_results:
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": f"topic:{topic}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": per_page,
                    "page": page,
                }

                try:
                    response = await client.get(url, headers=self.headers, params=params)
                    response.raise_for_status()
                    data = response.json()

                    items = data.get("items", [])
                    if not items:
                        break

                    for item in items:
                        if len(repos) >= max_results:
                            break

                        # 計算工具分類
                        repo_topics = item.get("topics", [])
                        tool_categories = get_tool_categories(repo_topics)

                        repo = Repository.from_github_response(
                            data=item,
                            ecosystem=ecosystem,
                            matched_topic=topic,
                            tool_categories=tool_categories,
                        )
                        repos.append(repo)

                    # 檢查是否還有更多頁
                    total_count = data.get("total_count", 0)
                    if page * per_page >= total_count:
                        break

                    page += 1

                    # Rate limit: Search API 每分鐘 30 次
                    await asyncio.sleep(SEARCH_DELAY_SECONDS)

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 403:
                        # Rate limit exceeded
                        logger.warning(f"Rate limit exceeded for topic '{topic}', stopping search")
                        break
                    elif e.response.status_code == 422:
                        # Validation failed (可能是搜尋語法問題)
                        logger.warning(f"Search validation failed for topic '{topic}': {e}")
                        break
                    else:
                        logger.error(f"HTTP error searching topic '{topic}': {e}")
                        raise
                except httpx.RequestError as e:
                    logger.error(f"Request error searching topic '{topic}': {e}")
                    raise

        logger.info(f"[{ecosystem}] Found {len(repos)} repositories for topic '{topic}'")
        return repos

    async def search_all_topics(self) -> AsyncGenerator[tuple[str, list[Repository]], None]:
        """
        搜尋所有設定的 topics

        Yields:
            (ecosystem, repos) tuple
        """
        for ecosystem, topics in TOPICS.items():
            ecosystem_repos: list[Repository] = []

            for topic in topics:
                logger.info(f"[{ecosystem}] Searching topic: {topic}")

                try:
                    repos = await self.search_by_topic(
                        topic=topic,
                        ecosystem=ecosystem,  # type: ignore
                    )
                    ecosystem_repos.extend(repos)

                    # Rate limit between topics
                    await asyncio.sleep(SEARCH_DELAY_SECONDS)

                except Exception as e:
                    logger.error(f"Error searching topic '{topic}': {e}")
                    continue

            yield ecosystem, ecosystem_repos

    async def fetch_all_repositories(self) -> list[Repository]:
        """
        爬取所有生態系的 repositories 並去重

        Returns:
            去重後的 Repository 列表，依星星數排序
        """
        all_repos: dict[str, Repository] = {}  # 使用 full_name 作為 key 去重

        async for ecosystem, repos in self.search_all_topics():
            for repo in repos:
                # 如果已存在，保留星星數較高的（或更新的）
                if repo.full_name in all_repos:
                    existing = all_repos[repo.full_name]
                    # 合併 tool_categories
                    merged_categories = list(
                        set(existing.tool_categories + repo.tool_categories)
                    )
                    # 保留較新的資料並合併分類
                    if repo.updated_at > existing.updated_at:
                        repo.tool_categories = merged_categories
                        all_repos[repo.full_name] = repo
                    else:
                        existing.tool_categories = merged_categories
                else:
                    all_repos[repo.full_name] = repo

        # 依星星數排序
        sorted_repos = sorted(
            all_repos.values(),
            key=lambda r: r.stargazers_count,
            reverse=True,
        )

        logger.info(f"Total unique repositories: {len(sorted_repos)}")
        return sorted_repos

    async def check_rate_limit(self) -> dict:
        """檢查目前的 API rate limit 狀態"""
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            url = f"{self.base_url}/rate_limit"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
