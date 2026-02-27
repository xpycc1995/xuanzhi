"""
结论与建议Agent数据模型

定义了第6章"结论与建议"所需的所有数据结构。
使用Pydantic进行数据验证，确保数据的完整性和准确性。

特殊说明：第六章需要从前5章的结论中提取关键信息，生成综合论证一览表。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator


# ===== 子模型定义 =====


class 合规性结论(BaseModel):
    """
    合法合规性分析结论

    从第3章提取的合法合规性分析结论。
    """

    法律法规结论: str = Field(
        ..., description="法律法规符合性结论，如'符合相关法律法规及政策文件'"
    )

    三线结论: Dict[str, str] = Field(
        ...,
        description="三线协调结论，键为'耕地和永久基本农田'/'生态保护红线'/'城镇开发边界'",
    )

    国土空间规划结论: Dict[str, str] = Field(
        ...,
        description="国土空间规划结论，如'一张图上图落位'/'功能分区准入'/'用途管制'",
    )

    专项规划结论: Dict[str, str] = Field(
        ...,
        description="专项规划符合性结论，如'综合交通规划'/'市政基础设施规划'/'历史文化遗产保护规划'等",
    )

    其他规划结论: Optional[Dict[str, str]] = Field(
        None, description="其他规划符合性结论，如'国民经济规划'/'行业规划'等"
    )

    城乡总体规划结论: Optional[str] = Field(
        None, description="过渡期内城乡总体规划符合性结论"
    )

    综合结论: str = Field(..., description="合法合规性综合结论")


class 合理性结论(BaseModel):
    """
    选址合理性分析结论

    从第4章提取的选址合理性分析结论。
    """

    环境影响结论: str = Field(..., description="环境影响分析结论")

    矿产资源结论: str = Field(..., description="矿产资源压覆情况结论")

    地质灾害结论: str = Field(..., description="地质灾害影响结论")

    社会稳定结论: Optional[str] = Field(None, description="社会稳定影响结论")

    节能结论: Optional[str] = Field(None, description="节能分析结论")

    综合结论: str = Field(..., description="选址合理性综合结论")


class 节约集约结论(BaseModel):
    """
    节约集约用地分析结论

    从第5章提取的节约集约用地分析结论。
    """

    功能分区结论: str = Field(..., description="功能分区合理性结论")

    用地规模结论: str = Field(..., description="用地规模合理性结论")

    节地技术结论: str = Field(..., description="节地技术水平结论")

    综合结论: str = Field(..., description="节约集约用地综合结论")


class 建议项(BaseModel):
    """
    单条建议

    主要建议的每一条建议内容。
    """

    序号: int = Field(..., ge=1, le=5, description="建议序号，范围为1-5")

    内容: str = Field(..., description="建议内容，应具体可行")


# ===== 根模型定义 =====


class ConclusionData(BaseModel):
    """
    第六章结论与建议数据模型（根模型）

    该模型包含生成第6章所需的所有数据。

    特殊设计：
    - 数据可从前5章生成内容中提取
    - 也可从Excel输入独立提供
    - 建议条数固定为5条
    """

    # 项目基本信息（从第1章提取）
    项目基本信息: Dict[str, str] = Field(
        ..., description="项目名称、建设单位、建设性质、投资等基本信息"
    )

    # 6.1 综合论证结论
    合法合规性结论: 合规性结论 = Field(..., description="合法合规性分析结论")

    选址合理性结论: 合理性结论 = Field(..., description="选址合理性分析结论")

    节约集约用地结论: 节约集约结论 = Field(
        ..., description="节约集约用地分析结论"
    )

    综合论证结论: str = Field(..., description="综合论证最终结论")

    # 6.2 主要建议（固定5条）
    建议列表: List[建议项] = Field(
        ..., min_length=5, max_length=5, description="5条主要建议"
    )

    # 元数据
    数据来源: Optional[str] = Field(None, description="数据来源说明")

    编制日期: Optional[str] = Field(None, description="报告编制日期")

    @field_validator("建议列表")
    @classmethod
    def validate_suggestions(cls, v):
        """验证建议列表"""
        if len(v) != 5:
            raise ValueError("必须提供5条建议")

        # 验证序号连续
        for i, item in enumerate(v, 1):
            if item.序号 != i:
                raise ValueError(f"建议序号必须从1到5连续，当前第{i}条序号为{item.序号}")

        return v

    def get_formatted_data(self) -> str:
        """
        获取格式化的数据描述，用于提示词

        Returns:
            格式化的数据字符串
        """
        lines = []

        # 项目概述
        lines.append("# 项目基本信息")
        for key, value in self.项目基本信息.items():
            lines.append(f"- {key}：{value}")

        # 合法合规性结论
        lines.append("\n# 合法合规性结论")
        lines.append(f"- 法律法规结论：{self.合法合规性结论.法律法规结论}")

        lines.append("\n## 三线协调结论")
        for key, value in self.合法合规性结论.三线结论.items():
            lines.append(f"- {key}：{value}")

        lines.append("\n## 国土空间规划结论")
        for key, value in self.合法合规性结论.国土空间规划结论.items():
            lines.append(f"- {key}：{value}")

        lines.append("\n## 专项规划结论")
        for key, value in self.合法合规性结论.专项规划结论.items():
            lines.append(f"- {key}：{value}")

        if self.合法合规性结论.其他规划结论:
            lines.append("\n## 其他规划结论")
            for key, value in self.合法合规性结论.其他规划结论.items():
                lines.append(f"- {key}：{value}")

        if self.合法合规性结论.城乡总体规划结论:
            lines.append(
                f"\n## 城乡总体规划结论：{self.合法合规性结论.城乡总体规划结论}"
            )

        lines.append(f"\n## 综合结论：{self.合法合规性结论.综合结论}")

        # 选址合理性结论
        lines.append("\n# 选址合理性结论")
        lines.append(f"- 环境影响结论：{self.选址合理性结论.环境影响结论}")
        lines.append(f"- 矿产资源结论：{self.选址合理性结论.矿产资源结论}")
        lines.append(f"- 地质灾害结论：{self.选址合理性结论.地质灾害结论}")

        if self.选址合理性结论.社会稳定结论:
            lines.append(f"- 社会稳定结论：{self.选址合理性结论.社会稳定结论}")

        if self.选址合理性结论.节能结论:
            lines.append(f"- 节能结论：{self.选址合理性结论.节能结论}")

        lines.append(f"- 综合结论：{self.选址合理性结论.综合结论}")

        # 节约集约用地结论
        lines.append("\n# 节约集约用地结论")
        lines.append(f"- 功能分区结论：{self.节约集约用地结论.功能分区结论}")
        lines.append(f"- 用地规模结论：{self.节约集约用地结论.用地规模结论}")
        lines.append(f"- 节地技术结论：{self.节约集约用地结论.节地技术结论}")
        lines.append(f"- 综合结论：{self.节约集约用地结论.综合结论}")

        # 综合论证结论
        lines.append("\n# 综合论证结论")
        lines.append(self.综合论证结论)

        # 建议列表
        lines.append("\n# 主要建议")
        for suggestion in self.建议列表:
            lines.append(f"（{suggestion.序号}）{suggestion.内容}")

        return "\n".join(lines)


# ===== 示例数据函数 =====


def get_sample_data() -> ConclusionData:
    """
    获取示例数据，用于测试和演示

    基于sample_第六章.md的内容构建示例数据。

    Returns:
        结论与建议分析示例数据
    """
    return ConclusionData(
        项目基本信息={
            "项目名称": "香溪河流域生态环境综合治理项目（峡口镇白鹤污水处理厂）",
            "建设单位": "湖北兴山经济开发区管理委员会",
            "建设性质": "新建",
            "项目投资": "15938.70万元",
            "建设内容": "对香溪河左岸峡口片区的生活污水、峡口集镇部分污水及地表污水进行系统治理和循环利用",
            "用地面积": "10633.00平方米",
            "建设规模": "日处理能力达6000m³/d污水处理厂",
        },
        合法合规性结论=合规性结论(
            法律法规结论="符合相关法律法规及政策文件",
            三线结论={
                "耕地和永久基本农田": "不占用耕地和永久基本农田",
                "生态保护红线": "不占用生态保护红线",
                "城镇开发边界": "不占用城镇开发边界",
            },
            国土空间规划结论={
                "一张图上图落位情况": "已上图",
                "功能分区准入": "符合功能分区准入标准",
                "用途管制": "符合用途管制相关标准",
                "国土空间总体格局": "符合国土空间总体格局",
            },
            专项规划结论={
                "综合交通规划": "符合",
                "市政基础设施规划": "符合",
                "历史文化遗产保护规划": "符合",
                "综合防灾工程规划": "符合",
                "旅游规划": "符合",
                "环境保护规划": "符合",
                "自然保护地规划": "符合",
            },
            其他规划结论={
                "国民经济和社会发展规划": "符合兴山'十四五'香溪河生态修复相关规划",
            },
            城乡总体规划结论="符合峡口镇总体规划（2014-2030）规划布局要求",
            综合结论="符合相关法律法规及各项规划要求",
        ),
        选址合理性结论=合理性结论(
            环境影响结论="影响较小，有防治措施",
            矿产资源结论="未压覆已查明矿产",
            地质灾害结论="受灾程度小，有防治措施",
            社会稳定结论="影响较小，有相应措施",
            节能结论="已采用先进节能技术",
            综合结论="选址合理，符合项目建设要求",
        ),
        节约集约用地结论=节约集约结论(
            功能分区结论="功能分区合理",
            用地规模结论="用地规模各分区合理",
            节地技术结论="较其他项目节地水平更高",
            综合结论="符合节约集约用地要求",
        ),
        综合论证结论="该项目选址符合项目所需的建设场地要求，与各项规划、政策基本协调，项目选址可行",
        建议列表=[
            建议项(
                序号=1,
                内容="项目应进一步衔接和协调建设项目选址与各类规划的关系。",
            ),
            建议项(
                序号=2,
                内容="项目选址应进一步分析项目运营对周边敏感目标（如居民区、学校、自然保护区）的潜在环境影响，确保满足卫生防护距离要求，并论证尾水排放对受纳水体的影响是否在区域水环境容量承载范围之内。",
            ),
            建议项(
                序号=3,
                内容="项目选址须精准落入城镇排水与污水处理系统专项规划所确定的设施布局和服务范围内。应重点复核与城镇污水主干管网的衔接可行性，评估提升泵站的设置需求与成本，确保污水能够经济、高效地收集输送。",
            ),
            建议项(
                序号=4,
                内容="项目选址应精确核算厂区防洪排涝标准（通常应高于50年一遇），核实场地标高与周边河流洪水位的关系，确保厂区不受洪涝威胁。对尾水排放口进行水力模型模拟，优化排放方式，减少对河床、岸线的冲刷。",
            ),
            建议项(
                序号=5,
                内容="项目在环评基础上，可针对选址特性，重点深化恶臭气体扩散模拟，精确划定卫生防护距离，并提前规划高效的除臭系统与绿化隔离带布局方案。",
            ),
        ],
        数据来源="第3、4、5章结论汇总",
        编制日期="2026年2月27日",
    )


# ===== 测试代码 =====

if __name__ == "__main__":
    # 测试数据模型
    print("测试结论与建议数据模型...")

    try:
        data = get_sample_data()
        print(f"✓ 数据模型创建成功")
        print(f"  项目名称：{data.项目基本信息['项目名称']}")
        print(f"  建议数量：{len(data.建议列表)}")
        print(f"  综合论证结论：{data.综合论证结论[:50]}...")

        # 测试格式化输出
        formatted = data.get_formatted_data()
        print(f"\n✓ 格式化数据生成成功（{len(formatted)}字符）")

        # 显示格式化数据预览
        print("\n格式化数据预览：")
        print(formatted[:800])

        # 测试JSON序列化
        import json

        json_str = data.model_dump_json()
        print(f"\n✓ JSON序列化成功（{len(json_str)}字符）")

    except Exception as e:
        print(f"✗ 测试失败：{str(e)}")
        import traceback

        traceback.print_exc()