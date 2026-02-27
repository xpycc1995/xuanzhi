"""
端到端测试脚本 - 从Excel输入到Word报告输出 (全部6章节)

完整流程:
1. 读取Excel模板数据
2. 调用6个Agent生成章节内容
3. 生成Word报告文档
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.autogen_config import get_model_client, get_model_info
from src.services.excel_parser import ExcelParser
from src.services.document_service import DocumentService
from src.agents import (
    ProjectOverviewAgent,
    SiteSelectionAgent,
    ComplianceAnalysisAgent,
    RationalityAnalysisAgent,
    LandUseAnalysisAgent,
    ConclusionAgent
)
from src.utils.logger import setup_logger, logger


# Excel模板路径
EXCEL_TEMPLATE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates", "excel_templates", "项目数据模板.xlsx"
)

# 输出目录
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output", "reports"
)


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_success(message: str):
    """打印成功信息"""
    print(f"  ✓ {message}")


def print_error(message: str):
    """打印错误信息"""
    print(f"  ✗ {message}")


def print_info(message: str):
    """打印信息"""
    print(f"  → {message}")


async def test_excel_parsing(excel_path: str):
    """测试Excel解析 - 解析全部6章数据"""
    print_header("步骤1: Excel数据解析 (6章节)")
    
    try:
        parser = ExcelParser(excel_path)
        
        # 使用 parse_all_with_chapter6 解析全部6章数据
        print_info("解析全部6章数据...")
        project_data, site_data, compliance_data, rationality_data, land_use_data, conclusion_data = parser.parse_all_with_chapter6()
        
        # 第1章数据
        print_info("第1章: 项目概况")
        print_success(f"项目名称: {project_data.项目名称}")
        print_success(f"建设单位: {project_data.建设单位}")
        print_success(f"项目投资: {project_data.项目投资}")
        
        # 第2章数据
        print_info("第2章: 选址可行性分析")
        print_success(f"备选方案数量: {len(site_data.备选方案)}")
        print_success(f"选址原则数量: {len(site_data.选址原则)}")
        print_success(f"征求意见数量: {len(site_data.征求意见情况)}")
        print_success(f"推荐方案: {site_data.方案比选.推荐方案}")
        
        # 第3章数据
        print_info("第3章: 合法合规性分析")
        print_success(f"是否占用耕地: {compliance_data.三线协调分析.是否占用耕地}")
        print_success(f"是否占用生态红线: {compliance_data.三线协调分析.是否占用生态保护红线}")
        print_success(f"是否占用城镇开发边界: {compliance_data.三线协调分析.是否占用城镇开发边界}")
        
        # 第4章数据
        print_info("第4章: 选址合理性分析")
        if rationality_data:
            print_success(f"是否压覆矿产资源: {rationality_data.矿产资源压覆.是否压覆矿产资源 if rationality_data.矿产资源压覆 else 'N/A'}")
            print_success(f"地质灾害易发程度: {rationality_data.地质灾害分析.地质灾害易发程度 if rationality_data.地质灾害分析 else 'N/A'}")
        else:
            print_error("第4章数据解析失败")
        
        # 第5章数据
        print_info("第5章: 节约集约用地分析")
        if land_use_data:
            print_success(f"功能分区数量: {len(land_use_data.功能分区情况) if land_use_data.功能分区情况 else 0}")
            if land_use_data.用地规模合理性 and land_use_data.用地规模合理性.总体指标:
                print_success(f"用地规模是否符合要求: {land_use_data.用地规模合理性.总体指标.是否符合要求}")
        else:
            print_error("第5章数据解析失败")
        
        # 第6章数据
        print_info("第6章: 结论与建议")
        if conclusion_data:
            print_success(f"建议数量: {len(conclusion_data.建议列表) if conclusion_data.建议列表 else 0}")
            if conclusion_data.综合论证结论:
                print_success(f"综合论证结论: {conclusion_data.综合论证结论[:50]}...")
        else:
            print_error("第6章数据解析失败")
        
        parser.close()
        print_success("Excel解析完成!")
        
        return project_data, site_data, compliance_data, rationality_data, land_use_data, conclusion_data
        
    except Exception as e:
        print_error(f"Excel解析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None, None, None, None


async def test_agent_generation(model_client, project_data, site_data, compliance_data, rationality_data, land_use_data, conclusion_data):
    """测试Agent内容生成 - 生成全部6章节"""
    print_header("步骤2: Agent内容生成 (6章节)")
    
    chapters = {}
    
    # 第1章: 项目概况
    print_info("生成第1章：项目概况...")
    try:
        agent1 = ProjectOverviewAgent(model_client)
        chapter1_content = await agent1.generate(project_data.to_dict())
        chapters["1"] = chapter1_content
        print_success(f"第1章生成成功，字数: {len(chapter1_content)}")
    except Exception as e:
        print_error(f"第1章生成失败: {str(e)}")
        chapters["1"] = f"[第1章生成失败: {str(e)}]"
    
    # 第2章: 选址可行性分析
    print_info("生成第2章：建设项目选址可行性分析...")
    try:
        agent2 = SiteSelectionAgent(model_client)
        context1 = chapters.get("1", "")[:500] if chapters.get("1") else None
        chapter2_content = await agent2.generate(site_data, context1)
        chapters["2"] = chapter2_content
        print_success(f"第2章生成成功，字数: {len(chapter2_content)}")
    except Exception as e:
        print_error(f"第2章生成失败: {str(e)}")
        chapters["2"] = f"[第2章生成失败: {str(e)}]"
    
    # 第3章: 合法合规性分析
    print_info("生成第3章：建设项目合法合规性分析...")
    try:
        agent3 = ComplianceAnalysisAgent(model_client)
        context2 = chapters.get("2", "")[:500] if chapters.get("2") else None
        chapter3_content = await agent3.generate(compliance_data, context2)
        chapters["3"] = chapter3_content
        print_success(f"第3章生成成功，字数: {len(chapter3_content)}")
    except Exception as e:
        print_error(f"第3章生成失败: {str(e)}")
        chapters["3"] = f"[第3章生成失败: {str(e)}]"
    
    # 第4章: 选址合理性分析
    print_info("生成第4章：建设项目选址合理性分析...")
    try:
        agent4 = RationalityAnalysisAgent(model_client)
        context3 = chapters.get("3", "")[:500] if chapters.get("3") else None
        chapter4_content = await agent4.generate(rationality_data, context3)
        chapters["4"] = chapter4_content
        print_success(f"第4章生成成功，字数: {len(chapter4_content)}")
    except Exception as e:
        print_error(f"第4章生成失败: {str(e)}")
        chapters["4"] = f"[第4章生成失败: {str(e)}]"
    
    # 第5章: 节约集约用地分析
    print_info("生成第5章：建设项目节约集约用地分析...")
    try:
        agent5 = LandUseAnalysisAgent(model_client)
        context4 = chapters.get("4", "")[:500] if chapters.get("4") else None
        chapter5_content = await agent5.generate(land_use_data, context4)
        chapters["5"] = chapter5_content
        print_success(f"第5章生成成功，字数: {len(chapter5_content)}")
    except Exception as e:
        print_error(f"第5章生成失败: {str(e)}")
        chapters["5"] = f"[第5章生成失败: {str(e)}]"
    
    # 第6章: 结论与建议
    print_info("生成第6章：结论与建议...")
    try:
        agent6 = ConclusionAgent(model_client)
        # 第6章需要前5章的上下文摘要
        context_all = "\n".join([
            f"第{i}章摘要: {chapters.get(str(i), '')[:300]}"
            for i in range(1, 6)
        ])
        chapter6_content = await agent6.generate(conclusion_data, context_all)
        chapters["6"] = chapter6_content
        print_success(f"第6章生成成功，字数: {len(chapter6_content)}")
    except Exception as e:
        print_error(f"第6章生成失败: {str(e)}")
        chapters["6"] = f"[第6章生成失败: {str(e)}]"
    
    return chapters


async def test_document_generation(project_data, chapters):
    """测试Word文档生成"""
    print_header("步骤3: Word文档生成")
    
    try:
        # 创建输出目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 生成报告
        doc_service = DocumentService()
        report_path = doc_service.generate_report(
            project_data=project_data.to_dict(),
            chapters=chapters,
            output_path=os.path.join(OUTPUT_DIR, f"{project_data.项目名称}_规划选址论证报告_完整版.docx")
        )
        
        print_success(f"Word报告生成成功!")
        print_success(f"报告路径: {report_path}")
        
        # 获取文件大小
        file_size = os.path.getsize(report_path)
        print_success(f"文件大小: {file_size / 1024:.2f} KB")
        
        return report_path
        
    except Exception as e:
        print_error(f"Word文档生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def run_end_to_end_test(excel_path: str = None):
    """运行端到端测试"""
    print("\n" + "=" * 60)
    print(" 端到端测试: Excel输入 → 6章节Agent生成 → Word输出")
    print(" Python环境: /Users/yc/miniconda/envs/xuanzhi")
    print("=" * 60)
    
    # 使用默认Excel模板
    if excel_path is None:
        excel_path = EXCEL_TEMPLATE
    
    print_info(f"Excel模板: {excel_path}")
    
    # 检查文件是否存在
    if not os.path.exists(excel_path):
        print_error(f"Excel文件不存在: {excel_path}")
        return False
    
    # 打印配置信息
    print_header("LLM配置信息")
    model_info = get_model_info()
    print_info(f"提供商: {model_info['provider']}")
    print_info(f"模型: {model_info['model']}")
    print_info(f"Base URL: {model_info['base_url']}")
    
    # 步骤1: Excel解析
    result = await test_excel_parsing(excel_path)
    project_data, site_data, compliance_data, rationality_data, land_use_data, conclusion_data = result
    if project_data is None:
        return False
    
    # 步骤2: Agent生成 (全部6章)
    model_client = get_model_client()
    chapters = await test_agent_generation(
        model_client, project_data, site_data, compliance_data, 
        rationality_data, land_use_data, conclusion_data
    )
    
    # 步骤3: Word生成
    report_path = await test_document_generation(project_data, chapters)
    
    # 结果汇总
    print_header("测试结果汇总")
    
    print(f"  Excel解析: {'✓ 成功' if project_data else '✗ 失败'}")
    
    chapter_names = {
        "1": "项目概况",
        "2": "选址可行性分析",
        "3": "合法合规性分析",
        "4": "选址合理性分析",
        "5": "节约集约用地分析",
        "6": "结论与建议"
    }
    
    for chapter_num, chapter_name in chapter_names.items():
        content = chapters.get(chapter_num, "")
        status = "✓ 成功" if len(content) > 100 else "✗ 失败"
        print(f"  第{chapter_num}章({chapter_name}): {status} ({len(content)} 字符)")
    
    print(f"  Word报告: {'✓ 成功' if report_path else '✗ 失败'}")
    
    # 统计总字数
    total_chars = sum(len(chapters.get(str(i), "")) for i in range(1, 7))
    print(f"\n  总字数: {total_chars} 字符")
    
    if report_path and all(len(chapters.get(str(i), "")) > 100 for i in range(1, 7)):
        print("\n" + "=" * 60)
        print("  🎉 端到端测试全部通过！")
        print(f"  📄 报告已保存: {report_path}")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("  ⚠️ 部分测试失败，请检查错误信息。")
        print("=" * 60)
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="端到端测试: Excel输入 → 6章节Agent生成 → Word输出")
    parser.add_argument("--excel", type=str, default=None, help="Excel模板路径 (默认: templates/excel_templates/项目数据模板.xlsx)")
    args = parser.parse_args()
    
    # 设置日志
    setup_logger()
    
    # 运行测试
    success = asyncio.run(run_end_to_end_test(args.excel))
    sys.exit(0 if success else 1)