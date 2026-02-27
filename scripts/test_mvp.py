"""
MVP测试脚本 - 测试项目概况Agent端到端流程

完整流程:
1. 准备测试项目数据
2. 初始化AutoGen编排器
3. 执行项目概况Agent生成第1章内容
4. 使用Word文档生成服务生成报告
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量（override=True 强制覆盖系统环境变量）
load_dotenv(override=True)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.autogen_config import get_model_client
from src.services.autogen_orchestrator import AutoGenOrchestrator
from src.services.document_service import DocumentService
from src.utils.logger import setup_logger, logger


def prepare_test_data() -> dict:
    """
    准备测试项目数据

    Returns:
        项目信息字典
    """
    logger.info("准备测试项目数据...")

    project_data = {
        "项目名称": "汉川市万福低闸等3座灌溉闸站更新改造工程项目",
        "项目代码": "2512-420984-04-01-395957",
        "建设单位": "汉川市水利和湖泊局",
        "建设性质": "更新改造",
        "项目投资": "7847.03万元",
        "项目选址": "龚家湾低闸泵站位于脉旺镇,万福低闸泵站、杜公泵站位于沉湖镇",
        "建设内容": "新建万福低闸泵站和龚家湾低闸泵站,改造杜公泵站。其中万福低闸灌溉泵站装机功率1350kW,设计流量10.0m³/s;龚家湾低闸灌溉泵站装机功率1800kW,设计流量12.0m³/s;杜公泵站装机功率560kW,设计流量3.0m³/s。",
        "建设规模": "总装机功率3710kW,总设计流量25.0m³/s",
        "建设期限": "24个月"
    }

    logger.info(f"✓ 测试数据准备完成 ({len(project_data)} 个字段)")
    return project_data


async def test_agent_generation_async(orchestrator: AutoGenOrchestrator, project_data: dict) -> str:
    """
    测试Agent内容生成 (异步版本)

    Args:
        orchestrator: AutoGen编排器
        project_data: 项目数据

    Returns:
        生成的第1章内容
    """
    logger.info("=" * 60)
    logger.info("开始测试:项目概况Agent内容生成")
    logger.info("=" * 60)

    try:
        # 获取 Agent
        agent = orchestrator.get_agent("project_overview")
        
        # 异步生成
        chapter_1_content = await agent.generate(project_data)

        # 显示生成结果
        logger.info("✓ 内容生成成功!")
        logger.info(f"  总字数: {len(chapter_1_content)}")
        paragraph_count = len(chapter_1_content.split('\n\n'))
        logger.info(f"  段落数: {paragraph_count}")

        # 显示前500字预览
        preview = chapter_1_content[:500] + "..." if len(chapter_1_content) > 500 else chapter_1_content
        logger.info(f"\n内容预览:\n{preview}")

        return chapter_1_content

    except Exception as e:
        logger.error(f"✗ 内容生成失败: {str(e)}")
        raise


def test_agent_generation(orchestrator: AutoGenOrchestrator, project_data: dict) -> str:
    """
    测试Agent内容生成

    Args:
        orchestrator: AutoGen编排器
        project_data: 项目数据

    Returns:
        生成的第1章内容
    """
    return asyncio.run(test_agent_generation_async(orchestrator, project_data))


def test_document_generation(project_data: dict, chapter_content: str) -> str:
    """
    测试Word文档生成

    Args:
        project_data: 项目数据
        chapter_content: 章节内容

    Returns:
        生成的Word文档路径
    """
    logger.info("=" * 60)
    logger.info("开始测试:Word文档生成")
    logger.info("=" * 60)

    try:
        # 创建文档服务
        doc_service = DocumentService()

        # 生成报告
        report_path = doc_service.generate_report(
            project_data=project_data,
            chapters={"1": chapter_content}
        )

        logger.info(f"✓ 报告生成成功: {report_path}")
        return report_path

    except Exception as e:
        logger.error(f"✗ 报告生成失败: {str(e)}")
        logger.info("提示:请确保标准模板文件存在于 templates/word_templates/标准模板.docx")
        raise


def main():
    """主测试函数"""
    # 设置日志
    setup_logger()

    logger.info("=" * 60)
    logger.info("MVP测试 - 项目概况Agent端到端验证")
    logger.info("=" * 60)

    try:
        # 1. 准备测试数据
        project_data = prepare_test_data()

        # 2. 初始化AutoGen编排器
        logger.info("\n初始化AutoGen编排器...")
        model_client = get_model_client()
        orchestrator = AutoGenOrchestrator(model_client=model_client)

        # 3. 测试Agent内容生成
        chapter_1_content = test_agent_generation(orchestrator, project_data)

        # 4. 测试文档生成
        report_path = test_document_generation(project_data, chapter_1_content)

        # 5. 测试总结
        logger.info("=" * 60)
        logger.info("MVP测试完成!")
        logger.info("=" * 60)
        logger.info("✓ 所有测试通过!")
        logger.info(f"✓ 生成的报告: {report_path}")
        logger.info("\n下一步:")
        logger.info("1. 打开生成的Word文档,检查内容质量")
        logger.info("2. 根据实际情况优化提示词模板")
        logger.info("3. 扩展实现其他Agent")

    except Exception as e:
        logger.error("=" * 60)
        logger.error("MVP测试失败!")
        logger.error("=" * 60)
        logger.error(f"错误信息: {str(e)}")
        logger.error("\n故障排查建议:")
        logger.error("1. 检查 API 密钥是否正确配置 (DASHSCOPE_API_KEY 或 OPENAI_API_KEY)")
        logger.error("2. 检查网络连接是否正常")
        logger.error("3. 检查模板文件是否存在")
        sys.exit(1)


if __name__ == "__main__":
    main()