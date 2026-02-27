"""
测试第3章合法合规性分析Agent - 简化版

测试内容：
1. 数据模型验证
2. Agent初始化
3. 用户消息构建
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
        # 加载compliance_data模块
        compliance_data = load_module(
            "compliance_data",
            os.path.join(project_root, "src", "models", "compliance_data.py")
        )
        
        # 获取示例数据
        data = compliance_data.get_sample_data()
        
        print(f"✓ 数据模型创建成功")
        print(f"  项目名称：{data.项目基本信息['项目名称']}")
        print(f"  产业政策符合性：{data.产业政策符合性.符合性结论}")
        print(f"  是否占用耕地：{data.三线协调分析.是否占用耕地}")
        print(f"  是否占用生态红线：{data.三线协调分析.是否占用生态保护红线}")
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
            project_root, "templates", "prompts", "compliance_analysis.md"
        )
        if not os.path.exists(template_path):
            print(f"✗ 提示词模板文件不存在: {template_path}")
            return False, None
        
        # 加载Agent模块
        compliance_agent = load_module(
            "compliance_analysis_agent",
            os.path.join(project_root, "src", "agents", "compliance_analysis_agent.py")
        )
        
        # 创建临时LLM配置
        test_config = {
            "config_list": [{"model": "qwen-plus", "api_key": "test-key"}],
            "temperature": 0.7,
            "cache_seed": 42,
        }
        
        # 初始化Agent
        agent = compliance_agent.ComplianceAnalysisAgent(test_config)
        
        # 获取Agent信息
        info = agent.get_agent_info()
        print(f"\n✓ Agent初始化成功!")
        print(f"  Agent名称：{info['name']}")
        print(f"  LLM模型：{info['llm_model']}")
        print(f"  System Message长度：{info['system_message_length']}字符")
        
        return True, agent
        
    except FileNotFoundError as e:
        print(f"✗ 提示词模板文件不存在: {str(e)}")
        print("  提示: 请确保 templates/prompts/compliance_analysis.md 存在")
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
        # 加载compliance_data模块
        compliance_data = load_module(
            "compliance_data",
            os.path.join(project_root, "src", "models", "compliance_data.py")
        )
        
        # 获取示例数据
        data = compliance_data.get_sample_data()
        
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
        # 加载compliance_data模块
        compliance_data = load_module(
            "compliance_data",
            os.path.join(project_root, "src", "models", "compliance_data.py")
        )
        
        # 测试法规符合性模型
        reg = compliance_data.RegulationCompliance(
            法规名称="《产业结构调整指导目录（2024年本）》",
            发布单位="国家发展和改革委员会",
            发布时间="2024年",
            符合性分析="项目属于鼓励类项目",
            符合性结论="符合"
        )
        print(f"✓ RegulationCompliance模型创建成功")
        
        # 测试三线分析模型
        three_lines = compliance_data.ThreeLinesAnalysis(
            是否占用耕地=False,
            是否占用永久基本农田=False,
            是否占用生态保护红线=False,
            是否占用城镇开发边界=False,
            符合性说明="符合三线管控要求"
        )
        print(f"✓ ThreeLinesAnalysis模型创建成功")
        
        # 测试专项规划符合性模型
        special_plan = compliance_data.SpecialPlanCompliance(
            规划名称="综合交通规划",
            符合性分析="符合交通规划要求",
            符合性结论="符合"
        )
        print(f"✓ SpecialPlanCompliance模型创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 子模型测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("第3章合法合规性分析Agent测试")
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
        print("\n🎉 所有测试通过！第3章Agent开发完成。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)