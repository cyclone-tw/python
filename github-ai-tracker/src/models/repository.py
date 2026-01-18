"""Repository data model"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, HttpUrl, field_validator


# 生態系分類類型
EcosystemType = Literal[
    "vibe_coding_ide",
    "antigravity",
    "ai_coding_agents",
    "notebooklm",
    "ai_infrastructure",
    "pdf_tools",
    "chinese_traditional",  # 繁體中文專案
]


class Repository(BaseModel):
    """GitHub Repository 資料模型"""

    # 基本資訊
    name: str  # 專案名稱
    full_name: str  # owner/repo
    description: Optional[str] = None  # 專案描述
    html_url: HttpUrl  # GitHub 網址
    homepage: Optional[str] = None  # 專案官網

    # 數據指標
    stargazers_count: int  # 星星數
    forks_count: int  # Fork 數
    open_issues_count: int  # Open Issues

    # 分類資訊
    language: Optional[str] = None  # 主要語言
    topics: list[str] = []  # Topics 標籤
    license_name: Optional[str] = None  # 授權類型

    # 時間資訊
    created_at: datetime  # 建立時間
    updated_at: datetime  # 更新時間

    # 自訂欄位
    ecosystem: EcosystemType  # 生態系分類
    tool_categories: list[str] = []  # 工具細分類（可多選）
    matched_topic: str  # 匹配的 Topic
    fetched_at: datetime  # 爬取時間

    @field_validator("homepage", mode="before")
    @classmethod
    def validate_homepage(cls, v: Optional[str]) -> Optional[str]:
        """驗證 homepage URL，空字串轉為 None"""
        if v is None or v == "":
            return None
        return v

    @classmethod
    def from_github_response(
        cls,
        data: dict,
        ecosystem: EcosystemType,
        matched_topic: str,
        tool_categories: list[str],
    ) -> "Repository":
        """從 GitHub API 回應建立 Repository 物件"""
        # 處理 license
        license_name = None
        if data.get("license") and isinstance(data["license"], dict):
            license_name = data["license"].get("name")

        return cls(
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            html_url=data["html_url"],
            homepage=data.get("homepage"),
            stargazers_count=data.get("stargazers_count", 0),
            forks_count=data.get("forks_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
            language=data.get("language"),
            topics=data.get("topics", []),
            license_name=license_name,
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            ecosystem=ecosystem,
            tool_categories=tool_categories,
            matched_topic=matched_topic,
            fetched_at=datetime.now(),
        )

    def __hash__(self) -> int:
        """使用 full_name 作為唯一識別"""
        return hash(self.full_name)

    def __eq__(self, other: object) -> bool:
        """比較兩個 Repository 是否相同"""
        if not isinstance(other, Repository):
            return False
        return self.full_name == other.full_name
