"""
合法合规性分析数据模型

定义了第3章"建设项目合法合规性分析"所需的所有数据结构。
使用Pydantic进行数据验证，确保数据的完整性和准确性。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator

# ============================================================================
# 子模型定义
# ============================================================================

class RegulationCompliance(BaseModel):
    """
    法规政策符合性数据模型
    
    表示单个法规或政策文件的符合性分析。
    """
    法规名称: str = Field(..., description="法规或政策文件名称")
    发布单位: Optional[str] = Field(None, description="发布单位")
    发布时间: Optional[str] = Field(None, description="发布时间，格式如'2024年'")
    符合性分析: str = Field(..., description="符合性分析内容")
    符合性结论: str = Field(..., description="符合/不符合/部分符合")


class ThreeLinesAnalysis(BaseModel):
    """
    三线协调分析数据模型
    
    分析项目与生态保护红线、永久基本农田、城镇开发边界的协调情况。
    """
    是否占用耕地: bool = Field(default=False, description="是否占用耕地")
    耕地面积: Optional[str] = Field(None, description="占用耕地面积（平方米）")
    是否占用永久基本农田: bool = Field(default=False, description="是否占用永久基本农田")
    永久基本农田面积: Optional[str] = Field(None, description="占用永久基本农田面积（平方米）")
    是否占用生态保护红线: bool = Field(default=False, description="是否占用生态保护红线")
    生态保护红线面积: Optional[str] = Field(None, description="占用生态保护红线面积（平方米）")
    是否占用城镇开发边界: bool = Field(default=False, description="是否位于城镇开发边界内")
    城镇开发边界说明: Optional[str] = Field(None, description="城镇开发边界相关说明")
    符合性说明: str = Field(..., description="三线协调符合性说明")
    数据来源: Optional[str] = Field(None, description="数据来源，如'2023年国土变更调查数据'")


class OneMapAnalysis(BaseModel):
    """
    国土空间规划"一张图"落位分析数据模型
    """
    是否上图: bool = Field(..., description="是否已上图落位")
    重点项目库名称: Optional[str] = Field(None, description="重点项目库名称")
    项目类型: Optional[str] = Field(None, description="项目类型，如'生态修复重点工程'")
    落位说明: str = Field(..., description="落位情况说明")


class FunctionalZoneAnalysis(BaseModel):
    """
    功能分区准入分析数据模型
    """
    城镇建设适宜性: str = Field(..., description="城镇建设适宜性评价结果")
    生态保护重要性: str = Field(..., description="生态保护重要性评价结果")
    农业生产适宜性: str = Field(..., description="农业生产适宜性评价结果")
    符合性说明: str = Field(..., description="功能分区准入符合性说明")


class SpatialPlanningCompliance(BaseModel):
    """
    国土空间总体规划符合性数据模型
    """
    一张图分析: OneMapAnalysis = Field(..., description="一张图落位分析")
    功能分区准入: FunctionalZoneAnalysis = Field(..., description="功能分区准入分析")
    用途管制符合性: str = Field(..., description="用途管制符合性说明")
    国土空间格局符合性: str = Field(..., description="国土空间总体格局符合性说明")
    总体符合性结论: str = Field(..., description="总体符合性结论")


class SpecialPlanCompliance(BaseModel):
    """
    单项专项规划符合性数据模型
    """
    规划名称: str = Field(..., description="规划名称")
    符合性分析: str = Field(..., description="符合性分析内容")
    符合性结论: str = Field(..., description="符合/不符合")


class SpecialPlanningCompliance(BaseModel):
    """
    专项规划符合性数据模型
    
    包含交通、市政、历史保护、防灾、旅游等专项规划的符合性分析。
    """
    综合交通规划: SpecialPlanCompliance = Field(..., description="综合交通体系规划符合性")
    市政基础设施规划: SpecialPlanCompliance = Field(..., description="市政基础设施规划符合性")
    历史文化遗产保护规划: SpecialPlanCompliance = Field(..., description="历史文化遗产保护规划符合性")
    综合防灾工程规划: SpecialPlanCompliance = Field(..., description="综合防灾工程规划符合性")
    旅游规划: SpecialPlanCompliance = Field(..., description="旅游规划符合性")
    环境保护规划: Optional[SpecialPlanCompliance] = Field(None, description="环境保护规划符合性")
    自然保护地规划: Optional[SpecialPlanCompliance] = Field(None, description="自然保护地规划符合性")


class OtherPlanningCompliance(BaseModel):
    """
    其他相关规划符合性数据模型
    
    包含国民经济规划、环保规划、"三线一单"等规划的符合性分析。
    """
    国民经济和社会发展规划: SpecialPlanCompliance = Field(
        ..., 
        description="国民经济和社会发展规划符合性"
    )
    生态环境保护规划: SpecialPlanCompliance = Field(
        ..., 
        description="生态环境保护规划符合性"
    )
    三线一单生态环境分区管控: SpecialPlanCompliance = Field(
        ..., 
        description="三线一单生态环境分区管控符合性"
    )
    综合交通体系规划: Optional[SpecialPlanCompliance] = Field(
        None, 
        description="综合交通体系规划符合性（如有单独分析）"
    )


class UrbanPlanningCompliance(BaseModel):
    """
    过渡期内城乡总体规划符合性数据模型
    """
    规划名称: str = Field(..., description="城乡总体规划名称")
    规划期限: str = Field(..., description="规划期限，如'2014-2030'")
    空间管制分区: str = Field(..., description="空间管制分区类型，如'适建区'")
    符合性分析: str = Field(..., description="符合性分析内容")
    符合性结论: str = Field(..., description="符合/不符合")


# ============================================================================
# 根模型定义
# ============================================================================

class ComplianceData(BaseModel):
    """
    合法合规性分析数据模型（根模型）
    
    包含生成第3章所需的所有数据。
    """
    
    # 基本信息
    项目基本信息: Dict[str, str] = Field(
        ...,
        description="项目基本信息：项目名称、建设单位、项目性质等"
    )
    
    # 3.1 法规政策符合性
    产业政策符合性: RegulationCompliance = Field(
        ...,
        description="产业政策符合性分析"
    )
    供地政策符合性: RegulationCompliance = Field(
        ...,
        description="供地政策符合性分析"
    )
    其他法规符合性: Optional[List[RegulationCompliance]] = Field(
        None,
        description="其他法规政策符合性分析列表"
    )
    
    # 3.2 三线协调分析
    三线协调分析: ThreeLinesAnalysis = Field(
        ...,
        description="三线和耕地等各类空间协调分析"
    )
    
    # 3.3 国土空间总体规划符合性
    国土空间规划符合性: SpatialPlanningCompliance = Field(
        ...,
        description="国土空间总体规划符合性分析"
    )
    
    # 3.4 专项规划符合性
    专项规划符合性: SpecialPlanningCompliance = Field(
        ...,
        description="专项规划符合性分析"
    )
    
    # 3.5 其他相关规划符合性
    其他规划符合性: OtherPlanningCompliance = Field(
        ...,
        description="其他相关规划符合性分析"
    )
    
    # 3.6 过渡期内城乡总体规划符合性
    城乡总体规划符合性: Optional[UrbanPlanningCompliance] = Field(
        None,
        description="过渡期内城乡总体规划符合性分析"
    )
    
    # 3.7 合法合规性小结
    合法合规小结: str = Field(
        ...,
        description="合法合规性分析综合小结"
    )
    
    # 图表信息
    图表清单: Optional[List[str]] = Field(
        None,
        description="需要插入的图表清单，如图3-1、图3-2等"
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
    
    @field_validator('其他法规符合性')
    @classmethod
    def validate_other_regulations(cls, v):
        """验证其他法规符合性"""
        if v is not None and len(v) == 0:
            return None
        return v
    
    def get_formatted_data(self) -> str:
        """
        获取格式化的数据描述，用于提示词
        
        Returns:
            格式化的数据字符串
        """
        lines = []
        
        # 项目基本信息
        lines.append("# 项目基本信息")
        for key, value in self.项目基本信息.items():
            lines.append(f"- {key}：{value}")
        
        # 法规政策符合性
        lines.append("\n# 法规政策符合性")
        lines.append(f"\n## 产业政策符合性")
        lines.append(f"- 法规名称：{self.产业政策符合性.法规名称}")
        lines.append(f"- 符合性分析：{self.产业政策符合性.符合性分析}")
        lines.append(f"- 结论：{self.产业政策符合性.符合性结论}")
        
        lines.append(f"\n## 供地政策符合性")
        lines.append(f"- 法规名称：{self.供地政策符合性.法规名称}")
        lines.append(f"- 符合性分析：{self.供地政策符合性.符合性分析}")
        lines.append(f"- 结论：{self.供地政策符合性.符合性结论}")
        
        # 三线协调分析
        lines.append("\n# 三线协调分析")
        三线 = self.三线协调分析
        lines.append(f"- 是否占用耕地：{'是' if 三线.是否占用耕地 else '否'}")
        lines.append(f"- 是否占用永久基本农田：{'是' if 三线.是否占用永久基本农田 else '否'}")
        lines.append(f"- 是否占用生态保护红线：{'是' if 三线.是否占用生态保护红线 else '否'}")
        lines.append(f"- 是否位于城镇开发边界内：{'是' if 三线.是否占用城镇开发边界 else '否'}")
        lines.append(f"- 符合性说明：{三线.符合性说明}")
        
        # 国土空间规划符合性
        lines.append("\n# 国土空间总体规划符合性")
        国空 = self.国土空间规划符合性
        lines.append(f"- 一张图落位：{'已上图' if 国空.一张图分析.是否上图 else '未上图'}")
        lines.append(f"- 功能分区准入：{国空.功能分区准入.符合性说明}")
        lines.append(f"- 总体符合性结论：{国空.总体符合性结论}")
        
        # 专项规划符合性
        lines.append("\n# 专项规划符合性")
        专项 = self.专项规划符合性
        lines.append(f"- 综合交通规划：{专项.综合交通规划.符合性结论}")
        lines.append(f"- 市政基础设施规划：{专项.市政基础设施规划.符合性结论}")
        lines.append(f"- 历史文化遗产保护规划：{专项.历史文化遗产保护规划.符合性结论}")
        lines.append(f"- 综合防灾工程规划：{专项.综合防灾工程规划.符合性结论}")
        lines.append(f"- 旅游规划：{专项.旅游规划.符合性结论}")
        
        # 合法合规小结
        lines.append(f"\n# 合法合规性小结")
        lines.append(self.合法合规小结)
        
        return "\n".join(lines)


# ============================================================================
# 示例数据函数
# ============================================================================

def get_sample_data() -> ComplianceData:
    """
    获取示例数据，用于测试和演示
    
    Returns:
        合法合规性分析示例数据
    """
    return ComplianceData(
        项目基本信息={
            "项目名称": "兴山县香溪河流域生态环境综合治理项目（峡口镇白鹤污水处理厂）",
            "建设单位": "湖北兴山经济开发区管理委员会",
            "项目性质": "新建",
            "项目类型": "市政公用类",
            "用地分类": "1302排水用地",
            "建设规模": "日处理能力6000m³/d，占地面积10633.00m²"
        },
        
        产业政策符合性=RegulationCompliance(
            法规名称="《产业结构调整指导目录（2024年本）》",
            发布单位="国家发展和改革委员会",
            发布时间="2024年",
            符合性分析="项目属于第一类鼓励类：四十二、环境保护与资源节约综合利用中的3.城镇污水垃圾处理，符合国家产业政策。",
            符合性结论="符合"
        ),
        
        供地政策符合性=RegulationCompliance(
            法规名称="《划拨用地目录》",
            发布单位="国土资源部",
            发布时间="2001年",
            符合性分析="项目符合城市基础设施用地和公益事业用地（三）城市基础设施用地5.环境卫生设施：包括污水处理厂，符合供地政策。",
            符合性结论="符合"
        ),
        
        其他法规符合性=[
            RegulationCompliance(
                法规名称="《城镇污水处理厂污染物排放标准》（GB18918-2002）",
                发布单位="国家环境保护总局",
                发布时间="2002年",
                符合性分析="出水水质满足一级A标准。",
                符合性结论="符合"
            ),
            RegulationCompliance(
                法规名称="《城市污水处理工程项目建设标准》（JB198-2022）",
                发布单位="住房和城乡建设部",
                发布时间="2022年",
                符合性分析="项目用地规模符合建设标准要求。",
                符合性结论="符合"
            )
        ],
        
        三线协调分析=ThreeLinesAnalysis(
            是否占用耕地=False,
            是否占用永久基本农田=False,
            是否占用生态保护红线=False,
            是否占用城镇开发边界=False,
            符合性说明="项目属于《省自然资源厅关于加强'三区三线'实施管理的意见》规定的单独选址项目用地清单中民生基础设施项目，符合单独选址要求。拟选址项目区不涉及压占耕地、不涉及压占永久基本农田，不涉及压占生态保护红线，不位于城镇开发边界内。符合永久基本农田管控规则，符合生态保护红线管控要求。",
            数据来源="2023年国土变更调查数据"
        ),
        
        国土空间规划符合性=SpatialPlanningCompliance(
            一张图分析=OneMapAnalysis(
                是否上图=True,
                重点项目库名称="生态修复重点工程",
                项目类型="生态修复类项目",
                落位说明="项目选址方案符合兴山县国土空间总体规划，本项目在兴山县国土空间规划'一张图'上，已列入规划生态修复重点工程。"
            ),
            功能分区准入=FunctionalZoneAnalysis(
                城镇建设适宜性="城镇建设适宜区",
                生态保护重要性="不属于生态保护极重要区",
                农业生产适宜性="农业生产不适宜区",
                符合性说明="项目选址方案在城镇适宜性评价结果图中属于城镇建设适宜区，在生态保护重要性评价结果图中不属于生态保护极重要区，于农业生产适宜性评价结果图中属于农业生产不适宜区，完全符合生态重要性等级、农业生产适宜等级和建设开发适宜等级等方面的符合性。"
            ),
            用途管制符合性="项目符合国土空间用途管制相关要求，用地性质为排水用地，符合规划用途。",
            国土空间格局符合性="项目整体符合国土空间总体规划的布局要求，已列入规划生态修复重点工程。",
            总体符合性结论="项目与国土空间总体规划符合性较高。"
        ),
        
        专项规划符合性=SpecialPlanningCompliance(
            综合交通规划=SpecialPlanCompliance(
                规划名称="兴山县国土空间总体规划（2021-2035年）-综合交通规划",
                符合性分析="项目拟选址位于规划'四纵三横两支'的公路骨架网络的'横三'312省道沿线，该项目未占用S312省道沿线，并沿S312省道沿线一侧预留绿化带。",
                符合性结论="符合"
            ),
            市政基础设施规划=SpecialPlanCompliance(
                规划名称="兴山县国土空间总体规划（2021-2035年）-市政基础设施规划",
                符合性分析="项目拟选址与市政基础设施规划中能源供应体系、通讯网络体系、水循环利用与污水治理体系相关规划均不冲突。",
                符合性结论="符合"
            ),
            历史文化遗产保护规划=SpecialPlanCompliance(
                规划名称="兴山县国土空间总体规划（2021-2035年）-历史文化遗产保护规划",
                符合性分析="项目所在区域无压占历史文化名城、名镇、名村保护范围等，均未发现古城镇、古建筑、古村落，文物古迹保护等保护对象。",
                符合性结论="符合"
            ),
            综合防灾工程规划=SpecialPlanCompliance(
                规划名称="兴山县国土空间总体规划（2021-2035年）-综合防灾减灾体系",
                符合性分析="项目所在区域位于一般防治区，主要面临轻度地质灾害和气象灾害风险，不与防灾重点工程冲突。",
                符合性结论="符合"
            ),
            旅游规划=SpecialPlanCompliance(
                规划名称="兴山县国土空间总体规划（2021-2035年）-城镇空间布局结构图",
                符合性分析="项目所在区域位于峡口旅游物流组团片区内部，周边为香溪河绿色山水风景廊道轴线，不与现有旅游规划项目冲突，项目建成有助于维护周边环境。",
                符合性结论="符合"
            ),
            环境保护规划=SpecialPlanCompliance(
                规划名称="宜昌市环境保护总体规划（2013-2030年）",
                符合性分析="项目拟选址位于生态黄线区，主要为小型点状开发的污水处理项目，针对生活污水处理加强了生态治理和修复。",
                符合性结论="符合"
            ),
            自然保护地规划=SpecialPlanCompliance(
                规划名称="湖北三峡万朝山省级自然保护区",
                符合性分析="项目用地不在湖北三峡万朝山省级自然保护区范围内。",
                符合性结论="符合"
            )
        ),
        
        其他规划符合性=OtherPlanningCompliance(
            国民经济和社会发展规划=SpecialPlanCompliance(
                规划名称="《兴山县国民经济和社会发展第十四个五年规划和2035年远景目标纲要》",
                符合性分析="项目可对香溪河左岸峡口片区的生活污水进行系统治理和循环利用，与《规划纲要》中'持续抓好香溪河流域生态保护和修复'要点符合。",
                符合性结论="符合"
            ),
            生态环境保护规划=SpecialPlanCompliance(
                规划名称="《宜昌市环境保护总体规划（2013-2030年）》",
                符合性分析="项目拟选址位于生态黄线区，符合管控要求。",
                符合性结论="符合"
            ),
            三线一单生态环境分区管控=SpecialPlanCompliance(
                规划名称="《宜昌市'三线一单'生态环境分区管控实施方案》",
                符合性分析="项目拟选址位于重点管控单元，编号为ZH42052620003，项目不属于该单元空间布局约束禁止项目，符合管控单元污染物排放和环境风险防控相关要求。",
                符合性结论="符合"
            ),
            综合交通体系规划=SpecialPlanCompliance(
                规划名称="《宜昌市综合交通体系规划（2011-2030年）》",
                符合性分析="项目拟选址位于规划的二级公路S312省道沿线，该项目未占用S312省道沿线，并沿S312省道沿线一侧预留绿化带。",
                符合性结论="符合"
            )
        ),
        
        城乡总体规划符合性=UrbanPlanningCompliance(
            规划名称="《宜昌市兴山县峡口镇总体规划（2014-2030）》",
            规划期限="2014-2030年",
            空间管制分区="适建区",
            符合性分析="项目拟选址位于镇域空间管制分类中适建区，适建区主要为工程地质条件良好、地势相对平坦、没有其它建设限制条件的区域。本项目建设规模、开发强度均较小，符合所在地经批复的城市总体规划布局的要求。",
            符合性结论="符合"
        ),
        
        合法合规小结="综合前述项目与相关法律法规、政策文件的符合性分析、与'三线'和耕地等各类空间的协调分析、与国土空间总体规划的符合性分析、与专项规划的符合性分析以及与其他相关规划的符合性分析，建设项目总体上属于合法合规。",
        
        图表清单=[
            "图3-1 项目范围与'三条控制线'叠加分析图",
            "图3-2 国土空间规划重点项目库清单项目所在页截图",
            "图3-3 项目与生态修复和综合整治规划图整合结果",
            "图3-4 项目与生态保护重要性评价结果图整合结果",
            "图3-5 项目与农业生产适宜性评价结果图整合结果",
            "图3-6 项目与城镇适宜性评价结果图整合结果",
            "图3-7 项目与县域综合交通规划图整合结果",
            "图3-8 项目与城镇空间布局结构图整合结果",
            "图3-9 十四五规划重点项目库清单项目所在页截图",
            "图3-10 宜昌市生态功能红线图",
            "图3-11 宜昌市环境管控单元分布图",
            "图3-12 宜昌市综合交通规划图",
            "图3-13 项目与镇域空间管控图整合结果"
        ],
        
        数据来源="兴山县国土空间总体规划（2021-2035年）、相关部门复函、2023年国土变更调查数据",
        编制日期="2026年2月26日"
    )


if __name__ == "__main__":
    # 测试数据模型
    print("测试合法合规性分析数据模型...")
    
    try:
        data = get_sample_data()
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
        import json
        json_str = data.model_dump_json()
        print(f"✓ JSON序列化成功（{len(json_str)}字符）")
        
    except Exception as e:
        print(f"✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()