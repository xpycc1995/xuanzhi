# MODELS MODULE KNOWLEDGE BASE

## OVERVIEW
数据模型层 - Pydantic BaseModel进行严格数据验证. 所有字段使用中文命名.

## FILES

| 文件 | 行数 | 章节数据 |
|------|------|----------|
| `project_overview_data.py` | ~80 | 第1章: 项目基本信息 |
| `site_selection_data.py` | 558 | 第2章: 选址分析数据 |

## MODEL STRUCTURE

### ProjectOverviewData (简单)
```python
class ProjectOverviewData(BaseModel):
    项目名称: str
    项目代码: Optional[str]
    建设单位: str
    建设性质: str
    项目投资: str
    项目选址: str
    建设内容: str
    建设规模: Optional[str]
    建设期限: Optional[str]
    
    def to_dict(self) -> Dict[str, str]: ...
```

### SiteSelectionData (复杂嵌套)
```python
SiteSelectionData
├── 项目基本信息: Dict[str, str]
├── 选址原则: List[str] (5-10条)
├── 备选方案: List[SiteAlternative] (必须2个)
│   ├── 方案编号, 方案名称, 位置, 面积
│   ├── 四至范围: Dict[str, str] (东南西北)
│   ├── 土地利用现状: Dict[str, str]
│   └── 是否占用耕地/基本农田/未利用地
├── 场地自然条件: SiteNaturalConditions
│   ├── 地形地貌, 气候, 区域地质构造
│   ├── 水文地质条件, 工程地质, 地震
├── 外部配套条件: SiteExternalConditions
├── 选址敏感条件: SiteSensitiveConditions
│   ├── 历史保护, 生态保护, 矿产资源
│   ├── 安全防护, 重要设施
│   ├── 耕地和基本农田, 生态保护红线
├── 施工运营条件: ConstructionConditions
├── 规划影响: PlanningImpact
├── 征求意见情况: List[ConsultationOpinion] (至少3个)
└── 方案比选: SchemeComparison
```

## VALIDATION RULES

### 必须字段校验
```python
@validator('备选方案')
def validate_alternatives(cls, v):
    if len(v) != 2:
        raise ValueError("必须提供2个备选方案")
    return v

@validator('征求意见情况')
def validate_opinions(cls, v):
    if len(v) < 3:
        raise ValueError("至少需要3个部门意见")
    return v

@validator('四至范围')
def validate_four_boundaries(cls, v):
    required = ['东', '南', '西', '北']
    for direction in required:
        if direction not in v:
            raise ValueError(f"四至范围缺少{direction}方向")
    return v
```

### 日期格式校验
```python
@validator('日期')
def validate_date_format(cls, v):
    patterns = [
        r'\d{4}年\d{1,2}月\d{1,2}日',
        r'\d{4}-\d{1,2}-\d{1,2}',
        r'\d{4}/\d{1,2}/\d{1,2}'
    ]
    # 不强制格式, 但支持多种格式
    return v
```

## SAMPLE DATA PATTERN

每个数据模型必须提供 `get_sample_data()` 函数:

```python
def get_sample_data() -> SiteSelectionData:
    """获取示例数据, 用于测试和演示"""
    return SiteSelectionData(
        项目基本信息={...},
        备选方案=[...],
        # ... 完整数据
    )

if __name__ == "__main__":
    data = get_sample_data()
    print(f"✓ 数据模型创建成功")
    print(f"  项目名称: {data.项目基本信息['项目名称']}")
```

## FORMATTED OUTPUT

```python
def get_formatted_data(self) -> str:
    """格式化数据, 用于Agent提示词"""
    lines = []
    lines.append("# 项目基本信息")
    for key, value in self.项目基本信息.items():
        lines.append(f"- {key}：{value}")
    
    lines.append("\n# 备选方案")
    for alt in self.备选方案:
        lines.append(f"\n## {alt.方案名称}")
        lines.append(f"- 位置：{alt.位置}")
        # ...
    
    return "\n".join(lines)
```

## EXTENSION GUIDE

### 添加新数据模型
1. 在 `src/models/` 创建 `xxx_data.py`
2. 定义Pydantic模型, 字段使用中文命名
3. 添加必要的 `@validator` 校验器
4. 实现 `get_formatted_data()` 方法
5. 提供 `get_sample_data()` 测试函数
6. 在 `__init__.py` 中导出

### 中文命名规范
```python
# 正确: 中文命名
项目名称: str = Field(..., description="项目名称")
是否占用耕地: bool = Field(default=False, description="是否占用耕地")

# 错误: 英文命名
project_name: str  # 不要这样
```

### 嵌套模型组织
```python
# 主模型包含子模型
class SiteSelectionData(BaseModel):
    备选方案: List[SiteAlternative]  # 嵌套模型列表
    场地自然条件: SiteNaturalConditions  # 单个嵌套模型
```