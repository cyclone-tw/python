"""GitHub API Client for searching repositories"""

import asyncio
from typing import AsyncGenerator

import httpx

from src.config import (
    GITHUB_TOKEN,
    GITHUB_API_BASE_URL,
    GITHUB_API_VERSION,
    TOPICS,
    MAX_REPOS_PER_ECOSYSTEM,
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

    async def _search_repos(
        self,
        query: str,
        ecosystem: EcosystemType,
        matched_topic: str,
        sort_by: str = "forks",
        max_results: int = 100,
    ) -> list[Repository]:
        """
        執行 GitHub 搜尋

        Args:
            query: 搜尋查詢字串
            ecosystem: 所屬生態系分類
            matched_topic: 匹配的 topic 名稱
            sort_by: 排序方式 (forks, stars, updated)
            max_results: 最大回傳數量

        Returns:
            Repository 列表
        """
        repos: list[Repository] = []
        page = 1
        per_page = min(100, max_results)

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            while len(repos) < max_results:
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": query,
                    "sort": sort_by,
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

                        repo_topics = item.get("topics", [])
                        tool_categories = get_tool_categories(repo_topics)

                        repo = Repository.from_github_response(
                            data=item,
                            ecosystem=ecosystem,
                            matched_topic=matched_topic,
                            tool_categories=tool_categories,
                        )
                        repos.append(repo)

                    total_count = data.get("total_count", 0)
                    if page * per_page >= total_count:
                        break

                    page += 1
                    await asyncio.sleep(SEARCH_DELAY_SECONDS)

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 403:
                        logger.warning(f"Rate limit exceeded, stopping search")
                        break
                    elif e.response.status_code == 422:
                        logger.warning(f"Search validation failed: {e}")
                        break
                    else:
                        logger.error(f"HTTP error: {e}")
                        raise
                except httpx.RequestError as e:
                    logger.error(f"Request error: {e}")
                    raise

        return repos

    async def search_ecosystem(
        self,
        ecosystem: EcosystemType,
        topics: list[str],
        max_results: int = MAX_REPOS_PER_ECOSYSTEM,
    ) -> list[Repository]:
        """
        搜尋單一生態系，合併所有 topics 後取 Fork 數前 N 名

        Args:
            ecosystem: 生態系名稱
            topics: 該生態系的 topics 列表
            max_results: 最大回傳數量（預設 50）

        Returns:
            該生態系 Fork 數前 N 名的 Repository 列表
        """
        all_repos: dict[str, Repository] = {}

        for topic in topics:
            logger.info(f"[{ecosystem}] Searching topic: {topic}")

            try:
                repos = await self._search_repos(
                    query=f"topic:{topic}",
                    ecosystem=ecosystem,
                    matched_topic=topic,
                    sort_by="forks",
                    max_results=100,  # 每個 topic 先抓 100 個
                )

                for repo in repos:
                    if repo.full_name not in all_repos:
                        all_repos[repo.full_name] = repo
                    else:
                        # 合併 tool_categories
                        existing = all_repos[repo.full_name]
                        existing.tool_categories = list(
                            set(existing.tool_categories + repo.tool_categories)
                        )

                await asyncio.sleep(SEARCH_DELAY_SECONDS)

            except Exception as e:
                logger.error(f"Error searching topic '{topic}': {e}")
                continue

        # 依 Fork 數排序，取前 N 名
        sorted_repos = sorted(
            all_repos.values(),
            key=lambda r: r.forks_count,
            reverse=True,
        )[:max_results]

        logger.info(f"[{ecosystem}] Top {len(sorted_repos)} repositories by forks")
        return sorted_repos

    async def search_chinese_projects(
        self,
        max_results: int = MAX_REPOS_PER_ECOSYSTEM,
    ) -> list[Repository]:
        """
        搜尋 README 含有繁體中文的 AI 相關專案

        Returns:
            繁體中文專案列表（依 Fork 數排序）
        """
        logger.info("[chinese_traditional] Searching for Traditional Chinese projects...")

        # 搜尋關鍵字：繁體中文常見詞彙 + AI 相關
        chinese_keywords = [
            "繁體中文",
            "台灣",
            "中文說明",
            "Chinese README",
        ]

        ai_topics = ["llm", "ai", "chatgpt", "gpt", "langchain", "ollama"]

        all_repos: dict[str, Repository] = {}

        for keyword in chinese_keywords:
            for ai_topic in ai_topics[:3]:  # 限制組合數量
                query = f"{keyword} {ai_topic} in:readme"
                logger.info(f"[chinese_traditional] Searching: {keyword} + {ai_topic}")

                try:
                    repos = await self._search_repos(
                        query=query,
                        ecosystem="chinese_traditional",  # type: ignore
                        matched_topic=f"chinese-{ai_topic}",
                        sort_by="forks",
                        max_results=30,
                    )

                    for repo in repos:
                        if repo.full_name not in all_repos:
                            all_repos[repo.full_name] = repo

                    await asyncio.sleep(SEARCH_DELAY_SECONDS)

                except Exception as e:
                    logger.error(f"Error searching Chinese projects: {e}")
                    continue

        # 依 Fork 數排序
        sorted_repos = sorted(
            all_repos.values(),
            key=lambda r: r.forks_count,
            reverse=True,
        )[:max_results]

        logger.info(f"[chinese_traditional] Found {len(sorted_repos)} Traditional Chinese projects")
        return sorted_repos

    async def fetch_all_repositories(self) -> list[Repository]:
        """
        爬取所有生態系的 repositories

        Returns:
            去重後的 Repository 列表，依 Fork 數排序
        """
        all_repos: dict[str, Repository] = {}

        # 1. 爬取各生態系
        for ecosystem, topics in TOPICS.items():
            logger.info(f"{'='*20} {ecosystem} {'='*20}")

            repos = await self.search_ecosystem(
                ecosystem=ecosystem,  # type: ignore
                topics=topics,
            )

            for repo in repos:
                if repo.full_name not in all_repos:
                    all_repos[repo.full_name] = repo
                else:
                    existing = all_repos[repo.full_name]
                    existing.tool_categories = list(
                        set(existing.tool_categories + repo.tool_categories)
                    )

        # 2. 爬取繁體中文專案
        logger.info(f"{'='*20} chinese_traditional {'='*20}")
        chinese_repos = await self.search_chinese_projects()

        for repo in chinese_repos:
            if repo.full_name not in all_repos:
                all_repos[repo.full_name] = repo

        # 依 Fork 數排序
        sorted_repos = sorted(
            all_repos.values(),
            key=lambda r: r.forks_count,
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
