"""摘要端口預留 - AI 摘要功能模組"""

from pathlib import Path
from typing import Optional

from .database import get_pending_summaries, mark_as_summarized


class Summarizer:
    """AI 摘要處理器

    目前為預留端口，尚未串接實際的 LLM API。
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    async def summarize_article(self, content_path: str) -> Optional[str]:
        """
        對單篇文章進行摘要

        Args:
            content_path: Markdown 檔案路徑

        Returns:
            摘要文字，目前回傳 None（預留端口）
        """
        # TODO: 在此處接入 Claude/OpenAI API
        # 範例實作流程：
        # 1. 讀取 content_path 的 Markdown 內容
        # 2. 構建 prompt（包含摘要指令與文章內容）
        # 3. 呼叫 LLM API
        # 4. 解析回應並返回摘要

        return None

    async def generate_daily_digest(self) -> Optional[str]:
        """
        生成每日 AI 新聞摘要報告

        Returns:
            完整的每日摘要報告，目前回傳 None（預留端口）
        """
        # TODO: 在此處接入 Claude/OpenAI API
        # 範例實作流程：
        # 1. 從資料庫取得今日所有文章
        # 2. 構建綜合摘要 prompt
        # 3. 呼叫 LLM API 生成報告
        # 4. 儲存並返回報告

        return None


async def process_pending_summaries() -> int:
    """
    處理所有待摘要的文章

    掃描資料庫中 is_summarized=0 的資料，並準備進行摘要處理。

    Returns:
        int: 處理的文章數量
    """
    pending_articles = await get_pending_summaries()

    if not pending_articles:
        print("[Summarizer] 沒有待處理的文章")
        return 0

    print(f"[Summarizer] 發現 {len(pending_articles)} 篇待摘要文章")

    processed_count = 0

    for article in pending_articles:
        title = article["title"]
        url = article["url"]
        content_path = article["content_path"]

        # TODO: 在此處接入 Claude/OpenAI API
        # 目前僅印出準備處理的文章資訊
        print(f"準備處理摘要：{title}")
        print(f"  - 來源: {article['source']}")
        print(f"  - URL: {url}")
        print(f"  - 內容路徑: {content_path}")

        # 模擬摘要完成（實際串接 API 後取消註解下方程式碼）
        # summary = await summarizer.summarize_article(content_path)
        # if summary:
        #     await mark_as_summarized(url)
        #     processed_count += 1

        processed_count += 1

    print(f"\n[Summarizer] 共處理 {processed_count} 篇文章（摘要端口尚未串接）")
    return processed_count
