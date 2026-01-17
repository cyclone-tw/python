"""Configuration management for GitHub AI Tracker"""

import os
from typing import Literal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ===== API Configuration =====
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

# ===== App Settings =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_REPOS_PER_TOPIC = int(os.getenv("MAX_REPOS_PER_TOPIC", "50"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
SEARCH_DELAY_SECONDS = float(os.getenv("SEARCH_DELAY_SECONDS", "2"))

# ===== GitHub API =====
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"

# ===== Ecosystem Type =====
EcosystemType = Literal[
    "vibe_coding_ide",
    "antigravity",
    "ai_coding_agents",
    "notebooklm",
    "ai_infrastructure",
    "pdf_tools",
]

# ===== Ecosystem Display Names =====
ECOSYSTEM_DISPLAY_NAMES = {
    "vibe_coding_ide": "Vibe Coding IDE",
    "antigravity": "Antigravity",
    "ai_coding_agents": "AI Coding Agents",
    "notebooklm": "NotebookLM",
    "ai_infrastructure": "AI Infrastructure",
    "pdf_tools": "PDF Tools",
}

# ===== Topics Configuration =====
TOPICS: dict[str, list[str]] = {
    # ===== Vibe Coding IDE =====
    "vibe_coding_ide": [
        "vibe-coding",
        "cursor",
        "cursor-ai",
        "cursor-rules",
        "windsurf",
        "windsurf-ai",
    ],
    # ===== Google Antigravity =====
    "antigravity": [
        "antigravity",
        "antigravity-ide",
        "antigravity-ai",
        "gemini-cli",
    ],
    # ===== AI Coding Agents =====
    "ai_coding_agents": [
        "ai-agent",
        "coding-assistant",
        "claude-code",
        "cline",
        "aider",
        "continue",
        "copilot",
    ],
    # ===== NotebookLM 生態系 =====
    "notebooklm": [
        "notebooklm",
        "pdf-to-pptx",
        "pdf-text-extraction",
        "ai-podcast",
        "open-notebooklm",
    ],
    # ===== AI 基礎設施 =====
    "ai_infrastructure": [
        "llm",
        "ollama",
        "local-llm",
        "rag",
        "ragflow",
        "mcp",
        "langchain",
        "langflow",
        "vllm",
    ],
    # ===== PDF 處理工具 =====
    "pdf_tools": [
        "pdf-extract",
        "pdf-parser",
        "ocr",
        "document-ai",
        "pdf-to-markdown",
    ],
}

# ===== Tool Category Mapping =====
# 用於根據 Topics 自動判斷工具分類（可多選）
TOOL_CATEGORY_MAPPING: dict[str, str] = {
    # Cursor 相關
    "cursor": "Cursor",
    "cursor-ai": "Cursor",
    "cursor-rules": "Cursor",
    # Antigravity 相關
    "antigravity": "Antigravity",
    "antigravity-ide": "Antigravity",
    "antigravity-ai": "Antigravity",
    "gemini-cli": "Antigravity",
    # Windsurf 相關
    "windsurf": "Windsurf",
    "windsurf-ai": "Windsurf",
    # Claude 相關
    "claude-code": "Claude",
    "claude": "Claude",
    "anthropic": "Claude",
    # 其他 AI Agents
    "cline": "Cline",
    "aider": "Aider",
    "copilot": "Copilot",
    "github-copilot": "Copilot",
    # NotebookLM 相關
    "notebooklm": "NotebookLM",
    "open-notebooklm": "NotebookLM",
    "ai-podcast": "Podcast",
    # AI 基礎設施
    "ollama": "Ollama",
    "local-llm": "Ollama",
    "vllm": "vLLM",
    "rag": "RAG",
    "ragflow": "RAG",
    "langchain": "LangChain",
    "langflow": "LangChain",
    "mcp": "MCP",
    "model-context-protocol": "MCP",
    # PDF 工具
    "pdf-extract": "PDF",
    "pdf-parser": "PDF",
    "pdf-to-pptx": "PDF",
    "pdf-text-extraction": "PDF",
    "ocr": "PDF",
    "document-ai": "PDF",
    "pdf-to-markdown": "PDF",
}


def get_tool_categories(topics: list[str]) -> list[str]:
    """根據 Topics 自動判斷工具分類（可能返回多個）"""
    categories = set()

    for topic in topics:
        topic_lower = topic.lower()
        if topic_lower in TOOL_CATEGORY_MAPPING:
            categories.add(TOOL_CATEGORY_MAPPING[topic_lower])

    return sorted(list(categories))


def validate_config() -> list[str]:
    """驗證必要的設定是否存在，返回缺少的設定列表"""
    missing = []

    if not GITHUB_TOKEN:
        missing.append("GITHUB_TOKEN")
    if not NOTION_TOKEN:
        missing.append("NOTION_TOKEN")
    if not NOTION_DATABASE_ID:
        missing.append("NOTION_DATABASE_ID")

    return missing
