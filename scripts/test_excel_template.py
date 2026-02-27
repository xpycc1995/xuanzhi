#!/usr/bin/env python3
#MY|"""
#XB|Excel 模板测试脚本 - 测试使用 Excel 模板生成报告
#HW|
#WR|完整流程:
#BQ|1. 初始化 AutoGen 编排器
#ZX|2. 从 Excel 模板读取项目数据
#BK|3. 依次调用项目概况、选址分析、合法合规性分析 Agent 生成内容
#SW|4. 使用 Word 文档生成服务生成报告
#KV|"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量 (override=True 强制覆盖系统环境变量)
load_dotenv(override=True)

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.autogen_config import get_llm_config
from src.services.autogen_orchestrator import AutoGenOrchestrator
from src.utils.logger import setup_logger, logger


def test_excel_template_generation():
    """
    测试从 Excel 模板生成报告
    """
    logger.info("=" * 60)
    logger.info("Excel 模板报告生成测试")
    logger.info("=" * 60)
    
    # Excel 模板路径
    excel_path = os.path.join(project_root, "templates/excel_templates/项目数据模板.xlsx")
    
    logger.info(f"Excel 模板路径：{excel_path}")
    
    # 检查文件是否存在
    if not os.path.exists(excel_path):
        logger.error(f"✗ Excel 模板文件不存在：{excel_path}")
        logger.info("提示：请确保模板文件存在于 templates/excel_templates/项目数据模板.xlsx")
        return False
    
    logger.info("✓ Excel 模板文件存在")
    
    try:
        # 1. 初始化 AutoGen 编排器
        logger.info("\n初始化 AutoGen 编排器...")
        llm_config = get_llm_config()
        orchestrator = AutoGenOrchestrator(llm_config)
        logger.info("✓ AutoGen 编排器初始化完成")
        
        # 2. 生成完整报告
        logger.info("\n开始生成报告...")
        report_path = orchestrator.generate_full_report(excel_path)
        
        logger.info("=" * 60)
        logger.info("✓ 报告生成成功!")
        logger.info("=" * 60)
        logger.info(f"报告路径：{report_path}")
        logger.info("\n下一步:")
        logger.info("1. 打开生成的 Word 文档，检查内容质量")
        logger.info("2. 查看日志了解详细生成过程")
        logger.info("3. 根据实际情况优化提示词模板")
        
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("报告生成失败!")
        logger.error("=" * 60)
        logger.error(f"错误信息：{str(e)}")
        logger.info("\n故障排查建议:")
        logger.info("1. 检查 API 密钥是否正确配置")
        logger.info("2. 检查网络连接是否正常")
        logger.info("3. 检查 Excel 模板格式是否正确")
        logger.info("4. 查看日志文件了解详细错误")
        return False


if __name__ == "__main__":
    # 设置日志
    setup_logger()
    
    # 执行测试
    success = test_excel_template_generation()
    
    # 退出状态
    sys.exit(0 if success else 1)
