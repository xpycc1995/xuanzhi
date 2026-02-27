"""
Excel数据输入测试脚本

测试从Excel文件读取数据并生成报告的完整流程。
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.autogen_config import get_llm_config
from src.services.autogen_orchestrator import AutoGenOrchestrator
from src.services.excel_parser import ExcelParser
from src.utils.logger import setup_logger, logger


def get_template_path() -> str:
    """获取Excel模板路径"""
    template_path = os.path.join(
        project_root,
        "templates",
        "excel_templates",
        "项目数据模板.xlsx"
    )
    return template_path


def test_excel_parser():
    """测试Excel解析器"""
    logger.info("=" * 60)
    logger.info("测试1: Excel解析器")
    logger.info("=" * 60)

    template_path = get_template_path()
    logger.info(f"模板路径: {template_path}")

    if not os.path.exists(template_path):
        logger.error(f"模板文件不存在: {template_path}")
        logger.info("请先运行 scripts/create_excel_template.py 创建模板")
        return None

    try:
        parser = ExcelParser(template_path)

        # 测试解析项目基本信息
        logger.info("\n--- 解析项目基本信息 ---")
        project_data = parser.parse_project_overview()
        logger.info(f"项目名称: {project_data.项目名称}")
        logger.info(f"建设单位: {project_data.建设单位}")
        logger.info(f"项目投资: {project_data.项目投资}")

        # 测试解析选址数据
        logger.info("\n--- 解析选址分析数据 ---")
        site_data = parser.parse_site_selection()
        logger.info(f"备选方案数: {len(site_data.备选方案)}")
        for alt in site_data.备选方案:
            logger.info(f"  - {alt.方案名称}: {alt.位置}")

        logger.info(f"征求意见数: {len(site_data.征求意见情况)}")
        logger.info(f"推荐方案: {site_data.方案比选.推荐方案}")

        parser.close()
        logger.info("\n✓ Excel解析器测试通过")
        return project_data, site_data

    except Exception as e:
        logger.error(f"✗ Excel解析器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_generate_from_excel():
    """测试从Excel生成报告"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 从Excel生成报告")
    logger.info("=" * 60)

    template_path = get_template_path()

    if not os.path.exists(template_path):
        logger.error(f"模板文件不存在: {template_path}")
        return None

    try:
        # 初始化LLM配置
        logger.info("初始化LLM配置...")
        llm_config = get_llm_config()

        # 初始化编排器
        logger.info("初始化AutoGen编排器...")
        orchestrator = AutoGenOrchestrator(llm_config)

        # 从Excel生成章节
        logger.info("从Excel生成报告...")
        chapters = orchestrator.generate_from_excel(template_path)

        # 显示结果
        for chapter_num, content in chapters.items():
            logger.info(f"\n--- 第{chapter_num}章 ---")
            logger.info(f"字数: {len(content)}")
            # 显示前300字预览
            preview = content[:300] + "..." if len(content) > 300 else content
            logger.info(f"预览:\n{preview}")

        logger.info("\n✓ 从Excel生成报告测试通过")
        return chapters

    except Exception as e:
        logger.error(f"✗ 从Excel生成报告测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_full_report_generation():
    """测试完整报告生成（包括Word文档）"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 完整报告生成")
    logger.info("=" * 60)

    template_path = get_template_path()

    if not os.path.exists(template_path):
        logger.error(f"模板文件不存在: {template_path}")
        return None

    try:
        # 初始化
        llm_config = get_llm_config()
        orchestrator = AutoGenOrchestrator(llm_config)

        # 生成完整报告
        logger.info("生成完整Word报告...")
        report_path = orchestrator.generate_full_report(template_path)

        logger.info(f"\n✓ 报告生成成功!")
        logger.info(f"文件路径: {report_path}")
        return report_path

    except Exception as e:
        logger.error(f"✗ 完整报告生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主测试函数"""
    # 设置日志
    setup_logger()

    logger.info("=" * 60)
    logger.info("Excel数据输入功能测试")
    logger.info("=" * 60)

    # 测试模式选择
    test_mode = "all"  # 可选: "parser", "generate", "report", "all"

    if len(sys.argv) > 1:
        test_mode = sys.argv[1]

    logger.info(f"测试模式: {test_mode}")
    logger.info("")

    try:
        if test_mode in ("parser", "all"):
            result = test_excel_parser()
            if result is None:
                logger.error("解析器测试失败，停止后续测试")
                return

        if test_mode in ("generate", "all"):
            result = test_generate_from_excel()
            if result is None:
                logger.error("报告生成测试失败，停止后续测试")
                return

        if test_mode in ("report", "all"):
            result = test_full_report_generation()
            if result is None:
                logger.error("完整报告测试失败")
                return

        logger.info("\n" + "=" * 60)
        logger.info("所有测试完成!")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("\n用户中断测试")
    except Exception as e:
        logger.error(f"\n测试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()