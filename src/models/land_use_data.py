"""
节约集约用地分析Agent数据模型

定义了第5章"建设项目节约集约用地分析"所需的所有数据结构。
使用Pydantic进行数据验证，确保数据的完整性和准确性。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator


class FunctionalZone(BaseModel):
    """
    功能分区数据模型

    表示项目的一个功能分区。
    """
    分区名称: str = Field(..., description="分区名称，如'生产区用地'、'生产管理及辅助生产区用地'")
    分区面积: float = Field(..., gt=0, description="分区面积（平方米）")
    占比: float = Field(..., gt=0, le=100, description="占总用地面积的比例（%）")
    子分区: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="子分区列表，如二级处理区、深度处理区等"
    )
    功能描述: Optional[str] = Field(None, description="分区功能描述")
    用地依据: Optional[str] = Field(None, description="用地标准依据文件")


class OverallLandIndicator(BaseModel):
    """
    总体用地指标数据模型
    """
    项目总用地面积: float = Field(..., gt=0, description="项目总用地面积（平方米）")
    建设规模: str = Field(..., description="项目建设规模，如'6000m³/d'")
    标准依据: str = Field(..., description="用地标准依据文件")
    标准要求范围: str = Field(..., description="标准规定的用地指标范围")
    是否符合要求: bool = Field(..., description="是否符合节约集约用地要求")
    对比分析: Optional[str] = Field(None, description="与标准的对比分析说明")


class SubAreaIndicator(BaseModel):
    """
    子区域用地指标数据模型
    """
    区域名称: str = Field(..., description="区域名称，如'二级处理区'、'深度处理区'")
    实际用地面积: float = Field(..., gt=0, description="实际用地面积（平方米）")
    标准依据: str = Field(..., description="用地标准依据文件")
    标准指标值: str = Field(..., description="标准规定的用地指标值")
    是否符合要求: bool = Field(..., description="是否符合节约集约用地要求")
    对比分析: Optional[str] = Field(None, description="与标准的对比分析说明")


class LandScaleAnalysis(BaseModel):
    """
    用地规模合理性分析数据模型
    """
    总体指标: OverallLandIndicator = Field(..., description="项目用地总体指标情况")
    各分区指标: List[SubAreaIndicator] = Field(
        ...,
        description="各功能分区用地指标情况"
    )
    辅助区用地占比: Optional[Dict[str, Any]] = Field(
        None,
        description="生产管理及辅助生产区用地占比分析"
    )
    综合评价: Optional[str] = Field(None, description="用地规模综合评价")


class PreConstructionMeasure(BaseModel):
    """
    前期工作阶段节地措施数据模型
    """
    措施名称: str = Field(..., description="措施名称，如'把好选线关'")
    措施描述: str = Field(..., description="措施详细描述")
    实施效果: Optional[str] = Field(None, description="实施效果说明")


class ConstructionPhaseMeasure(BaseModel):
    """
    建设实施阶段节地措施数据模型
    """
    措施名称: str = Field(..., description="措施名称")
    措施描述: str = Field(..., description="措施详细描述")
    实施主体: Optional[str] = Field(None, description="实施主体，如'项目法人'、'施工单位'")
    实施效果: Optional[str] = Field(None, description="实施效果说明")


class LandSavingTechnology(BaseModel):
    """
    节地技术数据模型
    """
    前期工作阶段措施: List[PreConstructionMeasure] = Field(
        ...,
        description="前期工作阶段节地措施"
    )
    建设实施阶段措施: List[ConstructionPhaseMeasure] = Field(
        ...,
        description="建设实施阶段节地措施"
    )
    综合评价: Optional[str] = Field(None, description="节地技术综合评价")


class ComparisonCase(BaseModel):
    """
    案例对比数据模型
    """
    案例名称: str = Field(..., description="案例名称")
    案例地点: Optional[str] = Field(None, description="案例地点")
    建设规模: str = Field(..., description="建设规模，如'30000m³/d'")
    用地面积: float = Field(..., gt=0, description="用地面积（平方米）")
    总投资: float = Field(..., gt=0, description="总投资（万元）")
    采用技术: Optional[str] = Field(None, description="采用的工艺技术")
    数据来源: Optional[str] = Field(None, description="数据来源")


class CaseComparison(BaseModel):
    """
    案例对比分析数据模型
    """
    本项目: ComparisonCase = Field(..., description="本项目数据")
    对比案例: List[ComparisonCase] = Field(
        ...,
        min_items=1,
        max_items=3,
        description="对比案例列表，通常1-3个案例"
    )
    对比结论: str = Field(..., description="案例对比结论分析")
    单位投资对比: Optional[Dict[str, float]] = Field(
        None,
        description="各单位用地投资量对比"
    )


class LandUseData(BaseModel):
    """
    节约集约用地分析数据模型（根模型）

    包含生成第5章所需的所有数据。
    """
    # 基本信息
    项目基本信息: Dict[str, str] = Field(
        ...,
        description="项目基本信息：项目名称、建设单位、建设性质、投资等"
    )

    # 功能分区
    功能分区情况: List[FunctionalZone] = Field(
        ...,
        min_items=1,
        description="项目功能分区列表"
    )

    # 用地规模
    用地规模合理性: LandScaleAnalysis = Field(
        ...,
        description="用地规模合理性分析"
    )

    # 节地技术
    采用的节地技术: LandSavingTechnology = Field(
        ...,
        description="采用的节地技术"
    )

    # 案例对比
    案例对比情况: CaseComparison = Field(
        ...,
        description="案例对比情况"
    )

    # 结论
    节约集约用地小结: Optional[str] = Field(
        None,
        description="节约集约用地分析小结"
    )

    # 元数据
    数据来源: Optional[str] = Field(
        None,
        description="数据来源说明"
    )
    编制日期: Optional[str] = Field(
        None,
        description="报告编制日期"
    )

    def get_formatted_data(self) -> str:
        """
        获取格式化的数据描述，用于提示词

        Returns:
            格式化的数据字符串
        """
        lines = []
        lines.append("# 项目基本信息")
        for key, value in self.项目基本信息.items():
            lines.append(f"- {key}：{value}")

        lines.append("\n# 功能分区情况")
        for zone in self.功能分区情况:
            lines.append(f"\n## {zone.分区名称}")
            lines.append(f"- 面积：{zone.分区面积}平方米")
            lines.append(f"- 占比：{zone.占比}%")
            if zone.功能描述:
                lines.append(f"- 功能描述：{zone.功能描述}")
            if zone.子分区:
                lines.append("- 子分区：")
                for sub in zone.子分区:
                    for k, v in sub.items():
                        lines.append(f"  - {k}：{v}")

        lines.append("\n# 用地规模合理性")
        overall = self.用地规模合理性.总体指标
        lines.append(f"\n## 项目用地总体指标情况")
        lines.append(f"- 项目总用地面积：{overall.项目总用地面积}平方米")
        lines.append(f"- 建设规模：{overall.建设规模}")
        lines.append(f"- 标准依据：{overall.标准依据}")
        lines.append(f"- 标准要求范围：{overall.标准要求范围}")
        lines.append(f"- 是否符合要求：{'是' if overall.是否符合要求 else '否'}")

        lines.append(f"\n## 各功能分区用地指标情况")
        for indicator in self.用地规模合理性.各分区指标:
            lines.append(f"\n### {indicator.区域名称}")
            lines.append(f"- 实际用地面积：{indicator.实际用地面积}平方米")
            lines.append(f"- 标准依据：{indicator.标准依据}")
            lines.append(f"- 标准指标值：{indicator.标准指标值}")
            lines.append(f"- 是否符合要求：{'是' if indicator.是否符合要求 else '否'}")

        lines.append("\n# 采用的节地技术")
        lines.append(f"\n## 前期工作阶段")
        for measure in self.采用的节地技术.前期工作阶段措施:
            lines.append(f"- {measure.措施名称}：{measure.措施描述}")

        lines.append(f"\n## 建设实施阶段")
        for measure in self.采用的节地技术.建设实施阶段措施:
            lines.append(f"- {measure.措施名称}：{measure.措施描述}")

        lines.append("\n# 案例对比情况")
        lines.append(f"\n## 本项目")
        lines.append(f"- 建设规模：{self.案例对比情况.本项目.建设规模}")
        lines.append(f"- 用地面积：{self.案例对比情况.本项目.用地面积}平方米")
        lines.append(f"- 总投资：{self.案例对比情况.本项目.总投资}万元")

        lines.append(f"\n## 对比案例")
        for i, case in enumerate(self.案例对比情况.对比案例, 1):
            lines.append(f"\n### 案例{i}：{case.案例名称}")
            lines.append(f"- 建设规模：{case.建设规模}")
            lines.append(f"- 用地面积：{case.用地面积}平方米")
            lines.append(f"- 总投资：{case.总投资}万元")
            if case.采用技术:
                lines.append(f"- 采用技术：{case.采用技术}")

        lines.append(f"\n## 对比结论")
        lines.append(self.案例对比情况.对比结论)

        if self.节约集约用地小结:
            lines.append(f"\n# 节约集约用地分析小结")
            lines.append(self.节约集约用地小结)

        return "\n".join(lines)


# 示例数据函数
def get_sample_data() -> LandUseData:
    """
    获取示例数据，用于测试和演示

    Returns:
        节约集约用地分析示例数据
    """
    return LandUseData(
        项目基本信息={
            "项目名称": "汉川市万福低闸等3座灌溉闸站更新改造工程项目",
            "建设单位": "汉川市水利和湖泊局",
            "建设性质": "更新改造",
            "项目投资": "7847.03万元",
            "建设内容": "新建万福低闸泵站和龚家湾低闸泵站，改造杜公泵站"
        },
        功能分区情况=[
            FunctionalZone(
                分区名称="生产区用地",
                分区面积=9208.00,
                占比=86.60,
                功能描述="包括二级处理区、深度处理区及污泥处置区",
                子分区=[
                    {"分区名称": "二级处理区用地", "面积": "6383.00平方米", "占比": "60.03%"},
                    {"分区名称": "深度处理区用地", "面积": "1216.00平方米", "占比": "11.44%"},
                    {"分区名称": "污泥处置区用地", "面积": "1609.00平方米", "占比": "15.13%"}
                ],
                用地依据="《城市污水处理工程项目建设标准》（JB198-2022）第十八条"
            ),
            FunctionalZone(
                分区名称="生产管理及辅助生产区用地",
                分区面积=1425.00,
                占比=13.40,
                功能描述="包括生产管理用房、辅助生产设施等",
                用地依据="《城市污水处理工程项目建设标准》（JB198-2022）第二十七条"
            )
        ],
        用地规模合理性=LandScaleAnalysis(
            总体指标=OverallLandIndicator(
                项目总用地面积=10633.00,
                建设规模="6000m³/d",
                标准依据="《湖北省产业用地目录和用地标准（2023年本）》第六章",
                标准要求范围="7500～12000平方米",
                是否符合要求=True,
                对比分析="本项目拟建设面积为10633.00平方米，满足用地指标要求，符合节约集约用地要求"
            ),
            各分区指标=[
                SubAreaIndicator(
                    区域名称="二级处理区",
                    实际用地面积=6383.00,
                    标准依据="《城市污水处理工程项目建设标准》（JB198-2022）表2",
                    标准指标值="9000平方米（按1.5×6000÷10000计算）",
                    是否符合要求=True,
                    对比分析="实际用地低于控制指标，符合节约集约用地要求"
                ),
                SubAreaIndicator(
                    区域名称="深度处理区",
                    实际用地面积=1216.00,
                    标准依据="《城市污水处理工程项目建设标准》（JB198-2022）表2",
                    标准指标值="2700平方米（按0.45×6000÷10000计算）",
                    是否符合要求=True,
                    对比分析="实际用地低于控制指标，符合节约集约用地要求"
                ),
                SubAreaIndicator(
                    区域名称="污泥处置区",
                    实际用地面积=1609.00,
                    标准依据="《城市排水工程规划规范》（GB50318-2017）表1",
                    标准指标值="3000平方米",
                    是否符合要求=True,
                    对比分析="实际用地低于控制指标，符合节约集约用地要求"
                )
            ],
            辅助区用地占比={
                "实际占比": "13.40%",
                "标准要求范围": "8%～20%",
                "是否符合": True
            },
            综合评价="各类用地指标均低于国家标准规定限制，符合节约集约用地要求"
        ),
        采用的节地技术=LandSavingTechnology(
            前期工作阶段措施=[
                PreConstructionMeasure(
                    措施名称="把好选线关",
                    措施描述="在遵循项目有关设计规范标准的前提下，以尽可能减少占用土地为原则，结合其他影响选线的因素进行深入研究，通过反复比选和论证，确定合理的选址方案",
                    实施效果="最大限度节约土地、保护耕地"
                ),
                PreConstructionMeasure(
                    措施名称="注重项目方案比选工作",
                    措施描述="项目方案设计中，在深入调查、论证的基础上确定合理的主要控制点，将土地占用情况作为方案选择的重要指标",
                    实施效果="优先选择能够最大限度节约土地的方案"
                ),
                PreConstructionMeasure(
                    措施名称="细化、优化、深化设计方案比选",
                    措施描述="在满足功能要求、防火要求的前提下，通过合理优化设计可达到节约用地的目的",
                    实施效果="合理布置建筑之间间距，降低土地占用"
                )
            ],
            建设实施阶段措施=[
                ConstructionPhaseMeasure(
                    措施名称="施工招标要求",
                    措施描述="项目施工招标时，应将耕地保护的有关条款列入招标文件，并严格执行",
                    实施主体="招标单位"
                ),
                ConstructionPhaseMeasure(
                    措施名称="项目法人职责",
                    措施描述="项目法人要增强耕地保护意识，统筹工程实施临时用地，加强科学指导",
                    实施主体="项目法人"
                ),
                ConstructionPhaseMeasure(
                    措施名称="施工单位要求",
                    措施描述="施工单位要严格控制临时用地数量，施工便道、各种料场、预制场要根据工程进度统筹考虑，尽可能设置在项目用地范围内或利用荒坡、废弃地解决",
                    实施主体="施工单位"
                ),
                ConstructionPhaseMeasure(
                    措施名称="废弃地处理",
                    措施描述="建设中废弃的空地要尽可能造地复垦，不能复垦的要尽量绿化，避免闲置浪费",
                    实施主体="施工单位"
                )
            ],
            综合评价="项目采用了先进的节地技术，符合节约集约用地要求"
        ),
        案例对比情况=CaseComparison(
            本项目=ComparisonCase(
                案例名称="本项目",
                建设规模="6000m³/d",
                用地面积=10633.00,
                总投资=15938.70,
                采用技术="A³/O生化池→二沉池→高效沉淀池+滤布滤池→紫外线消毒"
            ),
            对比案例=[
                ComparisonCase(
                    案例名称="黄埔镇大雁生活污水处理厂新建工程",
                    案例地点="中山市黄圃镇",
                    建设规模="30000m³/d",
                    用地面积=12367.61,
                    总投资=166426.7,
                    采用技术="粗格柵及提升泵房→细格栅及曝气沉砂池→调节池/事故池→A³/O生化池→二沉池→高效沉淀池+滤布滤池→紫外线消毒",
                    数据来源="公开资料"
                ),
                ComparisonCase(
                    案例名称="阳春市河西污水处理厂工程",
                    案例地点="阳春市河西街道",
                    建设规模="10000m³/d",
                    用地面积=14800.00,
                    总投资=25134.2,
                    采用技术="分体式水解酸化+A2/O+絮凝沉淀+过滤",
                    数据来源="公开资料"
                )
            ],
            对比结论="本项目单位用地投资量为1.50万元/平方米，低于对比案例，表明本项目节地水平较先进，节约集约利用效率较高",
            单位投资对比={
                "本项目": 1.50,
                "案例1": 5.36,
                "案例2": 1.70
            }
        ),
        节约集约用地小结="项目用地功能分区合理，且各类用地指标均低于国家标准规定限制，同时采用先进节地技术，合理节约利用土地，实现耕地有效保护，与国内同规模同类型项目相比，本项目占地面积较小，投入资金较低，表明本项目节约集约用地方面较为先进，满足项目建设需求。",
        数据来源="项目规划设计文件、用地标准文件、公开资料",
        编制日期="2026年2月26日"
    )


if __name__ == "__main__":
    # 测试数据模型
    print("测试节约集约用地分析数据模型...")

    try:
        data = get_sample_data()
        print(f"✓ 数据模型创建成功")
        print(f"  项目名称：{data.项目基本信息['项目名称']}")
        print(f"  功能分区数量：{len(data.功能分区情况)}")
        print(f"  项目总用地面积：{data.用地规模合理性.总体指标.项目总用地面积}平方米")

        # 测试格式化输出
        formatted = data.get_formatted_data()
        print(f"\n✓ 格式化数据生成成功（{len(formatted)}字符）")

        # 测试JSON序列化
        import json
        json_str = data.json()
        print(f"✓ JSON序列化成功（{len(json_str)}字符）")

    except Exception as e:
        print(f"✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()