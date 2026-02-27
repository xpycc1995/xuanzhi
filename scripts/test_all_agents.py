"""
Agent测试脚本 - 验证所有Agent在新版autogen-agentchat环境下正常运行

测试内容:
1. ProjectOverviewAgent (第1章)
2. SiteSelectionAgent (第2章)
3. ComplianceAnalysisAgent (第3章)
4. RationalityAnalysisAgent (第4章)
5. LandUseAnalysisAgent (第5章)
6. ConclusionAgent (第6章)
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
from src.agents import (
    ProjectOverviewAgent,
    SiteSelectionAgent,
    ComplianceAnalysisAgent,
    RationalityAnalysisAgent,
    LandUseAnalysisAgent,
    ConclusionAgent
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


def test_config():
    """测试配置加载"""
    print_header("测试1: LLM配置加载")
    
    try:
        model_info = get_model_info()
        print_success(f"提供商: {model_info['provider']}")
        print_success(f"模型: {model_info['model']}")
        print_success(f"Base URL: {model_info['base_url']}")
        
        # 测试创建客户端
        model_client = get_model_client()
        print_success(f"模型客户端创建成功: {type(model_client).__name__}")
        
        return True, model_client
    except Exception as e:
        print_error(f"配置加载失败: {str(e)}")
        return False, None


async def test_project_overview_agent(model_client):
    """测试项目概况Agent"""
    print_header("测试2: ProjectOverviewAgent (第1章)")
    
    try:
        # 1. 初始化Agent
        agent = ProjectOverviewAgent(model_client)
        info = agent.get_agent_info()
        print_success(f"Agent名称: {info['name']}")
        print_success(f"模板路径: {info['template_path']}")
        print_success(f"System Message长度: {info['system_message_length']} 字符")
        
        # 2. 准备测试数据
        project_data = {
            "项目名称": "汉川市万福低闸等3座灌溉闸站更新改造工程项目",
            "项目代码": "2512-420984-04-01-395957",
            "建设单位": "汉川市水利和湖泊局",
            "建设性质": "更新改造",
            "项目投资": "7847.03万元",
            "项目选址": "龚家湾低闸泵站位于脉旺镇,万福低闸泵站、杜公泵站位于沉湖镇",
            "建设内容": "新建万福低闸泵站和龚家湾低闸泵站,改造杜公泵站。",
        }
        
        # 3. 构建用户消息测试
        user_message = agent._build_user_message(project_data)
        print_success(f"用户消息构建成功: {len(user_message)} 字符")
        
        # 4. 测试内容生成 (实际调用LLM)
        print("\n  正在调用LLM生成内容...")
        content = await agent.generate(project_data)
        print_success(f"内容生成成功: {len(content)} 字符")
        
        # 显示预览
        preview = content[:300] + "..." if len(content) > 300 else content
        print(f"\n  内容预览:\n  {preview[:200]}...")
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_site_selection_agent(model_client):
    """测试选址分析Agent"""
    print_header("测试3: SiteSelectionAgent (第2章)")
    
    try:
        # 1. 初始化Agent
        agent = SiteSelectionAgent(model_client)
        info = agent.get_agent_info()
        print_success(f"Agent名称: {info['name']}")
        print_success(f"模板路径: {info['template_path']}")
        print_success(f"System Message长度: {info['system_message_length']} 字符")
        
        # 2. 加载示例数据
        from src.models.site_selection_data import get_sample_data
        sample_data = get_sample_data()
        print_success(f"示例数据加载成功")
        print_success(f"备选方案数量: {len(sample_data.备选方案)}")
        print_success(f"选址原则数量: {len(sample_data.选址原则)}")
        
        # 3. 构建用户消息测试
        user_message = agent._build_user_message(sample_data)
        print_success(f"用户消息构建成功: {len(user_message)} 字符")
        
        # 4. 测试数据验证
        agent._validate_data(sample_data)
        print_success("数据验证通过")
        
        # 5. 测试内容生成 (实际调用LLM)
        print("\n  正在调用LLM生成内容...")
        content = await agent.generate(sample_data)
        print_success(f"内容生成成功: {len(content)} 字符")
        
        # 显示预览
        preview = content[:300] + "..." if len(content) > 300 else content
        print(f"\n  内容预览:\n  {preview[:200]}...")
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_compliance_agent(model_client):
    """测试合法合规性分析Agent"""
    print_header("测试4: ComplianceAnalysisAgent (第3章)")
    
    try:
        # 1. 初始化Agent
        agent = ComplianceAnalysisAgent(model_client)
        info = agent.get_agent_info()
        print_success(f"Agent名称: {info['name']}")
        print_success(f"模板路径: {info['template_path']}")
        print_success(f"System Message长度: {info['system_message_length']} 字符")
        
        # 2. 加载示例数据
        from src.models.compliance_data import get_sample_data
        sample_data = get_sample_data()
        print_success(f"示例数据加载成功")
        print_success(f"项目名称: {sample_data.项目基本信息.get('项目名称', '未知')}")
        
        # 3. 构建用户消息测试
        user_message = agent._build_user_message(sample_data)
        print_success(f"用户消息构建成功: {len(user_message)} 字符")
        
        # 4. 测试数据验证
        agent._validate_data(sample_data)
        print_success("数据验证通过")
        
        # 5. 测试内容生成 (实际调用LLM)
        print("\n  正在调用LLM生成内容...")
        content = await agent.generate(sample_data)
        print_success(f"内容生成成功: {len(content)} 字符")
        
        # 显示预览
        preview = content[:300] + "..." if len(content) > 300 else content
        print(f"\n  内容预览:\n  {preview[:200]}...")
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_rationality_agent(model_client):
    """测试选址合理性分析Agent"""
    print_header("测试5: RationalityAnalysisAgent (第4章)")
    
    try:
        # 1. 初始化Agent
        agent = RationalityAnalysisAgent(model_client)
        info = agent.get_agent_info()
        print_success(f"Agent名称: {info['name']}")
        print_success(f"模板路径: {info['template_path']}")
        print_success(f"System Message长度: {info['system_message_length']} 字符")
        
        # 2. 加载示例数据
        from src.models.rationality_data import get_sample_data
        sample_data = get_sample_data()
        print_success(f"示例数据加载成功")
        print_success(f"项目名称: {sample_data.项目基本信息.get('项目名称', '未知')}")
        
        # 3. 构建用户消息测试
        user_message = agent._build_user_message(sample_data)
        print_success(f"用户消息构建成功: {len(user_message)} 字符")
        
        # 4. 测试内容生成 (实际调用LLM)
        print("\n  正在调用LLM生成内容...")
        content = await agent.generate(sample_data)
        print_success(f"内容生成成功: {len(content)} 字符")
        
        # 显示预览
        preview = content[:300] + "..." if len(content) > 300 else content
        print(f"\n  内容预览:\n  {preview[:200]}...")
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_land_use_agent(model_client):
    """测试节约集约用地分析Agent"""
    print_header("测试6: LandUseAnalysisAgent (第5章)")
    
    try:
        # 1. 初始化Agent
        agent = LandUseAnalysisAgent(model_client)
        info = agent.get_agent_info()
        print_success(f"Agent名称: {info['name']}")
        print_success(f"模板路径: {info['template_path']}")
        print_success(f"System Message长度: {info['system_message_length']} 字符")
        
        # 2. 加载示例数据
        from src.models.land_use_data import get_sample_data
        sample_data = get_sample_data()
        print_success(f"示例数据加载成功")
        print_success(f"项目名称: {sample_data.项目基本信息.get('项目名称', '未知')}")
        
        # 3. 构建用户消息测试
        user_message = agent._build_user_message(sample_data)
        print_success(f"用户消息构建成功: {len(user_message)} 字符")
        
        # 4. 测试内容生成 (实际调用LLM)
        print("\n  正在调用LLM生成内容...")
        content = await agent.generate(sample_data)
        print_success(f"内容生成成功: {len(content)} 字符")
        
        # 显示预览
        preview = content[:300] + "..." if len(content) > 300 else content
        print(f"\n  内容预览:\n  {preview[:200]}...")
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_conclusion_agent(model_client):
    """测试结论与建议Agent"""
    print_header("测试7: ConclusionAgent (第6章)")
    
    try:
        # 1. 初始化Agent
        agent = ConclusionAgent(model_client)
        info = agent.get_agent_info()
        print_success(f"Agent名称: {info['name']}")
        print_success(f"模板路径: {info['template_path']}")
        print_success(f"System Message长度: {info['system_message_length']} 字符")
        
        # 2. 加载示例数据
        from src.models.conclusion_data import get_sample_data
        sample_data = get_sample_data()
        print_success(f"示例数据加载成功")
        print_success(f"项目名称: {sample_data.项目基本信息.get('项目名称', '未知')}")
        print_success(f"建议数量: {len(sample_data.建议列表)}")
        
        # 3. 构建用户消息测试
        user_message = agent._build_user_message(sample_data)
        print_success(f"用户消息构建成功: {len(user_message)} 字符")
        
        # 4. 测试内容生成 (实际调用LLM)
        print("\n  正在调用LLM生成内容...")
        content = await agent.generate(sample_data)
        print_success(f"内容生成成功: {len(content)} 字符")
        
        # 显示预览
        preview = content[:300] + "..." if len(content) > 300 else content
        print(f"\n  内容预览:\n  {preview[:200]}...")
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print(" AutoGen新版API环境 - 全部Agent测试")
    print(" Python环境: /Users/yc/miniconda/envs/xuanzhi")
    print("=" * 60)
    
    results = []
    
    # 测试1: 配置加载
    success, model_client = test_config()
    results.append(("LLM配置加载", success))
    
    if not success:
        print("\n配置加载失败，无法继续测试")
        return False
    
    # 测试2: 项目概况Agent
    success = await test_project_overview_agent(model_client)
    results.append(("ProjectOverviewAgent", success))
    
    # 测试3: 选址分析Agent
    success = await test_site_selection_agent(model_client)
    results.append(("SiteSelectionAgent", success))
    
    # 测试4: 合法合规性分析Agent
    success = await test_compliance_agent(model_client)
    results.append(("ComplianceAnalysisAgent", success))
    
    # 测试5: 选址合理性分析Agent
    success = await test_rationality_agent(model_client)
    results.append(("RationalityAnalysisAgent", success))
    
    # 测试6: 节约集约用地分析Agent
    success = await test_land_use_agent(model_client)
    results.append(("LandUseAnalysisAgent", success))
    
    # 测试7: 结论与建议Agent
    success = await test_conclusion_agent(model_client)
    results.append(("ConclusionAgent", success))
    
    # 输出测试结果汇总
    print_header("测试结果汇总")
    
    all_passed = True
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  🎉 所有测试通过！全部Agent运行正常。")
    else:
        print("  ⚠️ 部分测试失败，请检查错误信息。")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)