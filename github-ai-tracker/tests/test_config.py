"""Tests for configuration module"""

from src.config import (
    TOPICS,
    TOOL_CATEGORY_MAPPING,
    get_tool_categories,
    ECOSYSTEM_DISPLAY_NAMES,
)


def test_topics_structure():
    """測試 TOPICS 結構是否正確"""
    assert isinstance(TOPICS, dict)
    assert len(TOPICS) >= 6  # 至少 6 個生態系

    # 確認每個生態系都有 topics
    for ecosystem, topics in TOPICS.items():
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert all(isinstance(t, str) for t in topics)


def test_ecosystem_display_names():
    """測試生態系顯示名稱是否都有對應"""
    for ecosystem in TOPICS.keys():
        assert ecosystem in ECOSYSTEM_DISPLAY_NAMES


def test_get_tool_categories_single():
    """測試單一 topic 的分類"""
    topics = ["cursor"]
    categories = get_tool_categories(topics)
    assert "Cursor" in categories


def test_get_tool_categories_multiple():
    """測試多個 topics 的分類"""
    topics = ["cursor-ai", "mcp", "vibe-coding"]
    categories = get_tool_categories(topics)
    assert "Cursor" in categories
    assert "MCP" in categories


def test_get_tool_categories_notebooklm():
    """測試 NotebookLM 相關的分類"""
    topics = ["notebooklm", "pdf-to-pptx"]
    categories = get_tool_categories(topics)
    assert "NotebookLM" in categories
    assert "PDF" in categories


def test_get_tool_categories_empty():
    """測試空 topics"""
    categories = get_tool_categories([])
    assert categories == []


def test_get_tool_categories_unknown():
    """測試未知的 topic"""
    topics = ["unknown-topic", "another-unknown"]
    categories = get_tool_categories(topics)
    assert categories == []


def test_tool_category_mapping_completeness():
    """確認 TOOL_CATEGORY_MAPPING 涵蓋主要 topics"""
    # 確認一些關鍵的 topics 都有對應的分類
    key_topics = [
        "cursor",
        "claude-code",
        "cline",
        "ollama",
        "notebooklm",
        "mcp",
        "langchain",
    ]
    for topic in key_topics:
        assert topic in TOOL_CATEGORY_MAPPING
