"""
测试第6章结论与建议Agent - 简化版

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
        # 加载conclusion_data模块
        conclusion_data = load_module(
            "conclusion_data",
            os.path.join(project_root, "src", "models", "conclusion_data.py")
        )
        
        # 获取示例数据
        data = conclusion_data.get_sample_data()
        
        print(f"✓ 数据模型创建成功")
        print(f"  项目名称：{data.项目基本信息['项目名称']}")
        print(f"  法律法规结论：{data.合法合规性结论.法律法规结论}")
        print(f"  环境影响结论：{data.选址合理性结论.环境影响结论}")
        print(f"  功能分区结论：{data.节约集约用地结论.功能分区结论}")
        print(f"  建议数量：{len(data.建议列表)}")
        
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
            project_root, "templates", "prompts", "conclusion.md"
        )
        if not os.path.exists(template_path):
            print(f"⚠ 提示词模板文件不存在: {template_path}")
            print("  将跳过Agent初始化测试")
            return False, None
        
        # 加载Agent模块
        conclusion_agent = load_module(
            "conclusion_agent",
            os.path.join(project_root, "src", "agents", "conclusion_agent.py")
        )
        
        # 加载autogen_config
        autogen_config = load_module(
            "autogen_config",
            os.path.join(project_root, "src", "core", "autogen_config.py")
        )
        
        # 获取模型客户端
        model_client = autogen_config.get_model_client()
        
        # 初始化Agent
        agent = conclusion_agent.ConclusionAgent(model_client)
        
        # 获取Agent信息
        info = agent.get_agent_info()
        print(f"\n✓ Agent初始化成功!")
        print(f"  Agent名称：{info['name']}")
        print(f"  模板路径：{info['template_path']}")
        print(f"  System Message长度：{info['system_message_length']}字符")
        
        return True, agent
        
    except FileNotFoundError as e:
        print(f"✗ 提示词模板文件不存在: {str(e)}")
        print("  提示: 请确保 templates/prompts/conclusion.md 存在")
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
    
    if agent is None:
        print("⚠ Agent未初始化，跳过测试")
        return False
    
    try:
        # 加载conclusion_data模块
        conclusion_data = load_module(
            "conclusion_data",
            os.path.join(project_root, "src", "models", "conclusion_data.py")
        )
        
        # 获取示例数据
        data = conclusion_data.get_sample_data()
        
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
        # 加载conclusion_data模块
        conclusion_data = load_module(
            "conclusion_data",
            os.path.join(project_root, "src", "models", "conclusion_data.py")
        )
        
        # 测试合规性结论模型
        合规性 = conclusion_data.合规性结论(
            法律法规结论="符合相关法律法规",
            三线结论={
                "耕地和永久基本农田": "不占用",
                "生态保护红线": "不占用",
                "城镇开发边界": "不占用",
            },
            国土空间规划结论={
                "一张图上图落位情况": "已上图",
                "功能分区准入": "符合",
            },
            专项规划结论={
                "综合交通规划": "符合",
            },
            综合结论="合法合规"
        )
        print(f"✓ 合规性结论模型创建成功")
        
        # 测试合理性结论模型
        合理性 = conclusion_data.合理性结论(
            环境影响结论="影响较小",
            矿产资源结论="不压覆",
            地质灾害结论="危险性小",
            综合结论="选址合理"
        )
        print(f"✓ 合理性结论模型创建成功")
        
        # 测试节约集约结论模型
        节约集约 = conclusion_data.节约集约结论(
            功能分区结论="功能分区合理",
            用地规模结论="用地规模合理",
            节地技术结论="技术水平高",
            综合结论="符合节约集约用地要求"
        )
        print(f"✓ 节约集约结论模型创建成功")
        
        # 测试建议项模型
        建议 = conclusion_data.建议项(序号=1, 内容="测试建议内容")
        print(f"✓ 建议项模型创建成功")
        
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
            ConclusionData,
        )
        print(f"✓ 从src.models导入成功")
        print(f"  ConclusionData: {ConclusionData.__name__}")
        
        # 测试从src.agents导入
        try:
            from src.agents import ConclusionAgent
            print(f"✓ 从src.agents导入成功")
            print(f"  ConclusionAgent: {ConclusionAgent.__name__}")
        except ImportError:
            print(f"⚠ 从src.agents导入ConclusionAgent失败（可能提示词模板未创建）")
        
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


def test_excel_parser():
    """测试Excel解析器"""
    print("\n" + "=" * 60)
    print("测试6：Excel解析器")
    print("=" * 60)
    
    try:
        from src.services.excel_parser import ExcelParser
        
        # 测试parse_conclusion方法是否存在
        parser = ExcelParser.__dict__.get('parse_conclusion')
        if parser:
            print(f"✓ parse_conclusion方法已添加到ExcelParser")
        else:
            print(f"✗ parse_conclusion方法未找到")
            return False
        
        # 测试parse_all_with_chapter6方法是否存在
        method = ExcelParser.__dict__.get('parse_all_with_chapter6')
        if method:
            print(f"✓ parse_all_with_chapter6方法已添加到ExcelParser")
        else:
            print(f"✗ parse_all_with_chapter6方法未找到")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Excel解析器测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("第6章结论与建议Agent测试")
    print("=" * 60)
    
    results = []
    
    # 测试1：数据模型
    results.append(("数据模型验证", test_data_model()))
    
    # 测试2：Agent初始化
    success, agent = test_agent_initialization()
    results.append(("Agent初始化", success))
    
    # 测试3：用户消息构建
    results.append(("用户消息构建", test_message_building(agent)))
    
    # 测试4：子模型
    results.append(("子模型验证", test_sub_models()))
    
    # 测试5：模块导入
    results.append(("模块导入验证", test_module_import()))
    
    # 测试6：Excel解析器
    results.append(("Excel解析器", test_excel_parser()))
    
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
        print("\n🎉 所有测试通过！第6章Agent开发完成。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
    
    return all_passed


if __name__ == "__main__":
    main()