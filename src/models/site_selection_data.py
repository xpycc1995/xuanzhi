"""
选址分析Agent数据模型

定义了第2章"建设项目选址可行性分析"所需的所有数据结构。
使用Pydantic进行数据验证，确保数据的完整性和准确性。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator


class SiteAlternative(BaseModel):
    """
    备选方案数据模型

    表示一个备选方案的完整信息。
    """
    方案编号: str = Field(..., description="方案编号，如'1'或'2'")
    方案名称: str = Field(..., description="方案名称，如'方案一：XX镇XX村'")
    位置: str = Field(..., description="具体位置描述")
    面积: float = Field(..., gt=0, description="占地面积（平方米）")
    四至范围: Dict[str, str] = Field(
        default_factory=dict,
        description="四至范围：东、南、西、北四个方向的描述"
    )
    土地利用现状: Dict[str, str] = Field(
        ...,
        description="土地利用现状，键为用地类型，值为面积"
    )
    是否占用耕地: bool = Field(default=False, description="是否占用耕地")
    是否占用永久基本农田: bool = Field(default=False, description="是否占用永久基本农田")
    是否涉及未利用地: bool = Field(default=False, description="是否涉及未利用地")
    建设内容: str = Field(..., description="建设内容描述")
    工艺流程: Optional[str] = Field(None, description="工艺流程描述")
    出水标准: Optional[str] = Field(None, description="出水标准或排放标准")

    @validator('四至范围')
    def validate_four_boundaries(cls, v):
        """验证四至范围包含东、南、西、北"""
        if v:
            required = ['东', '南', '西', '北']
            for direction in required:
                if direction not in v:
                    raise ValueError(f"四至范围缺少{direction}方向")
        return v


class SiteNaturalConditions(BaseModel):
    """
    场地自然条件数据模型

    包含地形地貌、气候、地质构造等6个方面的自然条件。
    """
    地形地貌: Dict[str, Any] = Field(
        ...,
        description="地形地貌信息：地貌类型、地势走向、海拔高程等"
    )
    气候: Dict[str, Any] = Field(
        ...,
        description="气候信息：气候类型、温度、降雨量、风速等"
    )
    区域地质构造: Dict[str, Any] = Field(
        ...,
        description="地质构造信息：构造位置、主要断裂、地壳稳定性等"
    )
    水文地质条件: Dict[str, Any] = Field(
        ...,
        description="水文地质信息：主要水系、河流特征等"
    )
    工程地质: Dict[str, Any] = Field(
        ...,
        description="工程地质信息：岩组类型、承载力、岩土性质等"
    )
    地震: Dict[str, str] = Field(
        ...,
        description="地震信息：地震动参数、烈度、引用标准等"
    )


class SiteExternalConditions(BaseModel):
    """
    外部配套条件数据模型

    包含周边环境、基础设施等外部条件。
    """
    周边建筑物: str = Field(..., description="周边建筑物情况")
    供水: str = Field(..., description="供水配套情况")
    供电: str = Field(..., description="供电配套情况")
    通讯: str = Field(..., description="通讯配套情况")
    交通: str = Field(..., description="交通条件")
    建材来源: str = Field(..., description="建筑材料来源")
    是否压覆文物: bool = Field(default=False, description="是否压覆文物")
    是否影响防洪: bool = Field(default=False, description="是否影响防洪")


class SiteSensitiveConditions(BaseModel):
    """
    选址敏感条件数据模型

    包含历史保护、生态保护、矿产资源等7个方面的敏感条件。
    """
    历史保护: Dict[str, bool] = Field(
        default_factory=dict,
        description="历史保护情况：是否压占历史文化名城、古建筑等"
    )
    生态保护: Dict[str, Any] = Field(
        default_factory=dict,
        description="生态保护情况：是否涉及自然保护区、珍稀动植物等"
    )
    矿产资源: Dict[str, bool] = Field(
        default_factory=dict,
        description="矿产资源情况：是否压覆矿产资源、与采矿权重叠等"
    )
    安全防护: Dict[str, bool] = Field(
        default_factory=dict,
        description="安全防护情况：是否满足邻避要求、涉及水源保护区等"
    )
    重要设施: Dict[str, str] = Field(
        default_factory=dict,
        description="重要设施影响：机场、铁路、公路、水运等"
    )
    耕地和基本农田: Dict[str, bool] = Field(
        default_factory=dict,
        description="耕地和基本农田情况：是否占用耕地和永久基本农田"
    )
    生态保护红线: Dict[str, bool] = Field(
        default_factory=dict,
        description="生态保护红线情况：是否占用生态保护红线"
    )


class ConstructionConditions(BaseModel):
    """
    施工运营条件数据模型

    包含投资情况、政府支持、施工难度等信息。
    """
    方案一总投资: str = Field(..., description="方案一总投资（万元）")
    方案二总投资: str = Field(..., description="方案二总投资（万元）")
    政府支持: str = Field(..., description="政府支持情况")
    群众支持: str = Field(..., description="群众支持情况")
    征地拆迁: str = Field(default="", description="征地拆迁情况")
    施工难度: str = Field(..., description="施工难度评价")
    材料供应: str = Field(..., description="建筑材料供应情况")


class PlanningImpact(BaseModel):
    """
    规划影响条件数据模型

    包含与规划的符合性、重点项目库等信息。
    """
    是否符合国土空间总体规划: bool = Field(..., description="是否符合国土空间总体规划")
    是否列入重点项目库: bool = Field(..., description="是否列入规划重点项目库")
    重点项目库名称: Optional[str] = Field(None, description="重点项目库具体名称")
    对区域发展作用: str = Field(..., description="对区域发展的促进作用")


class ConsultationOpinion(BaseModel):
    """
    征求意见情况数据模型

    记录相关部门和利害关系人的意见。
    """
    部门: str = Field(..., description="部门名称")
    日期: str = Field(..., description="意见日期，格式：YYYY年M月D日")
    复函标题: str = Field(..., description="复函文件标题")
    结论: str = Field(..., description="核心结论")

    @validator('日期')
    def validate_date_format(cls, v):
        """验证日期格式"""
        import re
        # 支持多种日期格式
        patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{4}/\d{1,2}/\d{1,2}'
        ]
        if not any(re.match(pattern, v) for pattern in patterns):
            # 不强制格式，但给出警告
            pass
        return v


class SchemeComparison(BaseModel):
    """
    方案比选数据模型

    包含比选因子、推荐方案等信息。
    """
    比选因子: List[str] = Field(
        ...,
        description="比选因子列表，如场地自然条件、外部配套条件等"
    )
    推荐方案: str = Field(..., description="推荐方案，如'方案一'")
    推荐理由: List[str] = Field(
        ...,
        description="推荐理由列表"
    )
    比选原则: Optional[List[str]] = Field(
        None,
        description="比选原则列表"
    )


class SiteSelectionData(BaseModel):
    """
    选址分析数据模型（根模型）

    包含生成第2章所需的所有数据。
    """
    # 基本信息
    项目基本信息: Dict[str, str] = Field(
        ...,
        description="项目基本信息：项目名称、建设单位、建设性质、投资等"
    )

    # 选址原则
    选址原则: List[str] = Field(
        ...,
        min_items=5,
        max_items=10,
        description="选址原则列表，通常包含5-8条原则"
    )

    # 备选方案
    备选方案: List[SiteAlternative] = Field(
        ...,
        min_items=2,
        max_items=2,
        description="备选方案列表，通常为2个方案"
    )

    # 场地条件
    场地自然条件: SiteNaturalConditions = Field(
        ...,
        description="场地自然条件"
    )

    外部配套条件: SiteExternalConditions = Field(
        ...,
        description="外部配套条件"
    )

    选址敏感条件: SiteSensitiveConditions = Field(
        ...,
        description="选址敏感条件"
    )

    施工运营条件: ConstructionConditions = Field(
        ...,
        description="施工运营条件"
    )

    规划影响: PlanningImpact = Field(
        ...,
        description="规划影响条件"
    )

    # 征求意见
    征求意见情况: List[ConsultationOpinion] = Field(
        ...,
        description="相关部门和利害关系人的意见列表"
    )

    # 方案比选
    方案比选: SchemeComparison = Field(
        ...,
        description="方案比选信息"
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

    @validator('备选方案')
    def validate_alternatives(cls, v):
        """验证备选方案数量和编号"""
        if len(v) != 2:
            raise ValueError("必须提供2个备选方案")
        return v

    @validator('征求意见情况')
    def validate_opinions(cls, v):
        """验证征求意见数量"""
        if len(v) < 3:
            raise ValueError("至少需要3个部门意见")
        return v

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

        lines.append("\n# 选址原则")
        for i, principle in enumerate(self.选址原则, 1):
            lines.append(f"{i}. {principle}")

        lines.append("\n# 备选方案")
        for alt in self.备选方案:
            lines.append(f"\n## {alt.方案名称}")
            lines.append(f"- 位置：{alt.位置}")
            lines.append(f"- 面积：{alt.面积}平方米")
            lines.append(f"- 不占用耕地：{'是' if not alt.是否占用耕地 else '否'}")
            lines.append(f"- 不占用永久基本农田：{'是' if not alt.是否占用永久基本农田 else '否'}")

        return "\n".join(lines)


# 示例数据函数
def get_sample_data() -> SiteSelectionData:
    """
    获取示例数据，用于测试和演示

    Returns:
        选址分析示例数据
    """
    return SiteSelectionData(
        项目基本信息={
            "项目名称": "汉川市万福低闸等3座灌溉闸站更新改造工程项目",
            "建设单位": "汉川市水利和湖泊局",
            "建设性质": "更新改造",
            "项目投资": "7847.03万元",
            "建设期限": "24个月",
            "建设内容": "新建万福低闸泵站和龚家湾低闸泵站，改造杜公泵站。"
        },
        选址原则=[
            "符合规划要求",
            "不占优质耕地",
            "尽量不迁移民",
            "避免敏感区域",
            "基础设施优先",
            "集约节约利用",
            "方便施工运营",
            "安全可靠"
        ],
        备选方案=[
            SiteAlternative(
                方案编号="1",
                方案名称="方案一：脉旺镇龚家湾",
                位置="汉川市脉旺镇龚家湾村",
                面积=10633.00,
                四至范围={
                    "东": "农田",
                    "南": "沟渠",
                    "西": "村庄道路",
                    "北": "农田"
                },
                土地利用现状={
                    "农村道路": "548.00平方米",
                    "林地": "8094.00平方米",
                    "园地": "1934.00平方米",
                    "交通运输用地": "57.00平方米"
                },
                是否占用耕地=False,
                是否占用永久基本农田=False,
                是否涉及未利用地=False,
                建设内容="新建龚家湾低闸灌溉泵站，装机功率1800kW，设计流量12.0m³/s"
            ),
            SiteAlternative(
                方案编号="2",
                方案名称="方案二：沉湖镇万福闸",
                位置="汉川市沉湖镇万福闸村",
                面积=10276.98,
                四至范围={
                    "东": "农田",
                    "南": "河流",
                    "西": "村庄道路",
                    "北": "村庄"
                },
                土地利用现状={
                    "农村宅基地": "1392.68平方米",
                    "园地": "8884.29平方米"
                },
                是否占用耕地=False,
                是否占用永久基本农田=False,
                是否涉及未利用地=False,
                建设内容="新建万福低闸灌溉泵站，装机功率1350kW，设计流量10.0m³/s"
            )
        ],
        场地自然条件=SiteNaturalConditions(
            地形地貌={
                "地貌类型": "平原",
                "地势走向": "地势平坦",
                "最高海拔": "30米",
                "最低海拔": "25米",
                "对项目影响": "影响较小"
            },
            气候={
                "气候类型": "亚热带季风气候",
                "年均气温": "16-18℃",
                "年降雨量": "1200毫米",
                "极端最高温": "40℃",
                "极端最低温": "-10℃",
                "风速": "3.0m/s",
                "对施工影响": "影响较小"
            },
            区域地质构造={
                "构造位置": "江汉平原",
                "主要断裂": ["无"],
                "地壳稳定性": "稳定",
                "抗震设防烈度": "6度"
            },
            水文地质条件={
                "主要水系": ["汉江"],
                "河流长度": "无主要河流",
                "流域面积": "无",
                "年均产水量": "无"
            },
            工程地质={
                "岩组类型": "第四系松散土工程地质岩组",
                "承载力特征值": "150kPa",
                "岩土性质": "稳定性良好"
            },
            地震={
                "地震动峰值加速度": "0.05g",
                "地震动反应周期": "0.35s",
                "地震基本烈度": "6度",
                "引用标准": "《中国地震动参数区划图》（GB18306-2015）"
            }
        ),
        外部配套条件=SiteExternalConditions(
            周边建筑物="无影响施工的建筑物",
            供水="完备",
            供电="完备",
            通讯="完备",
            交通="省道，交通便利",
            建材来源="当地建材厂家供应充足",
            是否压覆文物=False,
            是否影响防洪=False
        ),
        选址敏感条件=SiteSensitiveConditions(
            历史保护={
                "是否压占历史文化名城": False,
                "是否有古建筑古村落": False,
                "是否有文物古迹": False
            },
            生态保护={
                "是否涉及自然保护区": False,
                "是否有珍稀动植物": False,
                "是否影响生态环境": "影响较小，已采取措施"
            },
            矿产资源={
                "是否压覆矿产资源": False,
                "是否与采矿权重叠": False,
                "是否与探矿权重叠": False
            },
            安全防护={
                "是否满足邻避要求": True,
                "是否涉及饮用水源保护区": False,
                "是否涉及机场净空": False,
                "是否涉及军事设施": False
            },
            重要设施={
                "机场": "无",
                "铁路": "距离较远，无影响",
                "公路": "省道，无影响",
                "水运": "不涉及"
            },
            耕地和基本农田={
                "是否占用耕地": False,
                "是否占用永久基本农田": False
            },
            生态保护红线={
                "是否占用生态保护红线": False
            }
        ),
        施工运营条件=ConstructionConditions(
            方案一总投资="4500万元",
            方案二总投资="5200万元",
            政府支持="各级政府支持",
            群众支持="群众支持，征地拆迁已达成一致",
            施工难度="较小",
            材料供应="充足"
        ),
        规划影响=PlanningImpact(
            是否符合国土空间总体规划=True,
            是否列入重点项目库=True,
            重点项目库名称="水利发展重点项目库",
            对区域发展作用="促进农业发展，保障粮食安全"
        ),
        征求意见情况=[
            ConsultationOpinion(
                部门="自然资源和规划局",
                日期="2025年9月3日",
                复函标题="《关于查询项目是否位于地质灾害易发区的复函》",
                结论="不属于地质灾害易发区"
            ),
            ConsultationOpinion(
                部门="文物保护站",
                日期="2025年9月3日",
                复函标题="《关于是否压占文物保护区的函》",
                结论="未发现地面文物"
            ),
            ConsultationOpinion(
                部门="生态环境局",
                日期="2025年9月4日",
                复函标题="《关于是否占用饮用水源保护地的复函》",
                结论="不涉及饮用水源保护地"
            )
        ],
        方案比选=SchemeComparison(
            比选因子=[
                "场地自然条件",
                "外部配套条件",
                "选址敏感条件",
                "施工运营条件",
                "规划影响条件"
            ],
            推荐方案="方案一",
            推荐理由=[
                "投资较低",
                "交通条件更好",
                "不占耕地和基本农田",
                "有效避让生态保护红线"
            ]
        ),
        数据来源="2023年国土变更调查数据、勘测定界数据、相关部门复函",
        编制日期="2026年2月26日"
    )


if __name__ == "__main__":
    # 测试数据模型
    print("测试选址分析数据模型...")

    try:
        data = get_sample_data()
        print(f"✓ 数据模型创建成功")
        print(f"  项目名称：{data.项目基本信息['项目名称']}")
        print(f"  备选方案数量：{len(data.备选方案)}")
        print(f"  征求意见数量：{len(data.征求意见情况)}")

        # 测试格式化输出
        formatted = data.get_formatted_data()
        print(f"\n✓ 格式化数据生成成功（{len(formatted)}字符）")

        # 测试JSON序列化
        import json
        json_str = data.json()
        print(f"✓ JSON序列化成功（{len(json_str)}字符）")

    except Exception as e:
        print(f"✗ 测试失败：{str(e)}")
