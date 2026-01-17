"""Tests for data models"""

from datetime import datetime
import pytest

from src.models.repository import Repository


def test_repository_from_github_response():
    """測試從 GitHub API 回應建立 Repository"""
    mock_response = {
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "description": "A test repository",
        "html_url": "https://github.com/owner/test-repo",
        "homepage": "https://example.com",
        "stargazers_count": 1000,
        "forks_count": 100,
        "open_issues_count": 10,
        "language": "Python",
        "topics": ["cursor", "ai", "mcp"],
        "license": {"name": "MIT License"},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2025-01-15T00:00:00Z",
    }

    repo = Repository.from_github_response(
        data=mock_response,
        ecosystem="ai_coding_agents",
        matched_topic="cursor",
        tool_categories=["Cursor", "MCP"],
    )

    assert repo.name == "test-repo"
    assert repo.full_name == "owner/test-repo"
    assert repo.description == "A test repository"
    assert str(repo.html_url) == "https://github.com/owner/test-repo"
    assert repo.homepage == "https://example.com"
    assert repo.stargazers_count == 1000
    assert repo.forks_count == 100
    assert repo.language == "Python"
    assert "cursor" in repo.topics
    assert repo.license_name == "MIT License"
    assert repo.ecosystem == "ai_coding_agents"
    assert "Cursor" in repo.tool_categories
    assert "MCP" in repo.tool_categories


def test_repository_from_github_response_minimal():
    """測試最小資料的 GitHub API 回應"""
    mock_response = {
        "name": "minimal-repo",
        "full_name": "owner/minimal-repo",
        "html_url": "https://github.com/owner/minimal-repo",
        "stargazers_count": 0,
        "forks_count": 0,
        "open_issues_count": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }

    repo = Repository.from_github_response(
        data=mock_response,
        ecosystem="notebooklm",
        matched_topic="notebooklm",
        tool_categories=[],
    )

    assert repo.name == "minimal-repo"
    assert repo.description is None
    assert repo.homepage is None
    assert repo.language is None
    assert repo.license_name is None
    assert repo.topics == []


def test_repository_empty_homepage():
    """測試空字串 homepage 會轉為 None"""
    mock_response = {
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "html_url": "https://github.com/owner/test-repo",
        "homepage": "",  # 空字串
        "stargazers_count": 0,
        "forks_count": 0,
        "open_issues_count": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }

    repo = Repository.from_github_response(
        data=mock_response,
        ecosystem="notebooklm",
        matched_topic="notebooklm",
        tool_categories=[],
    )

    assert repo.homepage is None


def test_repository_equality():
    """測試 Repository 相等性比較"""
    repo1 = Repository(
        name="test",
        full_name="owner/test",
        html_url="https://github.com/owner/test",
        stargazers_count=100,
        forks_count=10,
        open_issues_count=5,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        ecosystem="notebooklm",
        matched_topic="test",
        fetched_at=datetime.now(),
    )

    repo2 = Repository(
        name="test",
        full_name="owner/test",  # 同樣的 full_name
        html_url="https://github.com/owner/test",
        stargazers_count=200,  # 不同的星星數
        forks_count=20,
        open_issues_count=10,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        ecosystem="ai_infrastructure",  # 不同的 ecosystem
        matched_topic="test",
        fetched_at=datetime.now(),
    )

    # full_name 相同則視為相同
    assert repo1 == repo2
    assert hash(repo1) == hash(repo2)


def test_repository_inequality():
    """測試 Repository 不相等"""
    repo1 = Repository(
        name="test1",
        full_name="owner/test1",
        html_url="https://github.com/owner/test1",
        stargazers_count=100,
        forks_count=10,
        open_issues_count=5,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        ecosystem="notebooklm",
        matched_topic="test",
        fetched_at=datetime.now(),
    )

    repo2 = Repository(
        name="test2",
        full_name="owner/test2",  # 不同的 full_name
        html_url="https://github.com/owner/test2",
        stargazers_count=100,
        forks_count=10,
        open_issues_count=5,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        ecosystem="notebooklm",
        matched_topic="test",
        fetched_at=datetime.now(),
    )

    assert repo1 != repo2
