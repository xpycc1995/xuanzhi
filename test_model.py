"""
测试选址分析数据模型
"""
import sys
import os

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.site_selection_data import get_sample_data

print("测试选址分析数据模型...")

try:
    data = get_sample_data()
    print("OK - 数据模型创建成功")
    print(f"  项目名称：{data.项目基本信息['项目名称']}")
    print(f"  备选方案数量：{len(data.备选方案)}")
    print(f"  征求意见数量：{len(data.征求意见情况)}")

    # 测试格式化输出
    formatted = data.get_formatted_data()
    print(f"\nOK - 格式化数据生成成功（{len(formatted)}字符）")

    # 测试JSON序列化
    json_str = data.json()
    print(f"OK - JSON序列化成功（{len(json_str)}字符）")

    # 显示格式化数据的前500字符
    print(f"\n格式化数据预览：")
    print(formatted[:500])

except Exception as e:
    print(f"ERROR - 测试失败：{str(e)}")
    import traceback
    traceback.print_exc()
