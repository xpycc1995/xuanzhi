"""
项目概况数据模型

定义了第1章"项目概况"所需的数据结构。
使用Pydantic进行数据验证，确保数据的完整性和准确性。
"""

from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class ProjectOverviewData(BaseModel):
    """
    项目概况数据模型

    包含生成第1章所需的所有基本信息。
    """

    项目名称: str = Field(..., description="项目全称")
    项目代码: Optional[str] = Field(None, description="项目审批代码")
    建设单位: str = Field(..., description="项目建设单位名称")
    建设性质: str = Field(..., description="新建/改扩建/更新改造等")
    项目投资: str = Field(..., description="项目总投资金额及单位")
    项目选址: str = Field(..., description="项目选址位置描述")
    建设内容: str = Field(..., description="主要建设内容描述")
    建设规模: Optional[str] = Field(None, description="建设规模描述")
    建设期限: Optional[str] = Field(None, description="建设周期")

    # 扩展字段（可选）
    扩展信息: Optional[Dict[str, Any]] = Field(
        default=None,
        description="其他扩展信息"
    )

    def to_dict(self) -> Dict[str, str]:
        """
        转换为字典格式，用于编排器调用

        Returns:
            项目信息字典
        """
        result = {
            "项目名称": self.项目名称,
            "建设单位": self.建设单位,
            "建设性质": self.建设性质,
            "项目投资": self.项目投资,
            "项目选址": self.项目选址,
            "建设内容": self.建设内容,
        }

        # 添加可选字段
        if self.项目代码:
            result["项目代码"] = self.项目代码
        if self.建设规模:
            result["建设规模"] = self.建设规模
        if self.建设期限:
            result["建设期限"] = self.建设期限

        # 添加扩展信息
        if self.扩展信息:
            for key, value in self.扩展信息.items():
                if key not in result:
                    result[key] = str(value)

        return result


def get_sample_project_overview_data() -> ProjectOverviewData:
    """
    获取项目概况示例数据，用于测试和演示

    Returns:
        项目概况示例数据
    """
    return ProjectOverviewData(
        项目名称="汉川市万福低闸等3座灌溉闸站更新改造工程项目",
        项目代码="2512-420984-04-01-395957",
        建设单位="汉川市水利和湖泊局",
        建设性质="更新改造",
        项目投资="7847.03万元",
        项目选址="龚家湾低闸泵站位于脉旺镇,万福低闸泵站、杜公泵站位于沉湖镇",
        建设内容="新建万福低闸泵站和龚家湾低闸泵站,改造杜公泵站。其中万福低闸灌溉泵站装机功率1350kW,设计流量10.0m³/s;龚家湾低闸灌溉泵站装机功率1800kW,设计流量12.0m³/s;杜公泵站装机功率560kW,设计流量3.0m³/s。",
        建设规模="总装机功率3710kW,总设计流量25.0m³/s",
        建设期限="24个月"
    )


if __name__ == "__main__":
    # 测试数据模型
    print("测试项目概况数据模型...")

    try:
        data = get_sample_project_overview_data()
        print(f"数据模型创建成功")
        print(f"  项目名称: {data.项目名称}")
        print(f"  建设单位: {data.建设单位}")

        # 测试转换为字典
        data_dict = data.to_dict()
        print(f"\n转换为字典成功 ({len(data_dict)} 个字段)")
        for key, value in data_dict.items():
            print(f"  - {key}: {value[:30]}..." if len(str(value)) > 30 else f"  - {key}: {value}")

        # 测试JSON序列化
        json_str = data.model_dump_json()
        print(f"\nJSON序列化成功 ({len(json_str)} 字符)")

    except Exception as e:
        print(f"测试失败: {str(e)}")