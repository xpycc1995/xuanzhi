"""
测试第4章选址合理性分析Agent - 简化版

测试内容：
1. 数据模型验证
2. Agent初始化
3. 用户消息构建
4. 子模型验证
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 直接导入模型文件
import importlib.util

def load_module(module_name, file_path):
    """动态加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_data_model():
    """测试数据模型"""
    print("=" * 60)
    print("测试1：数据模型验证")
    print("=" * 60)
    
    try:
        # 加载rationality_data模块
        rationality_data = load_module(
            "rationality_data",
            os.path.join(project_root, "src", "models", "rationality_data.py")
        )
        
        # 获取示例数据
        data = rationality_data.get_sample_data()
        
        print(f"✓ 数据模型创建成功")
        print(f"  项目名称：{data.项目基本信息['项目名称']}")
        print(f"  大气环境影响程度：{data.环境影响分析.大气环境影响.影响程度}")
        print(f"  是否压覆矿产资源：{data.矿产资源压覆.是否压覆矿产资源}")
        print(f"  地质灾害易发程度：{data.地质灾害分析.地质灾害易发程度}")
        print(f"  社会稳定风险等级：{data.社会稳定分析.合法性风险.风险等级}")
        print(f"  图表数量：{len(data.图表清单) if data.图表清单 else 0}")
        
        # 测试格式化输出
        formatted = data.get_formatted_data()
        print(f"\n✓ 格式化数据生成成功（{len(formatted)}字符）")
        
        # 测试JSON序列化
        json_str = data.model_dump_json()
        print(f"✓ JSON序列化成功（{len(json_str)}字符）")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据模型测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_initialization():
    """测试Agent初始化"""
    print("\n" + "=" * 60)
    print("测试2：Agent初始化")
    print("=" * 60)
    
    try:
        # 检查提示词模板是否存在
        template_path = os.path.join(
            project_root, "templates", "prompts", "rationality_analysis.md"
        )
        if not os.path.exists(template_path):
            print(f"✗ 提示词模板文件不存在: {template_path}")
            return False, None
        
        # 加载Agent模块
        rationality_agent = load_module(
            "rationality_analysis_agent",
            os.path.join(project_root, "src", "agents", "rationality_analysis_agent.py")
        )
        
        # 加载autogen_config
        autogen_config = load_module(
            "autogen_config",
            os.path.join(project_root, "src", "core", "autogen_config.py")
        )
        
        # 获取模型客户端
        model_client = autogen_config.get_model_client()
        
        # 初始化Agent
        agent = rationality_agent.RationalityAnalysisAgent(model_client)
        
        # 获取Agent信息
        info = agent.get_agent_info()
        print(f"\n✓ Agent初始化成功!")
        print(f"  Agent名称：{info['name']}")
        print(f"  模板路径：{info['template_path']}")
        print(f"  System Message长度：{info['system_message_length']}字符")
        
        return True, agent
        
    except FileNotFoundError as e:
        print(f"✗ 提示词模板文件不存在: {str(e)}")
        print("  提示: 请确保 templates/prompts/rationality_analysis.md 存在")
        return False, None
    except Exception as e:
        print(f"✗ Agent初始化测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_message_building(agent):
    """测试用户消息构建"""
    print("\n" + "=" * 60)
    print("测试3：用户消息构建")
    print("=" * 60)
    
    try:
        # 加载rationality_data模块
        rationality_data = load_module(
            "rationality_data",
            os.path.join(project_root, "src", "models", "rationality_data.py")
        )
        
        # 获取示例数据
        data = rationality_data.get_sample_data()
        
        # 构建用户消息
        user_message = agent._build_user_message(data)
        
        print(f"✓ 用户消息构建成功（{len(user_message)}字符）")
        
        # 显示前800字符
        print("\n用户消息预览：")
        print("-" * 40)
        print(user_message[:800])
        print("-" * 40)
        print("...")
        
        return True
        
    except Exception as e:
        print(f"✗ 用户消息构建测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sub_models():
    """测试子模型"""
    print("\n" + "=" * 60)
    print("测试4：子模型验证")
    print("=" * 60)
    
    try:
        # 加载rationality_data模块
        rationality_data = load_module(
            "rationality_data",
            os.path.join(project_root, "src", "models", "rationality_data.py")
        )
        
        # 测试大气环境影响模型
        atmospheric = rationality_data.AtmosphericImpact(
            施工期扬尘措施=["洒水降尘", "覆盖防尘布"],
            影响程度="影响较小",
            防治结论="大气环境影响可控"
        )
        print(f"✓ AtmosphericImpact模型创建成功")
        
        # 测试噪声环境影响模型
        noise = rationality_data.NoiseImpact(
            施工期噪声措施=["设专人维护设备", "白天施工"],
            影响程度="影响较小",
            防治结论="噪声影响可控"
        )
        print(f"✓ NoiseImpact模型创建成功")
        
        # 测试水环境影响模型
        water = rationality_data.WaterImpact(
            施工期废水措施=["集中收集处理"],
            运营期废水措施=["达标排放"],
            影响程度="影响较小",
            防治结论="水环境影响较小"
        )
        print(f"✓ WaterImpact模型创建成功")
        
        # 测试地质灾害分析模型
        geo = rationality_data.GeologicalHazardAnalysis(
            地质灾害类型=["滑坡"],
            地质灾害易发程度="低易发区",
            危险性等级="小",
            地震基本烈度="6度",
            防治措施=["边坡防护"],
            分析结论="地质灾害危险性小"
        )
        print(f"✓ GeologicalHazardAnalysis模型创建成功")
        
        # 测试社会稳定分析模型
        legality_risk = rationality_data.LegalityRiskAnalysis(
            风险内容="项目决策合法性风险",
            风险等级="低",
            防范措施=["严格审批程序"]
        )
        print(f"✓ LegalityRiskAnalysis模型创建成功")
        
        # 测试矿产资源压覆分析模型
        mineral = rationality_data.MineralResourceAnalysis(
            是否压覆矿产资源=False,
            是否与采矿权重叠=False,
            是否与探矿权重叠=False,
            是否与地质项目重叠=False,
            分析结论="不压覆矿产资源"
        )
        print(f"✓ MineralResourceAnalysis模型创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 子模型测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_module_import():
    """测试模块导入"""
    print("\n" + "=" * 60)
    print("测试5：模块导入验证")
    print("=" * 60)
    
    try:
        # 测试从src.models导入
        from src.models import (
            RationalityData,
            AtmosphericImpact,
            NoiseImpact,
            WaterImpact,
            SolidWasteImpact,
            TrafficImpact,
            EcologicalRestoration,
            EnvironmentalImpactAnalysis,
            MineralResourceAnalysis,
            GeologicalHazardAnalysis,
            LegalityRiskAnalysis,
            LivingEnvironmentRisk,
            SocialEnvironmentRisk,
            SocialStabilityAnalysis,
            EnergySavingAnalysis
        )
        print(f"✓ 从src.models导入成功")
        print(f"  RationalityData: {RationalityData.__name__}")
        print(f"  EnvironmentalImpactAnalysis: {EnvironmentalImpactAnalysis.__name__}")
        
        # 测试从src.agents导入
        from src.agents import RationalityAnalysisAgent
        print(f"✓ 从src.agents导入成功")
        print(f"  RationalityAnalysisAgent: {RationalityAnalysisAgent.__name__}")
        
        return True
        
    except ImportError as e:
        print(f"✗ 模块导入失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ 模块导入测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("第4章选址合理性分析Agent测试")
    print("=" * 60)
    
    results = []
    
    # 测试1：数据模型
    results.append(("数据模型验证", test_data_model()))
    
    # 测试2：Agent初始化
    success, agent = test_agent_initialization()
    results.append(("Agent初始化", success))
    
    # 测试3：用户消息构建
    if agent:
        results.append(("用户消息构建", test_message_building(agent)))
    else:
        results.append(("用户消息构建", False))
    
    # 测试4：子模型
    results.append(("子模型验证", test_sub_models()))
    
    # 测试5：模块导入
    results.append(("模块导入验证", test_module_import()))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}：{status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 所有测试通过！第4章Agent开发完成。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)