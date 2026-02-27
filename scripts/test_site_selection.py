"""
选址分析Agent集成测试脚本

完整流程:
1. 准备测试数据
2. 初始化AutoGen编排器
3. 执行选址分析Agent生成第2章内容
4. 使用Word文档生成服务生成报告
5. 验证生成质量
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

# Windows编码问题修复
if sys.platform == 'win32':
    sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.core.autogen_config import get_model_client
from src.services.autogen_orchestrator import AutoGenOrchestrator
from src.services.document_service import DocumentService
from src.models.site_selection_data import get_sample_data
from src.utils.logger import setup_logger, logger


def prepare_test_data():
    """
    准备测试数据

    Returns:
        SiteSelectionData: 选址分析测试数据
    """
    logger.info("准备选址分析测试数据...")
    data = get_sample_data()

    logger.info(f"✓ 测试数据准备完成")
    logger.info(f"  项目名称：{data.项目基本信息.get('项目名称', '未知')}")
    logger.info(f"  备选方案数量：{len(data.备选方案)}")
    logger.info(f"  征求意见数量：{len(data.征求意见情况)}")

    return data


async def test_agent_generation_async(orchestrator: AutoGenOrchestrator, site_data) -> str:
    """
    测试Agent内容生成 (异步版本)

    Args:
        orchestrator: AutoGen编排器
        site_data: 选址分析数据

    Returns:
        生成的第2章内容
    """
    logger.info("=" * 60)
    logger.info("开始测试: 选址分析Agent内容生成")
    logger.info("=" * 60)

    try:
        # 获取 Agent
        agent = orchestrator.get_agent("site_selection")
        
        # 异步生成
        chapter_2_content = await agent.generate(site_data)

        # 显示生成结果
        logger.info("✓ 内容生成成功!")
        logger.info(f"  总字数: {len(chapter_2_content)}")

        # 计算段落数
        paragraph_count = len([p for p in chapter_2_content.split('\n\n') if p.strip()])
        logger.info(f"  段落数: {paragraph_count}")

        # 检查章节结构
        sections = [
            "2.1 建设项目选址原则",
            "2.2 项目备选方案情况",
            "2.3 场地自然条件",
            "2.4 项目外部配套条件",
            "2.5 选址敏感条件",
            "2.6 施工运营条件",
            "2.7 规划影响条件",
            "2.8 项目选址征求意见情况",
            "2.9 方案比选"
        ]

        found_sections = []
        for section in sections:
            if section in chapter_2_content:
                found_sections.append(section)

        logger.info(f"  包含章节数: {len(found_sections)}/{len(sections)}")
        if len(found_sections) < len(sections):
            missing = set(sections) - set(found_sections)
            logger.warning(f"  缺失章节: {missing}")

        # 显示内容预览
        preview = chapter_2_content[:800] + "..." if len(chapter_2_content) > 800 else chapter_2_content
        logger.info(f"\n内容预览:\n{preview}")

        return chapter_2_content

    except Exception as e:
        logger.error(f"✗ 内容生成失败: {str(e)}")
        raise


def test_agent_generation(orchestrator: AutoGenOrchestrator, site_data) -> str:
    """
    测试Agent内容生成

    Args:
        orchestrator: AutoGen编排器
        site_data: 选址分析数据

    Returns:
        生成的第2章内容
    """
    return asyncio.run(test_agent_generation_async(orchestrator, site_data))


def test_document_generation(site_data, chapter_content: str) -> str:
    """
    测试Word文档生成

    Args:
        site_data: 选址分析数据
        chapter_content: 章节内容

    Returns:
        生成的Word文档路径
    """
    logger.info("=" * 60)
    logger.info("开始测试: Word文档生成")
    logger.info("=" * 60)

    try:
        # 创建文档服务
        doc_service = DocumentService()

        # 生成第2章报告
        report_path = doc_service.generate_chapter_2(
            content=chapter_content,
            site_data=site_data
        )

        logger.info(f"✓ 报告生成成功: {report_path}")
        return report_path

    except Exception as e:
        logger.error(f"✗ 报告生成失败: {str(e)}")
        logger.info("提示: 请确保标准模板文件存在于 templates/word_templates/标准模板.docx")
        raise


def evaluate_quality(content: str) -> dict:
    """
    评估生成内容质量

    Args:
        content: 生成的内容

    Returns:
        质量评估结果
    """
    logger.info("=" * 60)
    logger.info("质量评估")
    logger.info("=" * 60)

    results = {
        "总字数": len(content),
        "章节数": 0,
        "表格数": content.count("表2-"),
        "图表数": content.count("图2-"),
        "质量评分": 0,
        "问题": []
    }

    # 检查章节完整性
    required_sections = [
        "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9"
    ]

    found_count = 0
    for section in required_sections:
        if section in content:
            found_count += 1

    results["章节数"] = found_count

    # 评估质量
    issues = []

    # 字数检查
    if results["总字数"] < 8000:
        issues.append(f"字数不足: {results['总字数']} < 8000")
    elif results["总字数"] > 12000:
        issues.append(f"字数过多: {results['总字数']} > 12000")

    # 章节完整性检查
    if found_count < 9:
        issues.append(f"章节不完整: 仅找到 {found_count}/9 个章节")

    # 表格检查
    if results["表格数"] < 3:
        issues.append(f"表格数量不足: {results['表格数']} < 3")

    results["问题"] = issues

    # 计算质量评分
    score = 100
    if issues:
        score -= len(issues) * 15
    results["质量评分"] = max(0, score)

    # 输出结果
    logger.info(f"总字数: {results['总字数']}")
    logger.info(f"章节数: {results['章节数']}/9")
    logger.info(f"表格标记数: {results['表格数']}")
    logger.info(f"图表标记数: {results['图表数']}")
    logger.info(f"质量评分: {results['质量评分']}/100")

    if issues:
        logger.warning(f"发现问题:")
        for issue in issues:
            logger.warning(f"  - {issue}")

    return results


def main():
    """主测试函数"""
    # 设置日志
    setup_logger()

    logger.info("=" * 60)
    logger.info("选址分析Agent集成测试")
    logger.info("=" * 60)

    try:
        # 1. 准备测试数据
        site_data = prepare_test_data()

        # 2. 初始化AutoGen编排器
        logger.info("\n初始化AutoGen编排器...")
        model_client = get_model_client()
        orchestrator = AutoGenOrchestrator(model_client=model_client)

        # 3. 测试Agent内容生成
        chapter_2_content = test_agent_generation(orchestrator, site_data)

        # 4. 测试文档生成
        report_path = test_document_generation(site_data, chapter_2_content)

        # 5. 质量评估
        quality = evaluate_quality(chapter_2_content)

        # 6. 测试总结
        logger.info("=" * 60)
        logger.info("集成测试完成!")
        logger.info("=" * 60)
        logger.info(f"✓ 所有测试通过!")
        logger.info(f"✓ 生成的报告: {report_path}")
        logger.info(f"✓ 质量评分: {quality['质量评分']}/100")

        logger.info("\n下一步:")
        logger.info("1. 打开生成的Word文档,检查内容质量")
        logger.info("2. 检查表格格式和数据正确性")
        logger.info("3. 根据实际情况优化提示词模板")

        return quality

    except Exception as e:
        logger.error("=" * 60)
        logger.error("集成测试失败!")
        logger.error("=" * 60)
        logger.error(f"错误信息: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()