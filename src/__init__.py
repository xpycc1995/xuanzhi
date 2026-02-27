"""
规划选址论证报告AI智能体协作系统

基于AutoGen框架的多Agent协作系统,用于自动生成规划选址综合论证报告。
"""

from pathlib import Path
from dotenv import load_dotenv

# 自动加载项目根目录的 .env 文件
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

__version__ = "1.0.0"
__author__ = "AI开发团队"
