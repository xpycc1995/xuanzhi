"""
选址合理性分析数据模型

定义了第4章"建设项目选址合理性分析"所需的所有数据结构。
使用Pydantic进行数据验证，确保数据的完整性和准确性。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# 子模型定义
# ============================================================================

class AtmosphericImpact(BaseModel):
    """
    大气环境影响分析数据模型
    
    分析施工期和运营期对大气环境的影响及防治措施。
    """
    施工期扬尘措施: List[str] = Field(
        default_factory=list,
        description="施工期扬尘防治措施列表"
    )
    施工机械废气措施: List[str] = Field(
        default_factory=list,
        description="施工机械废气防治措施列表"
    )
    运营期废气措施: Optional[List[str]] = Field(
        default_factory=list,
        description="运营期废气防治措施列表"
    )
    影响程度: str = Field(
        default="影响较小",
        description="大气环境影响程度评价"
    )
    防治结论: str = Field(
        ...,
        description="大气环境影响防治结论"
    )


class NoiseImpact(BaseModel):
    """
    噪声环境影响分析数据模型
    
    分析施工期和运营期噪声影响及防治措施。
    """
    施工期噪声措施: List[str] = Field(
        default_factory=list,
        description="施工期噪声防治措施列表"
    )
    运营期噪声措施: Optional[List[str]] = Field(
        default_factory=list,
        description="运营期噪声防治措施列表"
    )
    影响程度: str = Field(
        default="影响较小",
        description="噪声环境影响程度评价"
    )
    防治结论: str = Field(
        ...,
        description="噪声环境影响防治结论"
    )


class WaterImpact(BaseModel):
    """
    水环境影响分析数据模型
    
    分析施工期和运营期对水环境的影响及防治措施。
    """
    施工期废水措施: List[str] = Field(
        default_factory=list,
        description="施工期废水防治措施列表"
    )
    运营期废水措施: List[str] = Field(
        default_factory=list,
        description="运营期废水防治措施列表"
    )
    影响程度: str = Field(
        default="影响较小",
        description="水环境影响程度评价"
    )
    防治结论: str = Field(
        ...,
        description="水环境影响防治结论"
    )


class SolidWasteImpact(BaseModel):
    """
    固体废弃物环境影响分析数据模型
    
    分析施工期和运营期固废影响及处置措施。
    """
    施工期固废措施: List[str] = Field(
        default_factory=list,
        description="施工期固废处置措施列表"
    )
    运营期固废措施: Optional[List[str]] = Field(
        default_factory=list,
        description="运营期固废处置措施列表"
    )
    影响程度: str = Field(
        default="影响较小",
        description="固废环境影响程度评价"
    )
    防治结论: str = Field(
        ...,
        description="固废环境影响防治结论"
    )


class TrafficImpact(BaseModel):
    """
    交通影响分析数据模型
    
    分析施工期和运营期对交通的影响及缓解措施。
    """
    施工期交通影响: str = Field(
        ...,
        description="施工期交通影响描述"
    )
    施工期缓解措施: List[str] = Field(
        default_factory=list,
        description="施工期交通缓解措施列表"
    )
    运营期交通影响: Optional[str] = Field(
        None,
        description="运营期交通影响描述"
    )
    运营期缓解措施: Optional[List[str]] = Field(
        default_factory=list,
        description="运营期交通缓解措施列表"
    )
    防治结论: str = Field(
        ...,
        description="交通影响防治结论"
    )


class EcologicalRestoration(BaseModel):
    """
    生态修复措施数据模型
    
    分析项目对生态环境的影响及修复措施。
    """
    对居民点影响: str = Field(
        ...,
        description="对周边居民点的影响分析"
    )
    居民点防治措施: List[str] = Field(
        default_factory=list,
        description="居民点影响防治措施列表"
    )
    对动物影响: str = Field(
        ...,
        description="对野生动物的影响分析"
    )
    动物防治措施: List[str] = Field(
        default_factory=list,
        description="动物影响防治措施列表"
    )
    对植物影响: str = Field(
        ...,
        description="对植被的影响分析"
    )
    植物防治措施: List[str] = Field(
        default_factory=list,
        description="植物影响防治措施列表"
    )
    水土保持措施: List[str] = Field(
        default_factory=list,
        description="水土保持措施列表"
    )


class EnvironmentalImpactAnalysis(BaseModel):
    """
    环境影响分析数据模型（根模型）
    
    包含大气、噪声、水、固废、交通、生态修复六个方面。
    """
    大气环境影响: AtmosphericImpact = Field(
        ...,
        description="大气环境影响分析"
    )
    噪声环境影响: NoiseImpact = Field(
        ...,
        description="噪声环境影响分析"
    )
    水环境影响: WaterImpact = Field(
        ...,
        description="水环境影响分析"
    )
    固体废弃物影响: SolidWasteImpact = Field(
        ...,
        description="固体废弃物环境影响分析"
    )
    交通影响: TrafficImpact = Field(
        ...,
        description="交通影响分析"
    )
    生态修复: EcologicalRestoration = Field(
        ...,
        description="生态修复措施分析"
    )
    环境影响小结: str = Field(
        ...,
        description="环境影响分析综合小结"
    )


class MineralResourceAnalysis(BaseModel):
    """
    压覆矿产资源情况分析数据模型
    
    分析项目是否压覆已查明矿产资源。
    """
    是否压覆矿产资源: bool = Field(
        default=False,
        description="是否压覆已查明资源储量矿产地"
    )
    是否与采矿权重叠: bool = Field(
        default=False,
        description="是否与采矿权存在交叉重叠"
    )
    是否与探矿权重叠: bool = Field(
        default=False,
        description="是否与探矿权存在交叉重叠"
    )
    是否与地质项目重叠: bool = Field(
        default=False,
        description="是否与地质勘测基金项目重叠"
    )
    复函信息: Optional[str] = Field(
        None,
        description="相关部门复函信息"
    )
    分析结论: str = Field(
        ...,
        description="压覆矿产资源情况分析结论"
    )


class GeologicalHazardAnalysis(BaseModel):
    """
    地质灾害影响分析数据模型
    
    分析项目区域地质灾害危险性。
    """
    地质灾害类型: List[str] = Field(
        default_factory=list,
        description="主要地质灾害类型，如滑坡、崩塌、泥石流等"
    )
    地质灾害易发程度: str = Field(
        default="低易发区",
        description="地质灾害易发程度：高易发区/中易发区/低易发区/不易发区"
    )
    危险性等级: str = Field(
        default="小",
        description="地质灾害危险性等级：大/中/小"
    )
    地震基本烈度: str = Field(
        default="6度",
        description="地震基本烈度"
    )
    地震动峰值加速度: Optional[str] = Field(
        None,
        description="地震动峰值加速度值"
    )
    防治措施: List[str] = Field(
        default_factory=list,
        description="地质灾害防治措施列表"
    )
    分析结论: str = Field(
        ...,
        description="地质灾害影响分析结论"
    )


class LegalityRiskAnalysis(BaseModel):
    """
    合法性风险分析数据模型
    
    分析项目决策和程序的合法性风险。
    """
    风险内容: str = Field(
        ...,
        description="合法性风险具体内容描述"
    )
    风险等级: str = Field(
        default="低",
        description="风险等级：高/中/低"
    )
    防范措施: List[str] = Field(
        default_factory=list,
        description="合法性风险防范措施列表"
    )


class LivingEnvironmentRisk(BaseModel):
    """
    生活环境风险分析数据模型
    
    分析项目建设对周边生活环境的影响风险。
    """
    风险内容: str = Field(
        ...,
        description="生活环境风险具体内容描述"
    )
    风险等级: str = Field(
        default="低",
        description="风险等级：高/中/低"
    )
    防范措施: List[str] = Field(
        default_factory=list,
        description="生活环境风险防范措施列表"
    )


class SocialEnvironmentRisk(BaseModel):
    """
    社会环境风险分析数据模型
    
    分析项目建设对社会环境的影响风险。
    """
    风险内容: str = Field(
        ...,
        description="社会环境风险具体内容描述"
    )
    风险等级: str = Field(
        default="低",
        description="风险等级：高/中/低"
    )
    防范措施: List[str] = Field(
        default_factory=list,
        description="社会环境风险防范措施列表"
    )


class SocialStabilityAnalysis(BaseModel):
    """
    社会稳定影响分析数据模型（根模型）
    
    包含合法性风险、生活环境风险、社会环境风险三个方面。
    """
    合法性风险: LegalityRiskAnalysis = Field(
        ...,
        description="合法性风险分析"
    )
    生活环境风险: LivingEnvironmentRisk = Field(
        ...,
        description="生活环境风险分析"
    )
    社会环境风险: SocialEnvironmentRisk = Field(
        ...,
        description="社会环境风险分析"
    )
    社会稳定小结: str = Field(
        ...,
        description="社会稳定影响分析综合小结"
    )


class EnergySavingAnalysis(BaseModel):
    """
    节能分析数据模型
    
    分析项目采用的节能技术和措施。
    """
    前期工作节地措施: List[str] = Field(
        default_factory=list,
        description="前期工作阶段节地措施列表"
    )
    建设实施节能措施: List[str] = Field(
        default_factory=list,
        description="建设实施阶段节能措施列表"
    )
    施工节能措施: List[str] = Field(
        default_factory=list,
        description="施工期节能措施列表"
    )
    运营节能措施: Optional[List[str]] = Field(
        default_factory=list,
        description="运营期节能措施列表"
    )
    节能结论: str = Field(
        ...,
        description="节能分析结论"
    )


# ============================================================================
# 根模型定义
# ============================================================================

class RationalityData(BaseModel):
    """
    选址合理性分析数据模型（根模型）
    
    包含生成第4章所需的所有数据。
    """
    
    # 基本信息
    项目基本信息: Dict[str, str] = Field(
        ...,
        description="项目基本信息：项目名称、建设单位、项目性质等"
    )
    
    # 4.1 环境影响分析
    环境影响分析: EnvironmentalImpactAnalysis = Field(
        ...,
        description="环境影响分析"
    )
    
    # 4.2 压覆矿产资源情况分析
    矿产资源压覆: MineralResourceAnalysis = Field(
        ...,
        description="压覆矿产资源情况分析"
    )
    
    # 4.3 地质灾害影响分析
    地质灾害分析: GeologicalHazardAnalysis = Field(
        ...,
        description="地质灾害影响分析"
    )
    
    # 4.4 社会稳定影响分析
    社会稳定分析: SocialStabilityAnalysis = Field(
        ...,
        description="社会稳定影响分析"
    )
    
    # 4.5 节能分析
    节能分析: EnergySavingAnalysis = Field(
        ...,
        description="节能分析"
    )
    
    # 4.6 选址合理性分析小结
    合理性结论: str = Field(
        ...,
        description="选址合理性分析综合结论"
    )
    
    # 图表信息
    图表清单: Optional[List[str]] = Field(
        None,
        description="需要插入的图表清单"
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
        
        # 项目基本信息
        lines.append("# 项目基本信息")
        for key, value in self.项目基本信息.items():
            lines.append(f"- {key}：{value}")
        
        # 环境影响分析
        env = self.环境影响分析
        lines.append("\n# 环境影响分析")
        
        lines.append("\n## 大气环境影响")
        lines.append(f"- 影响程度：{env.大气环境影响.影响程度}")
        lines.append(f"- 防治结论：{env.大气环境影响.防治结论}")
        
        lines.append("\n## 噪声环境影响")
        lines.append(f"- 影响程度：{env.噪声环境影响.影响程度}")
        lines.append(f"- 防治结论：{env.噪声环境影响.防治结论}")
        
        lines.append("\n## 水环境影响")
        lines.append(f"- 影响程度：{env.水环境影响.影响程度}")
        lines.append(f"- 防治结论：{env.水环境影响.防治结论}")
        
        lines.append("\n## 固体废弃物影响")
        lines.append(f"- 影响程度：{env.固体废弃物影响.影响程度}")
        lines.append(f"- 防治结论：{env.固体废弃物影响.防治结论}")
        
        lines.append("\n## 交通影响")
        lines.append(f"- 防治结论：{env.交通影响.防治结论}")
        
        lines.append("\n## 生态修复")
        lines.append(f"- 对居民点影响：{env.生态修复.对居民点影响}")
        lines.append(f"- 对动物影响：{env.生态修复.对动物影响}")
        lines.append(f"- 对植物影响：{env.生态修复.对植物影响}")
        
        lines.append(f"\n- 环境影响小结：{env.环境影响小结}")
        
        # 压覆矿产资源
        mineral = self.矿产资源压覆
        lines.append("\n# 压覆矿产资源情况")
        lines.append(f"- 是否压覆矿产资源：{'是' if mineral.是否压覆矿产资源 else '否'}")
        lines.append(f"- 是否与采矿权重叠：{'是' if mineral.是否与采矿权重叠 else '否'}")
        lines.append(f"- 是否与探矿权重叠：{'是' if mineral.是否与探矿权重叠 else '否'}")
        lines.append(f"- 分析结论：{mineral.分析结论}")
        
        # 地质灾害分析
        geo = self.地质灾害分析
        lines.append("\n# 地质灾害影响分析")
        lines.append(f"- 地质灾害类型：{', '.join(geo.地质灾害类型) if geo.地质灾害类型 else '无'}")
        lines.append(f"- 易发程度：{geo.地质灾害易发程度}")
        lines.append(f"- 危险性等级：{geo.危险性等级}")
        lines.append(f"- 地震基本烈度：{geo.地震基本烈度}")
        lines.append(f"- 分析结论：{geo.分析结论}")
        
        # 社会稳定分析
        social = self.社会稳定分析
        lines.append("\n# 社会稳定影响分析")
        lines.append(f"- 合法性风险等级：{social.合法性风险.风险等级}")
        lines.append(f"- 生活环境风险等级：{social.生活环境风险.风险等级}")
        lines.append(f"- 社会环境风险等级：{social.社会环境风险.风险等级}")
        lines.append(f"- 社会稳定小结：{social.社会稳定小结}")
        
        # 节能分析
        energy = self.节能分析
        lines.append("\n# 节能分析")
        lines.append(f"- 节能结论：{energy.节能结论}")
        
        # 合理性结论
        lines.append("\n# 选址合理性分析小结")
        lines.append(self.合理性结论)
        
        return "\n".join(lines)


# ============================================================================
# 示例数据函数
# ============================================================================

def get_sample_data() -> RationalityData:
    """
    获取示例数据，用于测试和演示
    
    Returns:
        选址合理性分析示例数据
    """
    return RationalityData(
        项目基本信息={
            "项目名称": "兴山县香溪河流域生态环境综合治理项目（峡口镇白鹤污水处理厂）",
            "建设单位": "湖北兴山经济开发区管理委员会",
            "项目性质": "新建",
            "项目类型": "市政公用类",
            "建设规模": "日处理能力6000m³/d，占地面积10633.00m²"
        },
        
        环境影响分析=EnvironmentalImpactAnalysis(
            大气环境影响=AtmosphericImpact(
                施工期扬尘措施=[
                    "施工场地定期洒水，防止产生大量扬尘",
                    "避免在春季大风季节以及夏季暴雨时节施工",
                    "加强施工区的规划管理，建筑材料堆场采取防尘措施",
                    "弃土、弃料及时清运，超过一周的采取覆盖防尘布措施",
                    "运输车辆采用密闭车斗或苫布遮盖",
                    "出入工地车辆进行清洗",
                    "运输车辆经过居民点时减速慢行"
                ],
                施工机械废气措施=[
                    "运输车辆严禁超载运输",
                    "加强对施工机械、车辆的维修保养",
                    "禁止以柴油为燃料的施工机械超负荷工作"
                ],
                运营期废气措施=[
                    "厨房安装油烟净化处理装置，引至中控楼顶高空排放"
                ],
                影响程度="影响较小",
                防治结论="采取上述措施后，大气环境影响可控，满足《环境空气质量标准》要求"
            ),
            
            噪声环境影响=NoiseImpact(
                施工期噪声措施=[
                    "将低噪声、低振动施工设备作为中标的重要内容",
                    "设专人对施工设备进行定期保养和维护",
                    "施工尽量安排在白天进行，尽量缩短工期",
                    "严格施工现场管理，降低人为噪声",
                    "基坑开挖严禁大爆破",
                    "运输车辆经过环境敏感点时减速行驶，禁止使用音喇叭"
                ],
                影响程度="影响较小",
                防治结论="施工区域距离声环境敏感目标较远，采取上述措施后可满足《建筑施工场界噪声限值》要求"
            ),
            
            水环境影响=WaterImpact(
                施工期废水措施=[
                    "施工生产废水集中收集处理",
                    "在场区内设置化粪池进行处理"
                ],
                运营期废水措施=[
                    "生活污水经化粪池处理后，基本接近《农田灌溉水质标准》"
                ],
                影响程度="影响较小",
                防治结论="项目建设对水环境影响较小，污水处理后达标排放"
            ),
            
            固体废弃物影响=SolidWasteImpact(
                施工期固废措施=[
                    "开挖土方时洒水降尘，注意土方临时堆放",
                    "剩余弃渣可作为场区附近低洼地段的填土",
                    "建筑垃圾和开挖块石弃渣运至指定垃圾填埋点",
                    "生活垃圾集中收集清运至指定垃圾填埋点"
                ],
                影响程度="影响较小",
                防治结论="固体废弃物得到妥善处置，对环境影响较小"
            ),
            
            交通影响=TrafficImpact(
                施工期交通影响="工程建设时由于车辆运输可能导致交通暂时繁忙",
                施工期缓解措施=[
                    "运输车辆宜避开交通高峰期",
                    "合理安排施工机械流程",
                    "避免机械做无用功造成资源浪费"
                ],
                防治结论="交通影响是暂时的，随着工程结束而消失"
            ),
            
            生态修复=EcologicalRestoration(
                对居民点影响="项目地处区域距离居民点较远，对周边居民产生的影响甚微",
                居民点防治措施=[
                    "开挖及回填土石方过程中洒水保持湿度",
                    "临时堆土场定时洒水降尘，设置遮盖措施",
                    "施工结束时及时恢复地面道路及植被",
                    "运输车辆采取洒水和篷布遮盖措施",
                    "调整设备运输时间，运输车辆经居民点时降低车速减少鸣笛"
                ],
                对动物影响="项目施工期的基础建设、运输和设备安装对野生动物种群影响范围很小，施工结束后野生动物种群可逐渐迁回",
                动物防治措施=[
                    "项目区域不在候鸟迁徙通道上",
                    "照明采取遮光措施，避免对鸟类形成误导"
                ],
                对植物影响="永久占地原有生物量较小，场址范围内没有珍稀植物，建设对当地植物总体影响不大",
                植物防治措施=[
                    "泵站周边尽量绿化",
                    "道路边种植树木",
                    "构筑物间的空地种植草皮四季花卉"
                ],
                水土保持措施=[
                    "道路施工防治区设置边坡防护、截排水等工程防护措施",
                    "临时施工场地施工前清理表土，施工期间临时防护",
                    "工程竣工终止使用后拆除覆盖物并进行土地平整，覆土恢复植被"
                ]
            ),
            
            环境影响小结="项目区地质稳定，发生灾害可能性较小，自然条件良好，未压覆现有已探明矿产，对项目区周边环境影响较小"
        ),
        
        矿产资源压覆=MineralResourceAnalysis(
            是否压覆矿产资源=False,
            是否与采矿权重叠=False,
            是否与探矿权重叠=False,
            是否与地质项目重叠=False,
            复函信息="兴山县自然资源和城乡建设局发布《关于项目用地是否压覆已查明矿产资源的复函》，确定项目用地范围及外扩300m不与采矿权、探矿权存在交叉重叠",
            分析结论="项目不存在压覆矿产资源的情况"
        ),
        
        地质灾害分析=GeologicalHazardAnalysis(
            地质灾害类型=[],
            地质灾害易发程度="高易发区",
            危险性等级="小",
            地震基本烈度="6度",
            地震动峰值加速度="0.05g",
            防治措施=[
                "工程施工前委托有资质的单位进行详细岩土工程勘察",
                "查明土体的工程地质性质和分布特征",
                "基坑开挖时避免大方量的切坡开挖",
                "合理选择基础持力层",
                "修建好地表排水沟"
            ],
            分析结论="现状条件下，拟建场地无滑坡、崩塌、泥石流等不良地质灾害，地质灾害发育程度弱、危害程度小、危险性小"
        ),
        
        社会稳定分析=SocialStabilityAnalysis(
            合法性风险=LegalityRiskAnalysis(
                风险内容="项目的决策是否与现行政策、法律、法规相抵触，是否有充分的政策、法律依据",
                风险等级="低",
                防范措施=[
                    "项目经过严格的审查审批和报批程序",
                    "经过严谨科学的可行性研究论证",
                    "建设方案具体、详实，配套措施完善"
                ]
            ),
            生活环境风险=LivingEnvironmentRisk(
                风险内容="施工期间的扬尘、噪音、建筑垃圾等对周边环境的影响",
                风险等级="低",
                防范措施=[
                    "施工单位做好洒水降尘措施",
                    "合理安排施工时段，避免中午、夜间休息时间作业",
                    "建筑垃圾清理合理、有序、彻底",
                    "污水处理厂厂址远离居民区"
                ]
            ),
            社会环境风险=SocialEnvironmentRisk(
                风险内容="项目建设和运营可能引发的社会稳定问题",
                风险等级="低",
                防范措施=[
                    "充分发挥群众来访投诉接待中心功能",
                    "重视投诉公开电话、网上信访等群众意见反映渠道",
                    "加强对项目的正面宣传",
                    "强化利益相关者的参与",
                    "建立信访稳控工作方案"
                ]
            ),
            社会稳定小结="本项目社会稳定整体综合风险为低等级，但仍应做好相关的风险防范措施"
        ),
        
        节能分析=EnergySavingAnalysis(
            前期工作节地措施=[
                "把好选线关，尽可能减少占用土地",
                "注重项目方案比选工作，优先选择节约土地的方案",
                "细化、优化、深化设计方案比选"
            ],
            建设实施节能措施=[
                "合理安排施工机械流程，实现效率最大化",
                "定期维护检查机械设备，充分发挥机械的生产效率",
                "使用节能环保材料"
            ],
            施工节能措施=[
                "管道合理设计管径，减小排水阻力",
                "照明光源选用节能、高效的灯具"
            ],
            运营节能措施=[
                "选用新型工艺进行污水处理，有效减少用电消耗和资源消耗"
            ],
            节能结论="项目建设过程中积极运用四新技术，采用先进节能技术，有助于节省能源和资源消耗"
        ),
        
        合理性结论="综上所述，项目区地质稳定，发生灾害可能性较小，自然条件良好，未压覆现有已探明矿产，对项目区周边环境影响较小，社会稳定性较高，有利于项目的快速开展，同时采用节能技术及方案，有助于节省能源和资源消耗，所以选址是可行的和合理的。",
        
        图表清单=[
            "表4-1 环境影响分析表",
            "表4-2 地质灾害危险性评估表"
        ],
        
        数据来源="地质灾害危险性评估报告、环境影响评价报告、社会稳定风险评估报告",
        编制日期="2026年2月26日"
    )


if __name__ == "__main__":
    # 测试数据模型
    print("测试选址合理性分析数据模型...")
    
    try:
        data = get_sample_data()
        print(f"✓ 数据模型创建成功")
        print(f"  项目名称：{data.项目基本信息['项目名称']}")
        print(f"  是否压覆矿产：{data.矿产资源压覆.是否压覆矿产资源}")
        print(f"  地质灾害易发程度：{data.地质灾害分析.地质灾害易发程度}")
        print(f"  社会稳定风险等级：{data.社会稳定分析.合法性风险.风险等级}")
        
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