"""
日志配置模块

使用loguru库配置系统日志。
"""

import sys
import os
from pathlib import Path
from loguru import logger
import io

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    # 尝试设置 stdout 为 UTF-8
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        # Python < 3.7
        try:
            import codecs
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        except:
            pass  # 如果失败就使用默认编码


def setup_logger(log_dir: str = "output/logs", log_level: str = "INFO"):
    """
    配置日志系统

    Args:
        log_dir: 日志文件目录
        log_level: 日志级别
    """
    # 确保日志目录存在
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 移除默认的handler
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # 添加文件输出(所有日志)
    logger.add(
        f"{log_dir}/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",  # 日志文件大小达到10MB时轮转
        retention="30 days",  # 保留30天的日志
        compression="zip",  # 压缩旧日志
    )

    # 添加错误日志文件
    logger.add(
        f"{log_dir}/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="90 days",  # 错误日志保留90天
        compression="zip",
    )

    logger.info("日志系统初始化完成")


# 默认配置
if os.getenv("DEBUG") == "True":
    setup_logger(log_level="DEBUG")
else:
    setup_logger(log_level="INFO")
