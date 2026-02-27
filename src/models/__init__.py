# src/models/__init__.py
"""
数据模型模块

包含所有Agent和系统使用的数据模型定义。
"""

from .site_selection_data import (
    SiteSelectionData,
    SiteAlternative,
    SiteNaturalConditions,
    SiteExternalConditions,
    SiteSensitiveConditions,
    ConstructionConditions,
    PlanningImpact,
    ConsultationOpinion,
    SchemeComparison
)

from .compliance_data import (
    ComplianceData,
    RegulationCompliance,
    ThreeLinesAnalysis,
    OneMapAnalysis,
    FunctionalZoneAnalysis,
    SpatialPlanningCompliance,
    SpecialPlanCompliance,
    SpecialPlanningCompliance,
    OtherPlanningCompliance,
    UrbanPlanningCompliance
)

from .rationality_data import (
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

from .land_use_data import (
    LandUseData,
    FunctionalZone,
    OverallLandIndicator,
    SubAreaIndicator,
    LandScaleAnalysis,
    LandSavingTechnology,
    CaseComparison,
)

from .conclusion_data import (
    ConclusionData,
)

__all__ = [
    # 第2章 选址分析
    'SiteSelectionData',
    'SiteAlternative',
    'SiteNaturalConditions',
    'SiteExternalConditions',
    'SiteSensitiveConditions',
    'ConstructionConditions',
    'PlanningImpact',
    'ConsultationOpinion',
    'SchemeComparison',
    # 第3章 合法合规性分析
    'ComplianceData',
    'RegulationCompliance',
    'ThreeLinesAnalysis',
    'OneMapAnalysis',
    'FunctionalZoneAnalysis',
    'SpatialPlanningCompliance',
    'SpecialPlanCompliance',
    'SpecialPlanningCompliance',
    'OtherPlanningCompliance',
    'UrbanPlanningCompliance',
    # 第4章 选址合理性分析
    'RationalityData',
    'AtmosphericImpact',
    'NoiseImpact',
    'WaterImpact',
    'SolidWasteImpact',
    'TrafficImpact',
    'EcologicalRestoration',
    'EnvironmentalImpactAnalysis',
    'MineralResourceAnalysis',
    'GeologicalHazardAnalysis',
    'LegalityRiskAnalysis',
    'LivingEnvironmentRisk',
    'SocialEnvironmentRisk',
    'SocialStabilityAnalysis',
    'EnergySavingAnalysis',
    # 第5章 节约集约用地分析
    'LandUseData',
    'FunctionalZone',
    'OverallLandIndicator',
    'SubAreaIndicator',
    'LandScaleAnalysis',
    'LandSavingTechnology',
    'CaseComparison',
    # 第6章 结论与建议
    'ConclusionData',
]