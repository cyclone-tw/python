"""Logger configuration using loguru"""

import sys
from loguru import logger

from src.config import LOG_LEVEL


def setup_logger() -> None:
    """設定 logger 格式與輸出"""
    # 移除預設的 handler
    logger.remove()

    # 新增自訂格式的 handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL,
        colorize=True,
    )

    # 可選：輸出到檔案
    # logger.add(
    #     "logs/tracker_{time:YYYY-MM-DD}.log",
    #     rotation="1 day",
    #     retention="7 days",
    #     level="DEBUG",
    # )


# 初始化時自動設定
setup_logger()

__all__ = ["logger", "setup_logger"]
