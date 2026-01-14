"""資料管理層 - 使用 aiosqlite 進行異步資料庫操作"""

import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "data" / "articles.db"


async def init_db() -> None:
    """初始化資料庫，建立 articles 表"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                content_path TEXT,
                is_summarized INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def insert_article(
    url: str,
    title: str,
    source: str,
    content_path: Optional[str] = None
) -> bool:
    """
    插入新文章記錄

    Returns:
        bool: True 表示新增成功，False 表示文章已存在
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                """
                INSERT INTO articles (url, title, source, content_path, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (url, title, source, content_path, datetime.now().isoformat())
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            # URL 已存在
            return False


async def get_pending_summaries() -> list[dict]:
    """取得所有未摘要的文章"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT url, title, source, content_path FROM articles WHERE is_summarized = 0"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def mark_as_summarized(url: str) -> None:
    """將文章標記為已摘要"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE articles SET is_summarized = 1 WHERE url = ?",
            (url,)
        )
        await db.commit()


async def get_article_count() -> dict:
    """取得文章統計資訊"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM articles") as cursor:
            total = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM articles WHERE is_summarized = 1") as cursor:
            summarized = (await cursor.fetchone())[0]

        return {
            "total": total,
            "summarized": summarized,
            "pending": total - summarized
        }
